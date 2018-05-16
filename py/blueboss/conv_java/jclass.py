# coding: utf-8
from blueboss import writer as bw
import jpath
import function_converter


class Interface(object):

    def __init__(self, creator, jpt):
        if not isinstance(jpt, jpath.JPath):
            raise TypeError()
        self.creator = creator
        self.jpt = jpt
        self.bases = []
        self.funcs = []
        self.__linked = False
        self.is_top = False
        self.is_internal_class = False
        self.is_valid = True

    def isValid(self):
        return self.is_valid

    def isSys(self):
        return False

    def getClassPath(self):
        return self.jpt.getClassPath()

    def getImportPath(self):
        return self.jpt.getImportPath()

    def setTopLevel(self, is_top):
        self.is_top = is_top

    def setInternalClass(self, flag):
        self.is_internal_class = flag

    def link(self, default_package):
        self.jpt.package_path = default_package + self.jpt.package_path
        self.funcs = map(lambda x: x[1], sorted(zip(
            map(lambda x: x.getFunctionId(), self.funcs), self.funcs)))
        for i in xrange(len(self.funcs)):
            if not self.funcs[i].isValid():
                continue
            org_name = self.funcs[i].getJavaPubName()
            signature = self.funcs[i].getSignature()
            counter = 0
            flag = True
            while flag:
                flag = False
                for j in xrange(i):
                    if not self.funcs[j].isValid():
                        continue
                    if self.funcs[j].getSignature() == signature:
                        flag = True
                if flag:
                    self.funcs[i].setJavaPubName('%s%d' % (org_name, counter))
                    signature = self.funcs[i].getSignature()
                    counter += 1
                if counter > 1000:
                    raise Exception()
        self.__linked = True

    def addBase(self, jpt):
        if not isinstance(jpt, Interface):
            raise TypeError()
        if jpt in self.bases:
            return
        if self.jpt.path == jpt.jpt.path:
            raise Exception()
        self.bases.append(jpt)

    def addFunction(self, func_conv):
        if not isinstance(func_conv, function_converter.FunctionConverter):
            raise Exception()
        if func_conv in self.funcs:
            return
        if not func_conv.isValid():
            return
        self.funcs.append(func_conv)

    def findFunction(self, klass):
        return filter(lambda x: isinstance(x, klass), self.funcs)

    def getBases(self):
        return self.bases + [self.creator.getBaseInterface()]

    def javaSource(self):
        access = ""
        if self.is_top:
            access = "public"
        bases = map(lambda x: x.jpt.getClassPath(), self.getBases())
        interface = bw.java.Interface(self.jpt.class_path[-1],
                                      bases,
                                      access=access)
        for i in self.funcs:
            r = i.getJavaPubReturnType()
            n = i.getJavaPubName()
            a = i.getJavaPubArgs()
            interface << bw.java.FuncDecl(r, n, a)
        return interface

    def jniHeader(self):
        return bw.cxx.StatementList()

    def jniSource(self):
        return bw.cxx.StatementList()

    def imports(self):
        return []
        # _imports = set()
        # map(lambda x: _imports.update(x.imports()), self.funcs)
        # map(lambda x: _imports.add(x.jpt), filter(lambda x: not x.isSys(),
        #                                           self.getBases()))
        # if self.jpt in _imports:
        #     _imports.remove(self.jpt)
        # return list(_imports)

    def importsSys(self):
        _imports = set()
        map(lambda x: _imports.update(x.importsSys()), self.funcs)
        map(lambda x: _imports.add(x.jpt), filter(lambda x: x.isSys(),
                                                  self.getBases()))
        return [jpath.ByteBuffer, ] + list(_imports)


