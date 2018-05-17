# coding: utf-8
import converter


class ArgConverter(converter.Converter):
    def __init__(self, creator, arg, func_conv):
        super(ArgConverter, self).__init__(creator)
        self.arg = arg
        self.func_conv = func_conv
        self.__an = None

    def getArgName(self):
        if self.__an is None:
            if not self.arg.name:
                return "arg{}".format(self.__arg_index)
            return self.arg.name
        return self.__an

    def setArgName(self, arg_name):
        self.__an = arg_name

    def getArgTuple(self):
        return (self.getArgName(), self.getObjCType(), self.getArgName())

    def getObjCType(self):
        d, n = self.creator.resolveClass(self.arg.type)
        if d:
            return n + ' *'
        return n

    def getCType(self):
        return self.arg.type

    def dumpCCallPre(self, source):
        pass

    def getCCall(self):
        return self.getArgName()

    def dumpCCallPost(self, source):
        pass

    def setIndex(self, index):
        self.__arg_index = index
