# coding: utf-8
import converter


class ReturnConverter(converter.Converter):

    def __init__(self, creator, cxx_type, func_conv):
        super(ReturnConverter, self).__init__(creator)
        self.cxx_type = cxx_type
        self.func_conv = func_conv
        self.jinterface = self.getJInterface()
        self.jclass = self.getJClass()

    def isValid(self):
        return True

    def getJInterface(self):
        return self.creator.getInterface(self.cxx_type)

    def getJClass(self):
        return self.creator.getClass(self.cxx_type)

    def imports(self):
        return [self.jclass.jpt, self.jinterface.jpt]

    def getJavaPubType(self):
        return self.jinterface.getClassPath()

    def getJavaPrivType(self):
        return self.jclass.getClassPath()

    def dumpJavaPrivCallPre(self, source):
        pass

    def dumpJavaPrivCall(self, source, call_string):
        source << ('%s _ret_ = %s;' % (self.getJavaPrivType(), call_string))

    def dumpJavaPrivReturn(self, source):
        source << "return _ret_;"

    def dumpJavaPrivCallPost(self, source):
        pass

    def getJniType(self):
        return 'jobject'

    def dumpJniCallPre(self, source):
        pass

    def dumpJniCall(self, source, call_string):
        source << ('%s _ret_ = %s;' % (self.getJniType(), call_string, ))

    def dumpJniReturn(self, source):
        source << "return _ret_;"

    def dumpJniCallPost(self, source):
        pass
