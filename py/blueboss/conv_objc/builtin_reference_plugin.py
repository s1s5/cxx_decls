# coding: utf-8
from blueboss import common as bc
import plugin
import arg_converter
import return_converter


class ArgConverter(arg_converter.ArgConverter):

    def getCCall(self):
        t = self.arg.type
        if isinstance(t, bc.PointerType):
            return self.getArgName()
        return '(*(%s))' % self.getArgName()


class ReturnConverter(return_converter.ReturnConverter):

    def dumpCReturn(self, source):
        if isinstance(self.cxx_type, bc.PointerType):
            source << "return _ret_;"
        else:
            source << "return &_ret_;"


class BuiltinReferencePlugin(plugin.Plugin):

    def resolveFilter(self, decl_or_type):
        if isinstance(decl_or_type, bc.ParmVarDecl):
            decl_or_type = decl_or_type.type
        if not (isinstance(decl_or_type, bc.LValueReferenceType) or
                isinstance(decl_or_type, bc.PointerType)):
            return
        decl_or_type = decl_or_type.pointeeType
        return isinstance(decl_or_type, bc.BuiltinType)

    def converterFilter(self, *args):
        return self.resolveFilter(args[0])

    def resolveClass(self, decl_or_type):
        is_const = decl_or_type.isConstQualified
        decl_or_type = decl_or_type.pointeeType
        if decl_or_type.spelling == 'bool':
            return None, "BOOL *"
        spelling = decl_or_type.spelling
        if is_const or decl_or_type.isConstQualified:
            spelling = 'const ' + spelling
        return None, spelling + ' *'

    def getArgConverter(self, arg_decl, func_conv):
        return ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return ReturnConverter(
            self.creator, ret_type, func_conv)
