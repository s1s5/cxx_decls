# coding: utf-8
import sys
import os
import json
import jpath
import traceback

from blueboss import common as bc
from blueboss import writer as bw
from blueboss import tool as bb_tool

import jclass
import plugin
import builtin_plugin
import builtin_reference_plugin
import function_plugin
import class_plugin
import class_pointer_plugin
import builtin_pointer_plugin
import enum_plugin
import typedef_plugin
import string_plugin
import builtin_vector_plugin
import class_vector_plugin
import template_plugin
import builtin_constant_array_plugin
import class_constant_array_plugin
import function_type_plugin
import general_constant_array_plugin
import pointer_plugin
# import reference_plugin
import memory_plugin
import dummy_plugin
import string_ref_plugin
import string_vector_plugin


class Creator(plugin.Plugin):
    def __init__(self):
        super(Creator, self).__init__(None, None, None)
        self.settings = {'default_package': ('com', 'example'), }
        self.plugin_types = []
        self.addPlugin(dummy_plugin.DummyPlugin)
        self.addPlugin(memory_plugin.MemoryPlugin)
        # self.addPlugin(reference_plugin.ReferencePlugin)
        self.addPlugin(pointer_plugin.PointerPlugin)
        self.addPlugin(builtin_plugin.BuiltinPlugin)
        self.addPlugin(function_plugin.FunctionPlugin)
        self.addPlugin(class_plugin.ClassPlugin)
        self.addPlugin(builtin_reference_plugin.BuiltinReferencePlugin)
        self.addPlugin(class_pointer_plugin.ClassPointerPlugin)
        self.addPlugin(builtin_pointer_plugin.BuiltinPointerPlugin)
        self.addPlugin(enum_plugin.EnumPlugin)
        self.addPlugin(typedef_plugin.TypedefPlugin)
        self.addPlugin(string_plugin.StringPlugin)
        self.addPlugin(builtin_vector_plugin.BuiltinVectorPlugin)
        self.addPlugin(class_vector_plugin.ClassVectorPlugin)
        self.addPlugin(template_plugin.TemplatePlugin)
        self.addPlugin(general_constant_array_plugin.Plugin)
        self.addPlugin(class_constant_array_plugin.ClassConstantArrayPlugin)
        self.addPlugin(
            builtin_constant_array_plugin.BuiltinConstantArrayPlugin)
        self.addPlugin(function_type_plugin.FunctionTypePlugin)
        self.addPlugin(string_ref_plugin.StringRefPlugin)
        self.addPlugin(string_vector_plugin.StringVectorPlugin)

    def set(self, js):
        for i in js.diagnostics:
            if (i.level == 'fatal' or i.level == 'error'):
                i.show()
                raise Exception(i.message)
        self.d = js
        self.target_info = self.d.target_info

    def addPlugin(self, p):
        if not issubclass(p, plugin.Plugin):
            raise TypeError()
        self.plugin_types.append(p)

    def linkStart(self):
        self.converters = {}
        for i in reversed(self.plugins):
            i.linkStart()

    def __selectPlugin(self, name, fi, *args):
        if (name, args) in self.converters:
            return self.converters[(name, args)]
        map(lambda x: x.hook(args[0]), self.plugins)
        for p in self.plugins:
            try:
                # print p, name, fi and not getattr(p, fi)(*args)
                if fi and not getattr(p, fi)(*args):
                    continue
                i = getattr(p, name)(*args)
                if i:
                    self.converters[(name, args)] = i
                    return i
            except:
                raise
            # except Exception, e:
            #     raise
                # print "-=" * 40
                # print "Exception: function='%s'" % name
                # for arg in args:
                #     print "-" * 30
                #     print type(arg), arg
                # traceback.print_exc(e)
                # print
                # continue
        print "-=" * 40
        print "Exception: function='%s'" % name
        for arg in args:
            type_ = None
            if isinstance(arg, bc.Type):
                type_ = arg.cname()
            print type(arg), arg, type_
        raise Exception()

    def resolveInterfacePath(self, decl_or_type):
        return self.__selectPlugin("resolveInterfacePath", "resolveFilter",
                                   decl_or_type)

    def resolveClassPath(self, decl_or_type):
        return self.__selectPlugin("resolveClassPath", "resolveFilter",
                                   decl_or_type)

    def resolveFunctionClassPath(self, decl_or_type):
        return self.__selectPlugin("resolveFunctionClassPath", "resolveFilter",
                                   decl_or_type)

    def getFunctionConverter(self, func_decl, decl_class=None):
        return self.__selectPlugin("getFunctionConverter", "converterFilter",
                                   func_decl, decl_class)

    def getArgConverter(self, arg_decl, func_conv):
        return self.__selectPlugin("getArgConverter", "converterFilter",
                                   arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return self.__selectPlugin("getReturnConverter", "converterFilter",
                                   ret_type, func_conv)

    def declare(self, decl):
        try:
            return self.__selectPlugin("declare", False, decl)
        except Exception, e:
            print "unhandled decl", decl
            traceback.print_exc(e)

    def __getJavaClass(self, func, decl_or_type):
        ret = func(decl_or_type)
        if ret is None:
            return
        klass, jpath = ret
        return self.setNamespace(klass, jpath)

    def getInterface(self, decl_or_type):
        if isinstance(decl_or_type, jpath.JPath):
            return self.namespaces[decl_or_type]
        return self.__getJavaClass(self.resolveInterfacePath, decl_or_type)

    def getClass(self, decl_or_type):
        if isinstance(decl_or_type, jpath.JPath):
            return self.namespaces[decl_or_type]
        return self.__getJavaClass(self.resolveClassPath, decl_or_type)

    def setNamespace(self, klass, jpath):
        if jpath not in self.namespaces:
            self.namespaces[jpath] = klass(self, jpath)
        elif not isinstance(self.namespaces[jpath], klass):
            print jpath, self.namespaces[jpath], klass
            raise Exception()
        # print jpath, klass
        return self.namespaces[jpath]

    def getFunctionClass(self, decl_or_type):
        return self.__getJavaClass(self.resolveFunctionClassPath, decl_or_type)

    def getDeclarations(self):
        return self.d.declarations

    def getPlugin(self, klass):
        for i in self.plugins:
            if isinstance(i, klass):
                return i
        return None

    def linkEnd(self):
        for i in reversed(self.plugins):
            i.linkEnd()

        cmap = {}
        for key, value in self.namespaces.items():
            # if not value.isValid():
            #     continue
            fn = key.path
            for i in xrange(len(fn)):
                k = fn[:i]
                v = cmap.get(k, None)
                cmap[k] = v
            cmap[fn] = key
            # print ">>>", key
        for key in cmap:
            if cmap[key]:
                v = self.namespaces[cmap[key]]
                if not v.isValid():
                    continue
                for k in cmap:
                    a = '.'.join(key)
                    b = '.'.join(k)
                    if b.startswith(a) and cmap[k] is None:
                        cmap[k] = True

        # print cmap

        for key in cmap:
            if cmap[key] is None:
                continue
            ppath = ()
            cpath = key
            for i in xrange(len(key), 0, -1):
                if not cmap[key[:i]]:
                    ppath = key[:i]
                    cpath = key[i:]
                    break
            # print key, ppath, cpath
            if cmap[key] is True:
                value = jpath(key)
                cmap[key] = value
                self.namespaces[value] = jclass.Class(self, value)
            cmap[key].set(ppath, cpath)
            self.namespaces[cmap[key]].jpt.set(ppath, cpath)

        # print cmap

        tree = {}
        for key, value in self.namespaces.items():
            if not value.isValid():
                continue
            fn = self.settings[
                'default_package'] + key.package_path, key.class_path[0]
            a = tree.get(fn, (None, dict()))
            if len(key.class_path) == 1:
                a = (value, a[1])
                # print key, value, "a=", a
            else:
                l = list(key.class_path[1:])
                b = a[1]
                while l:
                    k = l.pop(0)
                    c = b.get(k, (None, dict()))
                    if len(l) == 0:
                        c = (value, c[1])
                    b[k] = c
                    b = c[1]
            # print ">>", key, value, 'a=', a[0]
            tree[fn] = a
        # print tree
        # print tree.values()
        for v in self.namespaces.values():
            v.link(self.settings['default_package'])
        self.tree = tree
        map(lambda x: x[0].setTopLevel(True), self.tree.values())

    def link(self):
        self.namespaces = {}
        key = self.getBaseClassKey()
        self.namespaces[key] = jclass.BaseClass(self, key)
        key = self.getBaseInterfaceKey()
        self.namespaces[key] = jclass.BaseInterface(self, key)

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

        self.linkStart()
        map(lambda x: map(lambda y: y.walkUsr(x), self.plugins),
            self.d.usr_map.values())
        map(lambda x: x.walkUsrEnd(), self.plugins)
        map(self.declare, self.d.declarations)
        self.linkEnd()

    def outputJavaSource(self, base_dir, libname, verbose=False):
        javas = map(lambda x: (bw.java.StatementList(), x[0], x[1]),
                    self.tree.items())
        sources = map(lambda x: (x[1], x[0]), javas)
        import_dict = {}
        for (directory, filename), source in sources:
            package = '.'.join(directory)
            if package:
                source << 'package %s;' % package
            imports = bw.java.StatementList()
            source << imports
            import_dict[(directory, filename)] = (imports, set(), set())

        while javas:
            dst, key, (val, di) = javas.pop(0)
            # print dst, key, val, di
            s = val.javaSource()
            if val == self.getBaseClass():
                s << "public static boolean __flag = false;"
                func = bw.java.Func("static void", "__loadLibrary", [])
                func << (bw.java.If("!__flag") << 'System.loadLibrary("%s");' %
                         libname << "__flag = true;")
                s << func
            elif isinstance(val, jclass.Class):
                jpt = self.getBaseClass().jpt.getClassPath()
                s << "static { %s.__loadLibrary(); }" % jpt
            javas = map(lambda x: (s, key, x[1]), di.items()) + javas
            dst << s
            import_dict[key][1].update(map(lambda x: x.getImportPath(),
                                           val.imports()))
            import_dict[key][2].update(map(lambda x: x.getImportPath(),
                                           val.importsSys()))

        for i in import_dict.values():
            for j in i[2]:
                i[0] << 'import %s;' % j
            for j in i[1]:
                # i[0] << 'import %s;' % (
                #     '.'.join(self.settings['default_package']) + '.' + j)
                i[0] << 'import %s;' % j

        for (directory, filename), source in sources:
            d = os.path.join(*((base_dir, ) + directory))
            bb_tool.mkdir_p(d)
            filename = os.path.join(d, filename + '.java')
            with open(filename, "wb") as fp:
                source.dump(fp)
            if verbose:
                print '=' * 120
                print filename
                print '-' * 60
                source.dump(sys.stdout)

    def outputJni(self, jni_filename, verbose=False):
        jni_header = bw.cxx.StatementList()
        jni_source = bw.cxx.StatementList()

        def ha(x):
            return jni_header << x if x else jni_header

        def sa(x):
            return jni_source << x if x else jni_source

        jni_header << '#include <jni.h>'
        for i in self.d.includes:
            jni_header << '#include "%s"' % i

        l = []
        for i in reversed(self.plugins):
            for j in i.includes():
                if j not in l:
                    l.append(j)
        for i in l:
            jni_header << '#include "%s"' % i

        l = []
        for i in reversed(self.plugins):
            for j in i.includesSys():
                if j not in l:
                    l.append(j)
        for i in l:
            jni_header << '#include <%s>' % i

        ha("namespace {")
        for i in reversed(self.plugins):
            ha(i.jniHeader())
            sa(i.jniSource())
        ha("}  // namespace")

        jni_header << '#ifdef __cplusplus'
        jni_header << 'extern "C" {'
        jni_header << '#endif  // __cplusplus'
        for key, value in self.namespaces.items():
            ha(value.jniHeader())
            sa(value.jniSource())

        jni_header << '#ifdef __cplusplus'
        jni_header << '}  // extern "C"'
        jni_header << '#endif  // __cplusplus'

        dirname = os.path.dirname(jni_filename)
        if dirname and dirname != "." and dirname != "..":
            bb_tool.mkdir_p(dirname)
        with open(jni_filename, "wb") as fp:
            jni_header.dump(fp)
            jni_source.dump(fp)

        if verbose:
            jni_header.dump(sys.stdout)
            jni_source.dump(sys.stdout)

    def getBaseInterfaceKey(self):
        return jpath.JPath(('BBInterface', ))

    def getBaseInterface(self):
        key = self.getBaseInterfaceKey()
        return self.namespaces[key]

    def getBaseClassKey(self):
        return jpath.JPath(('BBObject', ))

    def getBaseClass(self):
        key = self.getBaseClassKey()
        return self.namespaces[key]


def main(args, options):
    ds = map(lambda x: json.loads(open(x).read()), args)
    d = bc.mergeJson(*ds)
    o = bc.loadJson(d)
    c = Creator()
    c.settings['default_package'] = tuple(
        options.default_package.split('.'))
    c.set(o)
    c.link()
    c.outputJavaSource(options.base_dir,
                       options.libname,
                       verbose=options.verbose)
    c.outputJni(options.jni_filename, verbose=options.verbose)


def entry_point():
    import argparse
    parser = argparse.ArgumentParser(
        description=u'',  # プログラムの説明
    )
    parser.add_argument("args", nargs="+", help="extracted cxx decls, json format")
    parser.add_argument("--dst-dir", default="java", type=str, dest="base_dir")
    parser.add_argument("--jni-filename",
                        default="jniex.cpp",
                        type=str,
                        dest="jni_filename")
    parser.add_argument("--libname",
                        default="nativelib",
                        type=str,
                        dest="libname")
    parser.add_argument("-v",
                        "--verbose",
                        default=False,
                        action='store_true',
                        dest="verbose")
    parser.add_argument('--default-package', default="com.example",
                        dest="default_package", type=str)
    o = parser.parse_args()
    main(o.args, o)


if __name__ == '__main__':
    entry_point()
