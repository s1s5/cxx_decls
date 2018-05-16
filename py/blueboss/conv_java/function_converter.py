# coding: utf-8
from blueboss import common as bc
import converter


class FunctionConverter(converter.Converter):
    @classmethod
    def check(klass, creator, decl):
        if type(decl) is bc.FunctionDecl:
            return klass(creator, decl)

    def __init__(self, creator, decl):
        super(FunctionConverter, self).__init__(creator)
        self.decl = decl
        self.return_converter = self.getReturnConverter()
        self.arg_converters = self.getArgConverters()
        self.java_pub_name = None

    def isValid(self):
        t = self.return_converter.isValid()
        t = reduce(lambda x, y: x and y.isValid(), self.arg_converters, t)
        return t

    def getReturnConverter(self):
        return self.creator.getReturnConverter(self.decl.returnType, self)

    def getArgConverters(self):
        return map(lambda x: self.creator.getArgConverter(x, self),
                   self.decl.params)

    def imports(self):
        return (self.return_converter.imports() + reduce(
            lambda x, y: x + y.imports(), self.arg_converters, []))

    def importsSys(self):
        return (self.return_converter.importsSys() + reduce(
            lambda x, y: x + y.importsSys(), self.arg_converters, []))

    def isStatic(self):
        return True

    def setPrivName(self, jpath, name):
        self.priv_name = name
        self.jni_name = jpath.getJniFuncName(name)

    def annotations(self):
        return []

    def getJavaPubAccess(self):
        return "public"

    def setJavaPubName(self, n):
        self.java_pub_name = n

    def getJavaPubName(self):
        if self.java_pub_name is None:
            return self.decl.name.split('::')[-1]
        return self.java_pub_name

    def getSignature(self):
        return (self.getJavaPubName() + '$' + '+'.join(map(
            lambda x: x.getJavaPubType(), self.getJavaPubArgConverters())))

    def getFunctionId(self):
        s = self.getSignature()
        if hasattr(self.decl, 'isConst') and self.decl.isConst:
            s += 'C'
        s += self.getJavaPubReturnType()
        return s

    def getJavaPubReturnType(self):
        return self.return_converter.getJavaPubType()

    def getJavaPubArgConverters(self):
        return self.arg_converters

    def getJavaPubArgs(self):
        return zip(
            map(lambda x: x.getJavaPubType(), self.getJavaPubArgConverters()),
            map(lambda x: x.getArgName(), self.getJavaPubArgConverters()))

    def getJavaPrivName(self):
        return self.priv_name

    def getJavaPrivReturnType(self):
        return self.return_converter.getJavaPrivType()

    def getBridgeArgConverters(self):
        return self.arg_converters

    def getBridgeArgNames(self):
        return map(lambda x: x.getArgName(), self.getBridgeArgConverters())

    def getJavaPrivArgs(self):
        return zip(
            map(lambda x: x.getJavaPrivType(), self.getBridgeArgConverters()),
            map(lambda x: x.getArgName(), self.getBridgeArgConverters()))

    def dumpJavaPrivCallPre(self, source):
        pass

    def getJavaPrivCallString(self):
        l = map(lambda x: x.getJavaPrivCall(), self.getBridgeArgConverters())
        return '%s(%s)' % (self.getJavaPrivName(), ', '.join(l))

    def dumpJavaPrivCall(self, source):
        self.dumpJavaPrivCallPre(source)
        map(lambda x: x.dumpJavaPrivCallPre(source),
            self.getBridgeArgConverters())
        self.return_converter.dumpJavaPrivCallPre(source)
        call_string = self.getJavaPrivCallString()
        self.return_converter.dumpJavaPrivCall(source, call_string)
        map(lambda x: x.dumpJavaPrivCallPost(source),
            self.getBridgeArgConverters())
        self.return_converter.dumpJavaPrivCallPost(source)
        self.dumpJavaPrivCallPost(source)
        self.return_converter.dumpJavaPrivReturn(source)

    def dumpJavaPrivCallPost(self, source):
        pass

    def getJniName(self):
        return self.jni_name

    def getJniReturnType(self):
        return self.return_converter.getJniType()

    def getJniDefaultArgs(self):
        if self.isStatic():
            return ["JNIEnv *_jenv", "jclass _jclass"]
        else:
            return ["JNIEnv *_jenv", "jobject _jobj"]

    def getJniArgs(self):
        return self.getJniDefaultArgs() + zip(
            map(lambda x: x.getJniType(), self.getBridgeArgConverters()), map(
                lambda x: x.getArgName(), self.getBridgeArgConverters()))

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        return '%s(%s)' % (self.decl.path, ', '.join(l))

    def dumpJniCallPre(self, source):
        pass

    def dumpJniCall(self, source):
        self.dumpJniCallPre(source)
        map(lambda x: x.dumpJniCallPre(source), self.getBridgeArgConverters())
        self.return_converter.dumpJniCallPre(source)
        call_string = self.getJniCallString()
        self.return_converter.dumpJniCall(source, call_string)
        map(lambda x: x.dumpJniCallPost(source), self.getBridgeArgConverters())
        self.return_converter.dumpJniCallPost(source)
        self.dumpJniCallPost(source)
        self.return_converter.dumpJniReturn(source)

    def dumpJniCallPost(self, source):
        pass
