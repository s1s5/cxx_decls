# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import plugin
import arg_converter
import return_converter


def isBuiltinVector(cxx_type):

    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type
    if (isinstance(cxx_type, bc.ElaboratedType)):
        cxx_type = cxx_type.namedType

    if isinstance(cxx_type, bc.LValueReferenceType):
        is_const = cxx_type.isConstQualified
        cxx_type = cxx_type.pointeeType
        if (isinstance(cxx_type, bc.ElaboratedType)):
            is_const = is_const or cxx_type.isConstQualified
            cxx_type = cxx_type.namedType
        is_const = is_const or cxx_type.isConstQualified
        # print cxx_type, is_const
        if (isinstance(cxx_type, bc.TemplateSpecializationType) and
                is_const and (
                    bc.is_std_vector(cxx_type.sugar.decl)) and
                isinstance(cxx_type.args[0].type, bc.BuiltinType)):
            return cxx_type.args[0].type.spelling
        else:
            return False
    # if isinstance(cxx_type, bc.TemplateSpecializationType):
    #     print "-" * 80
    #     print cxx_type
    #     print (cxx_type.sugar.decl.path == 'std::vector' or
    #      cxx_type.sugar.decl.path == 'std::__1::vector')
    #     print isinstance(cxx_type.args[0].type, bc.BuiltinType)
    #     print "-" * 80

    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
        (bc.is_std_vector(cxx_type.sugar.decl)) and
            isinstance(cxx_type.args[0].type, bc.BuiltinType)):
        return cxx_type.args[0].type.spelling
    return False


class ArgConverter(arg_converter.ArgConverter):
    def dumpCCallPre(self, source):
        arg = self.getArgName()
        ct = isBuiltinVector(self.arg.type)
        otype = ct
        source << 'std::vector<%s> %s_;' % (ct, arg)
        f = bw.objc.ForEach("NSNumber *i", arg)
        f << '%s_.push_back([i %sValue]);' % (arg, otype)
        source << f

    def getCCall(self):
        return self.getArgName() + '_'


class ReturnConverter(return_converter.ReturnConverter):
    def dumpCReturn(self, source):
        ct = isBuiltinVector(self.cxx_type)
        otype = ct
        source << ('NSMutableArray *_ar = [NSMutableArray array];')
        f = bw.cxx.ForEach("auto &&_p", "_ret_")
        s = "[NSNumber numberWith%s:_p]" % (otype[0].upper() + otype[1:])
        f << ('[_ar addObject:%s];' % s)
        source << f
        source << "return _ar;"


class BuiltinVectorPlugin(plugin.Plugin):
    def resolveFilter(self, decl_or_type):
        return isBuiltinVector(decl_or_type)

    def resolveClass(self, decl_or_type):
        postfix = ''
        if self.settings['lightweight_generics']:
            # elem_type = isBuiltinVector(decl_or_type)
            # postfix = '<%s>' % elem_type
            postfix = '<NSNumber*>'
        return True, "NSArray%s" % postfix

    def converterFilter(self, *args):
        return isBuiltinVector(args[0])

    def getArgConverter(self, arg_decl, func_conv):
        return ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return ReturnConverter(self.creator, ret_type, func_conv)
