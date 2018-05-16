# coding: utf-8
import converter


class ReturnConverter(converter.Converter):
    def __init__(self, creator, cxx_type, func_conv):
        super(ReturnConverter, self).__init__(creator)
        self.cxx_type = cxx_type
        self.func_conv = func_conv

    def getObjCType(self):
        d, n = self.creator.resolveClass(self.cxx_type)
        if d:
            return n + ' *'
        return n

    def getCType(self):
        return self.cxx_type.cname()

    def dumpCCallPre(self, source):
        pass

    def dumpCCall(self, source, call_string):
        source << ('%s _ret_ = %s;' % (self.getCType(), call_string, ))

    def dumpCReturn(self, source):
        source << "return _ret_;"

    def dumpCCallPost(self, source):
        pass
