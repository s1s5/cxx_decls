# coding: utf-8
import converter


class ArgConverter(converter.Converter):

    def __init__(self, creator, arg, func_conv):
        super(ArgConverter, self).__init__(creator)
        self.arg = arg
        self.jclass = self.getJClass()
        self.func_conv = func_conv
        self.__an = None

    def isValid(self):
        return True

    def getJClass(self):
        return self.creator.getInterface(self.arg.type)

    def getArgName(self):
        if self.__an is None:
            if not self.arg.name:
                return "arg{}".format(self.__arg_index)
            return self.arg.name
        return self.__an

    def setArgName(self, arg_name):
        self.__an = arg_name

    def imports(self):
        return [self.jclass.jpt]

    def getJavaPubType(self):
        return self.jclass.getClassPath()

    def getJavaPrivType(self):
        return self.jclass.getClassPath()

    def dumpJavaPrivCallPre(self, source):
        pass

    def getJavaPrivCall(self):
        return self.getArgName()

    def dumpJavaPrivCallPost(self, source):
        pass

    def getJniType(self):
        return 'jobject'

    def dumpJniCallPre(self, source):
        pass

    def getJniCall(self):
        return self.getArgName()

    def dumpJniCallPost(self, source):
        pass

    def setIndex(self, index):
        self.__arg_index = index
