# coding: utf-8
import math

from blueboss import common as bc
from blueboss import writer as bw
import plugin
import bridge
import jclass
import jpath
import builtin_plugin
import builtin_reference_plugin
import function_converter

GET_DIRECT_ADDRESS = "_get_direct_address"


class PointerAtDecl(bc.CXXMethodDecl):
    pass


class PointerCAtDecl(bc.CXXMethodDecl):
    pass


class PointerClass(jclass.Class):
    pass


class WrapVoidPtrDecl(bc.CXXMethodDecl):
    pass


class WrapArrayDecl(bc.CXXMethodDecl):
    pass


class WrapVoidPtrArg(bc.ParmVarDecl):
    pass


class WrapArrayArg(bc.ParmVarDecl):
    pass


class BuiltinPointerArgConverter(
        builtin_reference_plugin.BuiltinReferenceArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        if (isinstance(cxx_type, bc.PointerType) and
                isinstance(cxx_type.pointeeType, bc.BuiltinType)):
            return klass(creator, arg, func_conv)

    def getJniCall(self):
        return '(%s<%s>(_jenv, %s))' % (bridge.GET_FUNC_NAME,
                                        self.arg.type.pointeeType.spelling,
                                        self.getArgName())


class WrapVoidPtrArgConverter(BuiltinPointerArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        if isinstance(arg, WrapVoidPtrArg):
            return klass(creator, arg, func_conv)

    def imports(self):
        return []

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPubType(self):
        return jpath.ByteBuffer.getClassPath()

    def getJavaPrivCall(self):
        return self.getArgName()

    def dumpJavaPrivCallPre(self, source):
        i = bw.java.If("!%s.isDirect()" % self.getArgName())
        i << ('throw new RuntimeException'
              '("ByteBuffer must be direct buffer");')
        source << i

    def getJniCall(self):
        return "%s<void*>(_jenv, %s)" % (GET_DIRECT_ADDRESS, self.getArgName())


class WrapArrayArgConverter(WrapVoidPtrArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        if isinstance(arg, WrapArrayArg):
            return klass(creator, arg, func_conv)

    def importsSys(self):
        jtype = builtin_plugin.getJavaBuiltinType(self.creator.target_info,
                                                  self.arg.type.pointeeType)
        Jtype = jtype[0].upper() + jtype[1:]
        bb = jpath.JPath(('java', 'nio', '%sBuffer' % Jtype, ), True,
                         ('java', 'nio'), ('%sBuffer' % Jtype, ))
        return [bb, jpath.ByteOrder]

    def getJavaPubType(self):
        return '%s []' % (builtin_plugin.getJavaBuiltinType(
            self.creator.target_info, self.arg.type.pointeeType), )

    def dumpJavaPrivCallPre(self, source):
        jtype = builtin_plugin.getJavaBuiltinType(self.creator.target_info,
                                                  self.arg.type.pointeeType)
        bits = builtin_plugin.getJavaBuiltinTypeBits(self.creator.target_info,
                                                     self.arg.type.pointeeType)
        bn = int(math.ceil(bits / 8.0))
        Jtype = jtype[0].upper() + jtype[1:]
        # print jtype, bits
        source << (
            'ByteBuffer _bb_ = ByteBuffer.allocateDirect(%d * %s.length);' % (
                bn, self.getArgName()))
        source << '_bb_.order(ByteOrder.nativeOrder());'
        source << '%sBuffer _tmp_bb = _bb_.as%sBuffer();' % (Jtype, Jtype)
        source << '_tmp_bb.put(%s);' % self.getArgName()
        # source << 'return new Bridge.Float.Ptr(bb, false, new Bridge());'

    def getJavaPrivCall(self):
        return "_bb_"

    def getJniCall(self):
        return "%s<%s*>(_jenv, %s)" % (GET_DIRECT_ADDRESS,
                                       self.arg.type.pointeeType.spelling,
                                       self.getArgName())


class BuiltinPointerReturnConverter(
        builtin_reference_plugin.BuiltinReferenceReturnConverter):

    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if (isinstance(cxx_type, bc.PointerType) and
                isinstance(cxx_type.pointeeType, bc.BuiltinType)):
            return klass(creator, cxx_type, func_conv)

    def getReferenceString(self):
        return "new Object()"

    def dumpJniCall(self, source, call_string):
        source << ('p->p = const_cast<%s*>(%s);' %
                   (self.cxx_type.pointeeType.spelling,
                    call_string, ))


class InstanceArgConverter(BuiltinPointerArgConverter):

    def __init__(self, creator, decl, func_conv):
        arg = bc.ParmVarDecl("_this",
                             bc.PointerType(bc.BuiltinType(decl.name)))
        super(InstanceArgConverter, self).__init__(creator, arg, func_conv)

    def imports(self):
        return []

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivCall(self):
        return 'this.__getBB()'

    def getJavaPrivType(self):
        return "ByteBuffer"


class BuiltinPointerBaseMethodConverter(function_converter.FunctionConverter):

    def __init__(self, creator, decl):
        super(BuiltinPointerBaseMethodConverter, self).__init__(creator, decl)
        self.instance_arg_converter = InstanceArgConverter(creator,
                                                           decl.parent, self)

    def isStatic(self):
        return self.decl.isStatic

    def getBridgeArgConverters(self):
        return [self.instance_arg_converter] + self.arg_converters


class PointerAtConverter(BuiltinPointerBaseMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is PointerAtDecl:
            return klass(creator, decl)

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        return '%s[%s]' % (l[0], l[1])


class PointerCAtConverter(BuiltinPointerBaseMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is PointerCAtDecl:
            return klass(creator, decl)

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        return '%s[%s]' % (l[0], l[1])


class WrapVoidPtrReturnConverter(BuiltinPointerReturnConverter):
    def getReferenceString(self):
        return self.func_conv.arg_converters[0].getArgName()


# class WrapVoidPtrConverter(BuiltinPointerBaseMethodConverter):
class WrapVoidPtrConverter(function_converter.FunctionConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is WrapVoidPtrDecl:
            return klass(creator, decl)

    # def isStatic(self):
    #     return True

    def getReturnConverter(self):
        return WrapVoidPtrReturnConverter(
            self.creator, self.decl.returnType, self)

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        # return '%s(%s)' % (self.decl.name, ', '.join(l))
        return l[0]


class WrapArrayConverter(WrapVoidPtrConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is WrapArrayDecl:
            return klass(creator, decl)

    # def getJavaPrivName(self):
    #     return None

    # def getJavaPrivCallString(self):
    #     l = map(lambda x: x.getJavaPrivCall(), self.getBridgeArgConverters())
    #     return 'return %s(%s)' % ("wrap", ', '.join(l))


class BuiltinPointerPlugin(plugin.Plugin):

    def includesSys(self):
        return ["cstdint"]

    def depends(self):
        return [builtin_reference_plugin.BuiltinReferencePlugin]

    def resolveFilter(self, decl_or_type):
        return (isinstance(decl_or_type, bc.PointerType) and
                isinstance(decl_or_type.pointeeType, bc.BuiltinType))

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getFunctionConverter(self, func_decl, decl_class=None):
        l = [
            PointerAtConverter.check,
            PointerCAtConverter.check,
            WrapVoidPtrConverter.check,
            WrapArrayConverter.check,
        ]
        return self.__getConverter(l, func_decl)

    def getArgConverter(self, arg_decl, func_decl):
        l = [WrapArrayArgConverter.check,
             WrapVoidPtrArgConverter.check,
             BuiltinPointerArgConverter.check, ]
        return self.__getConverter(l, arg_decl, func_decl)

    def getReturnConverter(self, ret_type, func_decl):
        return BuiltinPointerReturnConverter.check(self.creator, ret_type,
                                                   func_decl)

    def linkStart(self):
        self.classes = {}

    def resolveInterfacePath(self, decl_or_type):
        name = builtin_plugin.getJavaBuiltinType(self.target_info,
                                                 decl_or_type.pointeeType)
        cname = 'Const' + name[0].upper() + name[1:]
        vname = 'C' + name[0].upper() + name[1:]
        cpath = jpath.JPath(("primitives", cname, 'Ptr'))
        vpath = jpath.JPath(("primitives", vname, 'Ptr'))
        if decl_or_type.pointeeType.isConstQualified:
            name = cname
            klass = jclass.Interface
            self.creator.setNamespace(jclass.Class, vpath)
        else:
            name = vname
            klass = jclass.Class
            self.creator.setNamespace(jclass.Interface, jpath.JPath(
                ("primitives", cname, )))
            self.creator.setNamespace(jclass.Interface, cpath)
        if decl_or_type.pointeeType.spelling != "void":
            self.creator.getClass(bc.LValueReferenceType(bc.BuiltinType(
                decl_or_type.pointeeType.spelling)))
            self.creator.resolveInterfacePath(bc.PointerType(bc.BuiltinType(
                "void")))
            self.creator.getClass(bc.PointerType(bc.BuiltinType(
                "void")))
        self.creator.setNamespace(jclass.Interface, jpath.JPath(
            ("primitives", name, )))
        pjp = jpath.JPath(("primitives", name, 'Ptr'))
        self.classes[decl_or_type.pointeeType.spelling] = cpath, vpath
        return klass, pjp

    def resolveClassPath(self, decl_or_type):
        if decl_or_type.pointeeType.isConstQualified:
            decl_or_type = bc.PointerType(bc.BuiltinType(
                decl_or_type.pointeeType.spelling))
        return self.resolveInterfacePath(decl_or_type)

    def linkEnd(self):
        for spelling, (cpath, vpath) in self.classes.items():
            if spelling == 'void':
                void_ptr = cpath, vpath

        for spelling, (cpath, vpath) in self.classes.items():
            # print spelling, cpath, vpath
            cklass = self.creator.getInterface(cpath)
            klass = self.creator.getClass(vpath)
            klass.addBase(cklass)

            if spelling == 'void':
                t = builtin_reference_plugin.builtin_class_wrapper[spelling]
                f = WrapVoidPtrDecl("wrap",
                                    None,
                                    bc.PointerType(bc.BuiltinType("void")),
                                    [WrapVoidPtrArg("ptr",
                                                    bc.BuiltinType("void"), )],
                                    t,
                                    isStatic=True)
                conv = self.creator.getFunctionConverter(f)
                klass.addFunction(conv)
            else:
                klass.setBaseClass(self.creator.getClass(void_ptr[1]))
                t = builtin_reference_plugin.builtin_class_wrapper[spelling]
                f = PointerAtDecl(
                    "at", None,
                    bc.LValueReferenceType(bc.BuiltinType(spelling)),
                    [bc.ParmVarDecl("index",
                                    bc.BuiltinType("int"), )], t)
                conv = self.creator.getFunctionConverter(f)
                klass.addFunction(conv)

                f = PointerCAtDecl("cAt",
                                   None,
                                   bc.LValueReferenceType(
                                       bc.BuiltinType(spelling,
                                                      isConstQualified=True)),
                                   [bc.ParmVarDecl("index",
                                                   bc.BuiltinType("int"))],
                                   t,
                                   isConstQualified=True)
                conv = self.creator.getFunctionConverter(f)
                cklass.addFunction(conv)
                klass.addFunction(conv)

                f = WrapArrayDecl(
                    "wrap",
                    None,
                    bc.PointerType(bc.BuiltinType(spelling)),
                    # f = WrapArrayDecl(t, bc.BuiltinType("void"),
                    [WrapArrayArg("arg",
                                  bc.PointerType(bc.BuiltinType(spelling)), )],
                    t,
                    isStatic=True)
                conv = self.creator.getFunctionConverter(f)
                klass.addFunction(conv)

            # p = self.classes[i].pointeeType
            # spelling = p.spelling
            # klass = self.creator.getClass(self.classes[i])

            # if p.isConstQualified:
            #     conv = self.creator.getFunctionConverter(f)
            #     pass
            # else:
            #     ctype = bc.PointerType(
            # bc.BuiltinType(p.spelling, isConstQualified=True))
            #     cklass = self.creator.getInterface(ctype)
            #     klass.addBase(cklass)

    def jniHeader(self):
        f = bw.cxx.Func("template<class T> T", GET_DIRECT_ADDRESS,
                        ["JNIEnv *_jenv", "jobject _jobj"])
        f << 'jclass bbcls = _jenv->GetObjectClass(_jobj);'
        f << 'jmethodID mid = _jenv->GetMethodID(bbcls, "position", "()I");'
        f << ('void *p = (reinterpret_cast<int8_t*>'
              '(_jenv->GetDirectBufferAddress'
              '(_jobj))) + _jenv->CallIntMethod(_jobj, mid);')
        f << 'return reinterpret_cast<T>(p);'
        return f
