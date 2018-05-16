# coding: utf-8
from blueboss import common as bc
import plugin
import jclass
import jpath
import builtin_reference_plugin
# import bridge


def parseType(decl_or_type):
    if isinstance(decl_or_type, bc.ParmVarDecl):
        decl_or_type = decl_or_type.type
    # print "REFERENCE ?? ", decl_or_type, isinstance(
    # decl_or_type, bc.LValueReferenceType)
    if isinstance(decl_or_type, bc.LValueReferenceType):
        p = decl_or_type.pointeeType
    else:
        return None, False
    return p, p.isConstQualified


class ArgConverter(builtin_reference_plugin.BuiltinReferenceArgConverter):

    def __init__(self, *args, **kw):
        super(ArgConverter, self).__init__(*args, **kw)
        t, _ = parseType(self.arg)
        # self.creator.getArgConverter(t, self.func_conv)

    def getCTypeName(self):
        t, _ = parseType(self.arg)
        return t.cname()

    # def getJniCall(self):
    #     return '(%s<%s>(_jenv, %s))' % (bridge.GET_FUNC_NAME,
    #                                     self.getCTypeName(),
    #                                     self.getArgName())


class ReturnConverter(
        builtin_reference_plugin.BuiltinReferenceReturnConverter):

    def __init__(self, *args, **kw):
        super(ReturnConverter, self).__init__(*args, **kw)
        t, _ = parseType(self.cxx_type)
        # print t
        self.creator.getReturnConverter(t, self.func_conv)

    # def dumpJniCall(self, source, call_string):
    #     # if isinstance(self.cxx_type, bc.LValueReferenceType):
    #     #     source << ('p->p = &%s;' % call_string)
    #     # else:
    #     source << ('p->p = &%s;' % call_string)


class ReferencePlugin(plugin.Plugin):

    def resolveFilter(self, decl_or_type):
        decl, _ = parseType(decl_or_type)
        return decl

    def linkStart(self):
        self.classes = {}

    def resolveInterfacePath(self, decl_or_type):
        t, is_const = parseType(decl_or_type)
        # print self.creator.resolveInterfacePath(t)
        # print "resolveInterface >>>>>", hash(t), t
        klass, jp = self.creator.resolveInterfacePath(t)
        # print "resolveInterface <<<<<", hash(t), t
        klass = jclass.Class
        njp = jpath.JPath(jp.path + ('Ref', ))
        self.classes[njp] = decl_or_type
        return klass, njp

    def resolveClassPath(self, decl_or_type):
        return self.resolveInterfacePath(decl_or_type)

    def converterFilter(self, *args):
        t, _ = parseType(args[0])
        return t

    def getArgConverter(self, arg_decl, func_conv):
        return ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return ReturnConverter(self.creator, ret_type, func_conv)

    def linkEnd(self):
        for i in self.classes:
            klass = self.creator.getClass(i)
            klass.setInternalClass(True)
