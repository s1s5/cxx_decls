# coding: utf-8
from blueboss import common as bc
import plugin
import arg_converter
import return_converter


class VoidReturnConverter(return_converter.ReturnConverter):

    def dumpCCall(self, source, call_string):
        source << ('%s;' % (call_string, ))

    def dumpCReturn(self, source):
        pass


class BuiltinPlugin(plugin.Plugin):

    def resolveFilter(self, decl_or_type):
        if isinstance(decl_or_type, bc.ParmVarDecl):
            decl_or_type = decl_or_type.type
        if isinstance(decl_or_type, bc.SubstTemplateTypeParmType):
            # print "-" * 80
            # print decl_or_type.replacementType
            # print type(decl_or_type.replacementType)
            # decl_or_type.replacementType.show()
            decl_or_type = decl_or_type.replacementType
        if isinstance(decl_or_type, bc.LValueReferenceType):
            isc = decl_or_type.isConstQualified
            decl_or_type = decl_or_type.pointeeType
            isc = isc or decl_or_type.isConstQualified
            return isinstance(decl_or_type, bc.BuiltinType) and isc
        return isinstance(decl_or_type, bc.BuiltinType)

    def converterFilter(self, *args):
        return self.resolveFilter(args[0])

    def resolveClass(self, decl_or_type):
        if isinstance(decl_or_type, bc.SubstTemplateTypeParmType):
            decl_or_type = decl_or_type.replacementType
        if isinstance(decl_or_type, bc.LValueReferenceType):
            decl_or_type = decl_or_type.pointeeType
        if decl_or_type.spelling == 'bool':
            return None, "BOOL"
        return None, decl_or_type.spelling

    def getArgConverter(self, arg_decl, func_conv):
        return arg_converter.ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        klass = return_converter.ReturnConverter
        if isinstance(ret_type, bc.SubstTemplateTypeParmType):
            ret_type = ret_type.replacementType
        if isinstance(ret_type, bc.LValueReferenceType):
            ret_type = ret_type.pointeeType
        if ret_type.spelling == 'void':
            klass = VoidReturnConverter
        return klass(
            self.creator, ret_type, func_conv)
