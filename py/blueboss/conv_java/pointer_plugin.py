# coding: utf-8
from blueboss import common as bc
import plugin
import jclass
import jpath
import builtin_reference_plugin
import bridge


def parseType(decl_or_type):
    if isinstance(decl_or_type, bc.ParmVarDecl):
        decl_or_type = decl_or_type.type
    if isinstance(decl_or_type, bc.PointerType):
        p = decl_or_type.pointeeType
    # elif (isinstance(decl_or_type, bc.LValueReferenceType) and
    #       isinstance(decl_or_type.pointeeType, bc.PointerType)):
    #     p = decl_or_type.pointeeType
    else:
        return None, False
    return p, p.isConstQualified


def getDepth(decl_or_type):
    c = -1
    decl, _ = parseType(decl_or_type)
    while decl:
        decl, _ = parseType(decl)
        c += 1
    return c


class ArgConverter(builtin_reference_plugin.BuiltinReferenceArgConverter):

    def __init__(self, *args, **kw):
        super(ArgConverter, self).__init__(*args, **kw)
        t, _ = parseType(self.arg)
        # self.creator.getArgConverter(t, self.func_conv)

    def getCTypeName(self):
        t, _ = parseType(self.arg)
        return t.cname()

    def getJniCall(self):
        return '(%s<%s>(_jenv, %s))' % (bridge.GET_FUNC_NAME,
                                        self.getCTypeName(),
                                        self.getArgName())


class ReturnConverter(
        builtin_reference_plugin.BuiltinReferenceReturnConverter):

    def __init__(self, *args, **kw):
        super(ReturnConverter, self).__init__(*args, **kw)
        t, _ = parseType(self.cxx_type)
        self.creator.getReturnConverter(t, self.func_conv)

    def dumpJniCall(self, source, call_string):
        # if isinstance(self.cxx_type, bc.LValueReferenceType):
        #     source << ('p->p = &%s;' % call_string)
        # else:
        source << ('p->p = %s;' % call_string)


class PointerPlugin(plugin.Plugin):

    def resolveFilter(self, decl_or_type):
        decl, _ = parseType(decl_or_type)
        return decl

    def linkStart(self):
        self.classes = {}

    def resolveInterfacePath(self, decl_or_type):
        d = getDepth(decl_or_type)
        t, is_const = parseType(decl_or_type)
        klass, jp = self.creator.resolveInterfacePath(t)
        if not jp.path:
            return
        klass = jclass.Class
        njp = jpath.JPath(jp.path + ('Ptr%d' % d, ))
        self.classes[njp] = decl_or_type
        return klass, njp

    def resolveClassPath(self, decl_or_type):
        return self.resolveInterfacePath(decl_or_type)

    def converterFilter(self, *args):
        klass, jp = self.creator.resolveInterfacePath(args[0])
        if not jp.path:
            return
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
