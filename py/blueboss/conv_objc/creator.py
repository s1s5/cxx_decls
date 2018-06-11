# coding: utf-8
import sys
import os
import json
import traceback

from blueboss import common as bc
from blueboss import writer as bw

import objc_class

import plugin
import function_plugin
import builtin_plugin
# import builtin_reference_plugin
import builtin_pointer_plugin
import class_plugin
import enum_plugin
import string_plugin
import typedef_plugin
import builtin_vector_plugin
import class_vector_plugin
import unsupported_plugin
import string_vector_plugin


class Creator(plugin.Plugin):

    def __init__(self):
        super(Creator, self).__init__(None, None, None)
        self.settings = {
            'base_class_name': 'bb_BaseClass',
            'global_class': 'bb_Global',
            'global_prefix': 'bb_',
            'lightweight_generics': True,
        }
        self.plugin_types = []
        self.addPlugin(unsupported_plugin.UnsupportedPlugin)
        self.addPlugin(function_plugin.FunctionPlugin)
        self.addPlugin(builtin_plugin.BuiltinPlugin)
        # self.addPlugin(builtin_reference_plugin.BuiltinReferencePlugin)
        self.addPlugin(builtin_pointer_plugin.BuiltinPointerPlugin)
        self.addPlugin(class_plugin.ClassPlugin)
        self.addPlugin(enum_plugin.EnumPlugin)
        self.addPlugin(string_plugin.StringPlugin)
        self.addPlugin(typedef_plugin.TypedefPlugin)
        self.addPlugin(class_vector_plugin.ClassVectorPlugin)
        self.addPlugin(builtin_vector_plugin.BuiltinVectorPlugin)
        self.addPlugin(string_vector_plugin.StringVectorPlugin)

    def set(self, js):
        for i in js.diagnostics:
            if (i.level == 'fatal' or i.level == 'error'):
                raise Exception(i.message)
        self.d = js
        self.target_info = self.d.target_info

    def addPlugin(self, p):
        if not issubclass(p, plugin.Plugin):
            raise TypeError()
        p.creator = self
        self.plugin_types.append(p)

    def __selectPlugin(self, name, fi, *args):
        if (name, args) in self.converters:
            return self.converters[(name, args)]
        map(lambda x: x.hook(args[0]), self.plugins)
        for p in self.plugins:
            try:
                if fi and not getattr(p, fi)(*args):
                    continue
                i = getattr(p, name)(*args)
                if i:
                    self.converters[(name, args)] = i
                    return i
            except Exception, e:
                raise
                print "-=" * 40
                print "Exception: function='%s'" % name
                for arg in args:
                    print "-" * 30
                    print type(arg), arg
                traceback.print_exc(e)
                print
                continue
        print "-=" * 40
        print "Exception: function='%s'" % name
        for arg in args:
            type_ = None
            if isinstance(arg, bc.Type):
                type_ = arg.cname()
            print type(arg), arg, type_
        raise Exception()

    def resolveClass(self, decl_or_type):
        return self.__selectPlugin("resolveClass", "resolveFilter",
                                   decl_or_type)

    def getFunctionConverter(self, func_decl):
        return self.__selectPlugin("getFunctionConverter", "converterFilter",
                                   func_decl)

    def getArgConverter(self, arg_decl, func_conv):
        return self.__selectPlugin("getArgConverter", "converterFilter",
                                   arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return self.__selectPlugin("getReturnConverter", "converterFilter",
                                   ret_type, func_conv)

    def getPlugin(self, typeobj):
        for i in self.plugins:
            if type(i) is typeobj:
                return i
        return None

    def getClass(self, decl_or_type, klass=None):
        if (isinstance(decl_or_type, str) or
                isinstance(decl_or_type, unicode)):
            name = decl_or_type
        else:
            klass, name = self.resolveClass(decl_or_type)
        if name in self.class_map:
            if type(self.class_map[name]) is not klass:
                raise Exception()
        else:
            self.class_map[name] = klass(self, name)
        return self.class_map[name]

    def getBaseClass(self):
        name = self.settings['base_class_name']
        if name not in self.class_map:
            self.class_map[name] = objc_class.BaseObjCClass(self.creator, name)
        return self.class_map[name]

    def declare(self, decl):
        return self.__selectPlugin("declare", False, decl)
        # try:
        #     return self.__selectPlugin("declare", False, decl)
        # except Exception, e:
        #     print "unhandled decl", decl
        #     traceback.print_exc(e)

    def linkStart(self):
        self.plugins = []
        typeset = set()
        remain = []
        for ty in reversed(self.plugin_types):
            if ty in typeset:
                continue
            p = ty(self, self.settings, self.d.target_info)
            self.plugins.append(p)
            typeset.add(ty)
            remain.append(p)
        while remain:
            x = remain.pop(0)
            for ty in x.depends():
                if ty in typeset:
                    continue
                p = ty(self, self.settings, self.d.target_info)
                self.plugins.append(p)
                typeset.add(ty)
                remain.append(p)

        self.converters = {}
        self.class_map = {}
        for i in reversed(self.plugins):
            i.linkStart()

    def link(self):
        self.linkStart()
        map(self.declare, self.d.declarations)
        self.linkEnd()

    def linkEnd(self):
        for v in self.class_map.itervalues():
            v.link()
        for i in reversed(self.plugins):
            i.linkEnd()

    def output(self, header_filename, source_filename, verbose=False):
        header = bw.objc.StatementList()
        source = bw.objc.StatementList()
        # source_private = bw.objc.StatementList()
        source_header = bw.objc.StatementList()
        source_private = bw.cxx.Namespace()

        header << '#import <Foundation/NSObject.h>'
        header << '#import <Foundation/Foundation.h>'
        header << '#pragma clang diagnostic push'
        header << ('#pragma clang diagnostic ignored '
                   '"-Wproperty-attribute-mismatch"')
        header << ('#pragma clang diagnostic ignored '
                   '"-Wobjc-property-synthesis"')
        header_internal = bw.objc.StatementList()
        header << header_internal
        header << '#pragma clang diagnostic pop'

        source << '#import "%s"' % (
            os.path.relpath(header_filename, os.path.dirname(source_filename)))

        for i in sorted(self.d.includes):
            source << '#include "%s"' % i

        source << source_header
        source << source_private

        def ha(x):
            return header_internal << x if x else header_internal

        def sha(x):
            return source_header << x if x else source_header

        def spa(x):
            return source_private << x if x else source_private

        def sa(x):
            return source << x if x else source

        for i in sorted(self.class_map):
            header_internal << bw.objc.ClassDecl(
                i, self.class_map[i].isProtocol())

        for i in reversed(self.plugins):
            ha(i.objcHeader())
            sha(i.objcSourceHeader())
            spa(i.objcSourcePrivate())
            sa(i.objcSourcePublic())

        for i in sorted(
                self.class_map.itervalues(),
                key=lambda x: (x.priority, x.name)):
            if not i.isValid():
                continue
            ha(i.objcHeader())
            sha(i.objcSourceHeader())
            spa(i.objcSourcePrivate())
            sa(i.objcSourcePublic())

        with open(header_filename, 'w') as fp:
            header.dump(fp)
        with open(source_filename, 'w') as fp:
            source.dump(fp)

        if verbose:
            header.dump(sys.stdout)
            source.dump(sys.stdout)


def main(args, options):
    ds = map(lambda x: json.loads(open(x).read()), args)
    d = bc.mergeJson(*ds)
    o = bc.loadJson(d)
    c = Creator()
    c.settings['lightweight_generics'] = options.lightweight_generics
    c.set(o)
    c.link()
    c.output(options.dst_header, options.dst_source, verbose=options.verbose)


def entry_point():
    import argparse
    parser = argparse.ArgumentParser(
        description=u'',  # プログラムの説明
    )
    parser.add_argument("args", nargs="+")
    parser.add_argument(
        "--dst-header", default="objcif.h", type=str, dest="dst_header")
    parser.add_argument(
        "--dst-source", default="objcif.mm", type=str, dest="dst_source")
    parser.add_argument("-v",
                        "--verbose",
                        default=False,
                        action='store_true',
                        dest="verbose")
    parser.add_argument("--never-use-lightweight-generics",
                        default=True,
                        action='store_false',
                        dest="lightweight_generics")
    o = parser.parse_args()
    main(o.args, o)


if __name__ == '__main__':
    entry_point()
