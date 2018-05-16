# coding: utf-8
from blueboss import writer as bw
from blueboss import common as bc
import plugin
import base
import arg_converter
import return_converter


def parseType(d):
    if isinstance(d, bc.ParmVarDecl):
        d = d.type
    if isinstance(d, bc.ElaboratedType):
        d = d.namedType
    if isinstance(d, bc.EnumType):
        d = d.decl
    if not isinstance(d, bc.EnumDecl):
        return None
    return d


def enumObjCName(creator, decl, c):
    prefix = ""
    if decl.isScoped:
        prefix = (creator.settings['global_prefix'] +
                  '_'.join(decl.path.split('::')) + "_")
    else:
        prefix = creator.settings['global_prefix']
    return prefix + c.name


def c2objc(creator, decl):
    p = '_'.join(decl.path.split('::'))
    return "_enum_c2objc_%s" % p


def objc2c(creator, decl):
    p = '_'.join(decl.path.split('::'))
    return "_enum_obj2c_%s" % p


class ArgConverter(arg_converter.ArgConverter):
    def getCCall(self):
        decl = parseType(self.arg)
        return '%s(%s)' % (objc2c(self.creator, decl), self.getArgName())


class ReturnConverter(return_converter.ReturnConverter):
    def dumpCReturn(self, source):
        decl = parseType(self.cxx_type)
        source << "return %s(_ret_);" % c2objc(self.creator, decl)


class EnumPlugin(plugin.Plugin):
    def linkStart(self):
        self.enums = set()

    def resolveClass(self, decl_or_type):
        decl = parseType(decl_or_type)
        if decl is None:
            return None
        return None, base.getName(self.creator, decl)

    def hook(self, decl_or_type):
        decl = parseType(decl_or_type)
        if decl is None:
            return
        self.enums.add(decl)

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def converterFilter(self, *args):
        decl = parseType(args[0])
        return decl

    def getArgConverter(self, arg_decl, func_conv):
        return ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return ReturnConverter(self.creator, ret_type, func_conv)

    def declare(self, decl):
        if not isinstance(decl, bc.EnumDecl):
            return False

        self.hook(decl)
        return True

    def linkEnd(self):
        pass

    def objcHeader(self):
        sl = bw.objc.StatementList()
        for e in sorted(self.enums, key=lambda x: x.path):
            if e.access != "public" and e.access != "none":
                continue
            _, n = self.resolveClass(e)
            l = bw.objc.Enum(n)
            if e.isScoped:
                for i in e.enumerators:
                    l << "%s," % enumObjCName(self.creator, e, i)
            else:
                for i in e.enumerators:
                    l << "%s = %d," % (
                        enumObjCName(self.creator, e, i), i.value)
            sl << l
        return sl

    def objcSourcePrivate(self):
        sl = bw.objc.StatementList()
        for e in sorted(self.enums, key=lambda x: x.path):
            if e.access != "public" and e.access != "none":
                continue
            cn = e.cname()
            _, on = self.resolveClass(e)
            f0 = bw.cxx.Func(cn, objc2c(self.creator, e), [(on, "value")])
            f1 = bw.cxx.Func(on, c2objc(self.creator, e), [(cn, "value")])
            for idx, i in enumerate(e.enumerators):
                n = enumObjCName(self.creator, e, i)
                cond0 = "value == %s" % (n)
                cond1 = "value == %s" % (i.cname())
                if idx == 0:
                    t0 = bw.cxx.If(cond0)
                    t1 = bw.cxx.If(cond1)
                else:
                    t0 = bw.cxx.ElseIf(cond0)
                    t1 = bw.cxx.ElseIf(cond1)
                t0 << "return %s;" % i.cname()
                t1 << "return %s;" % n
                f0 << t0
                f1 << t1
            if e.enumerators:
                i = e.enumerators[0]
                n = enumObjCName(self.creator, e, i)
                f0 << "return %s;" % i.cname()
                f1 << "return %s;" % n
            sl << f0
            sl << f1
        return sl

    def objcSourcePublic(self):
        pass
