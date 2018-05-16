# coding: utf-8
from blueboss import common as bc
import jpath
import jclass
import plugin
import return_converter
import arg_converter
import function_converter
import builtin_plugin
import bridge


class BuiltinRecord(bc.CXXRecordDecl):
    pass


builtin_class_wrapper = dict(map(lambda x: (x, BuiltinRecord(x)),
                                 bc.builtin_types))


class BuiltinReferenceGetMethod(bc.CXXMethodDecl):
    pass


class BuiltinReferenceAssignMethod(bc.CXXMethodDecl):
    pass


class BuiltinReferenceArgConverter(arg_converter.ArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        if (isinstance(cxx_type, bc.LValueReferenceType) and
            isinstance(cxx_type.pointeeType, bc.BuiltinType) and
                (not cxx_type.pointeeType.isConstQualified)):
            return klass(creator, arg, func_conv)

    # def imports(self):
    #     return super(BuiltinReferenceArgConverter, self).imports()

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivType(self):
        return 'ByteBuffer'

    def getJavaPrivCall(self):
        return self.getArgName() + '.__getBB()'

    def getCTypeName(self):
        return self.arg.type.pointeeType.spelling

    def getJniCall(self):
        return '(*(%s<%s>(_jenv, %s)))' % (bridge.GET_FUNC_NAME,
                                           self.getCTypeName(),
                                           self.getArgName())


class BuiltinReferenceReturnConverter(return_converter.ReturnConverter):

    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if (isinstance(cxx_type, bc.LValueReferenceType) and
            isinstance(cxx_type.pointeeType, bc.BuiltinType) and
                (not cxx_type.pointeeType.isConstQualified)):
            return klass(creator, cxx_type, func_conv)

    def getJavaPrivType(self):
        return 'ByteBuffer'

    def dumpJavaPrivCall(self, source, call_string):
        source << 'ByteBuffer _ret_ = %s;' % call_string

    def getReferenceString(self):
        if isinstance(self.cxx_type, bc.LValueReferenceType):
            if self.func_conv.isStatic():
                return "new Object()"
            else:
                return "(Object)this"
        return "null"

    def dumpJavaPrivReturn(self, source):
        jcls = self.jclass.getClassPath()
        r = self.getReferenceString()
        source << "return new %s(_ret_, %s);" % (jcls, r)

    def getJniType(self):
        return 'jobject'

    def dumpJniCallPre(self, source):
        source << "jobject _bb_ = %s(_jenv);" % bridge.CREATE_FUNC_NAME
        source << '%s *p = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                      bridge.STRUCT_NAME)
        source << '    _jenv->GetDirectBufferAddress(_bb_));'

    def dumpJniCall(self, source, call_string):
        source << ('p->p = &(%s);' % call_string)

    def dumpJniReturn(self, source):
        source << "return _bb_;"


class InstanceArgConverter(BuiltinReferenceArgConverter):

    def __init__(self, creator, decl, func_conv):
        arg = bc.ParmVarDecl("_this",
                             bc.LValueReferenceType(bc.BuiltinType(decl.name)))
        super(InstanceArgConverter, self).__init__(creator, arg, func_conv)

    def imports(self):
        return []

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivCall(self):
        return 'this.__getBB()'

    def getJavaPrivType(self):
        return "ByteBuffer"


class BuiltinReferenceBaseMethodConverter(
        function_converter.FunctionConverter):

    def __init__(self, creator, decl):
        super(BuiltinReferenceBaseMethodConverter, self).__init__(creator,
                                                                  decl)
        self.instance_arg_converter = self.getInstanceArgConverter()

    def getInstanceArgConverter(self):
        return InstanceArgConverter(self.creator, self.decl.parent, self)

    def isStatic(self):
        return False

    def getBridgeArgConverters(self):
        return [self.instance_arg_converter] + self.arg_converters


class BuiltinReferenceGetMethodConverter(BuiltinReferenceBaseMethodConverter):

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        return l[0]


class BuiltinReferenceAssignMethodConverter(
        BuiltinReferenceBaseMethodConverter):

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        return "%s = %s" % (l[0], l[1])


class BuiltinReferencePlugin(plugin.Plugin):

    def depends(self):
        return [bridge.BridgePlugin]

    def resolveFilter(self, decl_or_type):
        return (isinstance(decl_or_type, bc.LValueReferenceType) and
                isinstance(decl_or_type.pointeeType, bc.BuiltinType) and
                (not decl_or_type.pointeeType.isConstQualified))

    def resolveInterfacePath(self, decl_or_type):
        name = builtin_plugin.getJavaBuiltinType(self.target_info,
                                                 decl_or_type.pointeeType)
        name = 'C' + name[0].upper() + name[1:]
        self.builtin_types.append(decl_or_type)
        return jclass.Interface, jpath.JPath(("primitives", name, ))

    def resolveClassPath(self, decl_or_type):
        res = self.creator.resolveInterfacePath(decl_or_type)
        if res:
            self.builtin_types.append(decl_or_type)
            return jclass.Class, jpath.JPath(res[1].path + ('Impl', ))

    def getFunctionConverter(self, func_decl, decl_class=None):
        if isinstance(func_decl, BuiltinReferenceGetMethod):
            return BuiltinReferenceGetMethodConverter(self.creator, func_decl)
        if isinstance(func_decl, BuiltinReferenceAssignMethod):
            return BuiltinReferenceAssignMethodConverter(self.creator,
                                                         func_decl)

    def getArgConverter(self, arg_decl, func_decl):
        return BuiltinReferenceArgConverter.check(self.creator, arg_decl,
                                                  func_decl)

    def getReturnConverter(self, ret_type, func_decl):
        return BuiltinReferenceReturnConverter.check(self.creator, ret_type,
                                                     func_decl)

    def linkStart(self):
        self.builtin_types = []

    def linkEnd(self):
        processed = set()
        for i in list(self.builtin_types):
            interface = self.creator.getInterface(i)
            klass = self.creator.getClass(i)
            if interface in processed:
                continue
            spelling = i.pointeeType.spelling
            processed.add(interface)
            klass.addBase(interface)
            t = builtin_class_wrapper[spelling]
            f = BuiltinReferenceGetMethod("get", None,
                                          bc.BuiltinType(spelling), [], t)
            conv = self.creator.getFunctionConverter(f)
            interface.addFunction(conv)
            klass.addFunction(conv)
            f = BuiltinReferenceAssignMethod(
                "assign", None, bc.BuiltinType("void"),
                [bc.ParmVarDecl("arg",
                                bc.BuiltinType(spelling), )], t)
            conv = self.creator.getFunctionConverter(f)
            interface.addFunction(conv)
            klass.addFunction(conv)

    # def generalClass(self):
    #     st = bw.cxx.Struct(STRUCT_NAME)
    #     st << "void *p;"
    #     return st

    # def createInstanceCodeBase(self):
    #     func = bw.cxx.Func("jobject", CREATE_FUNC_NAME, ["JNIEnv *_jenv", ])
    #     func << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
    #     func << 'jmethodID mid = _jenv->GetStaticMethodID('
    #     func << '    bbcls, "allocateDirect", "(I)Ljava/nio/ByteBuffer;");'
    #     func << 'jobject bb = _jenv->CallStaticObjectMethod('
    #     func << '    bbcls, mid, sizeof(%s));' % STRUCT_NAME
    #     func << 'return bb;'
    #     return func

    # def getBuiltinInstanceCode(self):
    #     func = bw.cxx.Func("template<class T> T *", GET_FUNC_NAME,
    #                        ["JNIEnv *_jenv", "jobject _this"])
    #     func << '%s *p = reinterpret_cast<%s*>(' % (STRUCT_NAME, STRUCT_NAME)
    #     func << '    _jenv->GetDirectBufferAddress(_this));'
    #     func << "return reinterpret_cast<T*>(p->p);"
    #     return func

    # def jniHeader(self):
    #     if not self.builtin_types:
    #         return
    #     sl = bw.cxx.StatementList()
    #     sl << self.generalClass()
    #     sl << self.createInstanceCodeBase()
    #     sl << self.getBuiltinInstanceCode()
    #     return sl

    # def jniSource(self):
    #     pass
