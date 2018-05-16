# coding: utf-8
from blueboss import writer as bw
from blueboss import common as bc
import jpath
import jclass
import plugin
import arg_converter
import return_converter


def c2jFunc(decl):
    return "c2jEnum" + '_'.join(decl.path.split('::'))


def j2cFunc(decl):
    return "j2cEnum" + '_'.join(decl.path.split('::'))


def getEnumDecl(d):
    if isinstance(d, bc.ParmVarDecl):
        d = d.type
    if isinstance(d, bc.ElaboratedType):
        d = d.namedType
    if isinstance(d, bc.EnumType):
        return d


class EnumClass(jclass.Class):
    def getBaseClass(self):
        return None

    def setEnum(self, enum):
        self.enum = enum

    def javaSource(self):
        klass = super(EnumClass, self).javaSource()
        cp = self.jpt.getClassPath()
        for idx, i in enumerate(self.enum.enumerators):
            klass << ("public static %s %s = new %s(%d, %d);" %
                      (cp, i.name, cp, idx, i.value))
            # print i.name, i.value
        klass << "private int __i;"
        klass << "private int __v;"
        func = bw.java.Func("int", "getId", [])
        func << "return __i;"
        klass << func
        func = bw.java.Func("int", "getValue", [])
        func << "return __v;"
        klass << func
        func = bw.java.Func(cp, "get", ["int v"], is_static=True)
        sw = bw.java.Switch("v")
        for idx, i in enumerate(self.enum.enumerators):
            sw << (bw.java.Case(str(idx)) << "return %s;" % i.name)
        func << sw
        func << "return %s;" % self.enum.enumerators[0].name
        klass << func
        return klass

    def dumpConstructor(self, klass):
        func = bw.java.Func("",
                            self.jpt.class_path[-1],
                            ["int idx",
                             "int v", ],
                            access="private")
        func << "__i = idx;"
        func << "__v = v;"
        klass << func


class EnumArgConverter(arg_converter.ArgConverter):
    @classmethod
    def check(klass, creator, arg, func_conv):
        if getEnumDecl(arg):
            return klass(creator, arg, func_conv)

    def getJavaPrivType(self):
        return "int"

    def getJavaPrivCall(self):
        return "%s.getId()" % self.getArgName()

    def getJniType(self):
        return 'jint'

    def getJniCall(self):
        cxx_type = self.arg.type
        if isinstance(cxx_type, bc.ElaboratedType):
            cxx_type = cxx_type.namedType
        return "%s(%s)" % (j2cFunc(cxx_type.decl), self.getArgName())


class EnumReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if getEnumDecl(cxx_type):
            return klass(creator, cxx_type, func_conv)

    def getJavaPrivType(self):
        return "int"

    def dumpJavaPrivReturn(self, source):
        source << "return %s.get(_ret_);" % self.jclass.getClassPath()

    def getJniType(self):
        return 'jint'

    def dumpJniCall(self, source, call_string):
        cxx_type = self.cxx_type
        if isinstance(cxx_type, bc.ElaboratedType):
            cxx_type = cxx_type.namedType
        source << ('%s _ret_ = %s(%s);' % (self.getJniType(),
                                           c2jFunc(cxx_type.decl),
                                           call_string, ))


class EnumPlugin(plugin.Plugin):
    def linkStart(self):
        self.classes = {}
        self.arg_set = set()
        self.ret_set = set()

    def resolveFilter(self, decl_or_type):
        if isinstance(decl_or_type, bc.ElaboratedType):
            decl_or_type = decl_or_type.namedType
        return (isinstance(decl_or_type, bc.EnumType) or
                isinstance(decl_or_type, bc.EnumDecl))

    def resolveInterfacePath(self, decl_or_type):
        return self.creator.resolveClassPath(decl_or_type)

    def resolveClassPath(self, decl_or_type):
        if isinstance(decl_or_type, bc.ElaboratedType):
            decl_or_type = decl_or_type.namedType
        if isinstance(decl_or_type, bc.EnumType):
            decl_or_type = decl_or_type.decl
        n = decl_or_type.path.split('::')
        jpt = jpath.JPath(tuple(n))
        self.classes[jpt] = decl_or_type
        return EnumClass, jpt

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getArgConverter(self, arg_decl, func_conv):
        l = [EnumArgConverter.check, ]
        if getEnumDecl(arg_decl):
            self.arg_set.add(getEnumDecl(arg_decl).decl)
        return self.__getConverter(l, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        l = [EnumReturnConverter.check, ]
        if getEnumDecl(ret_type):
            self.ret_set.add(getEnumDecl(ret_type).decl)
        return self.__getConverter(l, ret_type, func_conv)

    def declare(self, decl):
        if not isinstance(decl, bc.EnumDecl):
            return False
        if decl.access != "public" and decl.access != "none":
            return False
        self.creator.getClass(bc.EnumType(decl, decl.name))
        # klass = self.creator.getClass(bc.EnumType(decl, decl.name))
        # print klass
        # print decl
        return True

    def linkEnd(self):
        headers = bw.cxx.StatementList()
        sources = bw.cxx.StatementList()
        for jpt, decl in self.classes.items():
            klass = self.creator.getClass(jpt)
            klass.setEnum(decl)
            if decl in self.ret_set:
                self.dumpReturnConverter(decl, headers, sources)
            if decl in self.arg_set:
                self.dumpArgConverter(decl, headers, sources)

        self.headers = headers
        self.sources = sources

    def dumpReturnConverter(self, decl, hl, sl):
        func = bw.cxx.Func("jint", c2jFunc(decl), [(decl.path, "value")])
        # hl << ('%s;' % func.decl)
        prefix = ""
        if True or decl.isScoped:
            prefix = decl.path + "::"
        for idx, i in enumerate(decl.enumerators):
            cond = "value == %s%s" % (prefix, i.name)
            if idx == 0:
                t = bw.cxx.If(cond)
            else:
                t = bw.cxx.ElseIf(cond)
            t << "return %d;" % idx
            func << t
        func << "return 0;"
        hl << func

    def dumpArgConverter(self, decl, hl, sl):
        func = bw.cxx.Func(decl.path, j2cFunc(decl), [("jint", "value")])
        # hl << ('%s;' % func.decl)
        sw = bw.cxx.Switch("value")
        prefix = ""
        if True or decl.isScoped:
            prefix = decl.path + "::"
        for idx, i in enumerate(decl.enumerators):
            sw << (bw.cxx.Case(str(idx)) << "return %s%s;" % (prefix, i.name))
        func << sw
        func << "return %s%s;" % (prefix, decl.enumerators[0].name)
        hl << func

    def jniHeader(self):
        return self.headers

    def jniSource(self):
        return self.sources
