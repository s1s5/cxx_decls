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

    def isValid(self):
        v = self.return_converter.isValid()
        for a in self.arg_converters:
            v = v and a.isValid()
        return v

    def isStatic(self):
        return True

    def isPrivate(self):
        return False

    def getName(self):
        suffix = ''
        if hasattr(self.decl, '_objc_name'):
            suffix = self.decl._objc_name
        l = self.decl.path.split('::')
        if len(l) == 1:
            return self.creator.settings['global_prefix'] + l[0] + suffix
        else:
            return l[-1] + suffix

    def getUid(self):
        n = self.getName()
        return n + str(map(lambda x: x.getArgTuple(), self.arg_converters))

    def getReturnConverter(self):
        return self.creator.getReturnConverter(self.decl.returnType, self)

    def getArgConverters(self):
        converters = map(lambda x: self.creator.getArgConverter(x, self),
                         self.decl.params)
        [x.setIndex(i) for i, x in enumerate(converters)]
        return converters

    def getFuncTuple(self):
        ret = self.return_converter.getObjCType()
        args = map(lambda x: x.getArgTuple(), self.arg_converters)
        return ret, self.getName(), args, self.isStatic()

    def getFuncName(self):
        return self.creator.resolveName(self.decl)

    def getCArgs(self):
        return self.getCDefaultArgs() + zip(
            map(lambda x: x.getCType(), self.arg_converters), map(
                lambda x: x.getArgName(), self.arg_converters))

    def getCCallString(self):
        l = map(lambda x: x.getCCall(), self.arg_converters)
        return '%s(%s)' % (self.decl.path, ', '.join(l))

    def dumpCCallPre(self, source):
        pass

    def dumpCCallImpl(self, source):
        call_string = self.getCCallString()
        self.return_converter.dumpCCall(source, call_string)
        map(lambda x: x.dumpCCallPost(source), self.arg_converters)

    def dumpCCall(self, source):
        self.dumpCCallPre(source)
        map(lambda x: x.dumpCCallPre(source), self.arg_converters)
        self.return_converter.dumpCCallPre(source)
        self.dumpCCallImpl(source)
        self.return_converter.dumpCCallPost(source)
        self.dumpCCallPost(source)
        self.return_converter.dumpCReturn(source)

    def dumpCCallPost(self, source):
        pass