class Class(Interface):

    def __init__(self, *args, **kw):
        super(Class, self).__init__(*args, **kw)
        self.base_class = None

    def link(self, default_package):
        super(Class, self).link(default_package)
        jp = jpath.JPath(self.jpt.path, self.jpt.is_sys,
                         self.jpt.package_path,
                         self.jpt.class_path)
        for idx, i in enumerate(self.funcs):
            i.setPrivName(jp, 'f%d' % idx)

    def getBaseClass(self):
        if self.base_class is None:
            return self.creator.getBaseClass()
        return self.base_class

    def setBaseClass(self, base_class):
        self.base_class = base_class

    def getBases(self):
        k = self.getBaseClass()
        if k is None:
            return self.bases
        return self.bases + [k]

    def dumpFunctions(self, klass):
        for i in self.funcs:
            r = i.getJavaPubReturnType()
            n = i.getJavaPubName()
            a = i.getJavaPubArgs()
            s = ""
            if i.isStatic():
                s = " static"
            pub_func = bw.java.Func(
                r, n, a, access="%s%s" % (i.getJavaPubAccess(), s))
            i.dumpJavaPrivCall(pub_func)
            klass << pub_func

        for i in self.funcs:
            r = i.getJavaPrivReturnType()
            n = i.getJavaPrivName()
            a = i.getJavaPrivArgs()
            if (i.getJavaPrivName() is None):
                continue
            s = ""
            if i.isStatic():
                s = " static"
            priv_func = bw.java.FuncDecl(r,
                                         n,
                                         a,
                                         access="private%s native" % s)
            klass << priv_func

    def javaSource(self):
        access = ""
        if self.is_top:
            access = "public"
        if self.is_internal_class:
            access = "public static"
        base = self.getBaseClass()
        if base is None:
            base = ''
        else:
            base = base.jpt.getClassPath()
        bases = map(lambda x: x.jpt.getClassPath(),
                    filter(lambda x: type(x) is Interface, self.bases))
        klass = bw.java.Class(self.jpt.class_path[-1],
                              base,
                              bases,
                              access=access)
        self.dumpFunctions(klass)
        self.dumpConstructor(klass)
        return klass

    def dumpConstructor(self, klass):
        func = bw.java.Func("", self.jpt.class_path[-1],
                            ["ByteBuffer o", "Object owner"])
        func << "super(o, owner);"
        klass << func

    def jniHeader(self):
        sl = bw.cxx.StatementList()
        for i in self.funcs:
            if (i.getJavaPrivName() is None):
                continue
            r = 'JNIEXPORT %s JNICALL' % i.getJniReturnType()
            n = i.getJniName()
            a = i.getJniArgs()
            sl << bw.cxx.FuncDec(r, n, a)
        return sl

    def jniSource(self):
        sl = bw.cxx.StatementList()
        for i in self.funcs:
            if (i.getJavaPrivName() is None):
                continue
            r = i.getJniReturnType()
            n = i.getJniName()
            a = i.getJniArgs()
            func = bw.cxx.Func(r, n, a)
            i.dumpJniCall(func)
            sl << func
        return sl


class FunctionClass(Class):
    pass


class BaseInterface(Interface):

    def javaSource(self):
        access = ""
        if self.is_top:
            access = "public"
        interface = bw.java.Interface(self.jpt.class_path[-1], access=access)
        f = bw.java.FuncDecl("ByteBuffer", "__getBB", [])
        interface << f
        return interface

    def importsSys(self):
        return [jpath.ByteBuffer]


class BaseClass(Class):

    def javaSource(self):
        access = ""
        if self.is_top:
            access = "public"
        klass = bw.java.Class(
            self.jpt.class_path[-1],
            None,
            [
                '.'.join(self.creator.getBaseInterface().jpt.class_path)
            ],
            access=access)
        klass << "private ByteBuffer __bb;"
        klass << "private Object __owner;"
        func = bw.java.Func("",
                            self.jpt.class_path[-1],
                            [],
                            access="protected")
        func << "__bb = null;"
        func << "__owner = null;"
        klass << func
        func = bw.java.Func("",
                            self.jpt.class_path[-1],
                            ["ByteBuffer o", "Object owner"],
                            access="protected")
        func << "__bb = o;"
        func << "__owner = owner;"
        klass << func

        func = bw.java.Func("void",
                            "__set",
                            ["ByteBuffer o", "Object owner"],
                            access="protected")
        func << "__bb = o;"
        func << "__owner = owner;"
        klass << func

        func = bw.java.Func("ByteBuffer", "__getBB", [])
        func << "return __bb;"
        klass << func

        self.dumpFunctions(klass)

        return klass

    def imports(self):
        return [self.creator.getBaseInterface().jpt, ]

    def importsSys(self):
        return [jpath.ByteBuffer, ]
