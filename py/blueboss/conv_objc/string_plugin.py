# coding: utf-8
import plugin
from blueboss import common as bc
import arg_converter
import return_converter


CONST_CHAR_PTR = 1
CXX_STRING = 2


def isString(cxx_type):
    def _update(c, t):
        if hasattr(t, 'isConstQualified'):
            c = c or t.isConstQualified
        return c
    is_const = False

    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type
    if isinstance(cxx_type, bc.ElaboratedType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.namedType
    if isinstance(cxx_type, bc.TypedefType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.decl.underlyingType
    if (isinstance(cxx_type, bc.PointerType) and
            isinstance(cxx_type.pointeeType, bc.BuiltinType) and
            cxx_type.pointeeType.spelling == 'char' and
            cxx_type.pointeeType.isConstQualified):
        return CONST_CHAR_PTR
    elif (isinstance(cxx_type, bc.TemplateSpecializationType) and
          isinstance(cxx_type.sugar, bc.RecordType) and
          (cxx_type.sugar.decl.path == 'std::basic_string' or
           cxx_type.sugar.decl.path == 'std::__1::basic_string') and
          len(cxx_type.args) >= 1 and
          isinstance(cxx_type.args[0].type, bc.BuiltinType) and
          (cxx_type.args[0].type.spelling == 'char' or
           cxx_type.args[0].type.spelling == 'unsigned char')):
        return CXX_STRING
    elif isinstance(cxx_type, bc.LValueReferenceType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.pointeeType
        if isinstance(cxx_type, bc.ElaboratedType):
            is_const = _update(is_const, cxx_type)
            cxx_type = cxx_type.namedType
        if isinstance(cxx_type, bc.TypedefType):
            is_const = _update(is_const, cxx_type)
            cxx_type = cxx_type.decl.underlyingType
        is_const = _update(is_const, cxx_type)
        a = isString(cxx_type)
        _, isc = parseString(cxx_type)
        # if (isc or is_const) and a:
        if a:
            return CXX_STRING
    return False


def getString(cxx_type):
    def _update(c, t):
        if hasattr(t, 'isConstQualified'):
            c = c or t.isConstQualified
        return c
    is_const = False

    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type
    if isinstance(cxx_type, bc.ElaboratedType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.namedType
    if isinstance(cxx_type, bc.TypedefType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.decl.underlyingType
    if (isinstance(cxx_type, bc.PointerType) and
            isinstance(cxx_type.pointeeType, bc.BuiltinType) and
            cxx_type.pointeeType.spelling == 'char' and
            cxx_type.pointeeType.isConstQualified):
        return cxx_type
    elif (isinstance(cxx_type, bc.TemplateSpecializationType) and
          isinstance(cxx_type.sugar, bc.RecordType) and
          (cxx_type.sugar.decl.path == 'std::basic_string' or
           cxx_type.sugar.decl.path == 'std::__1::basic_string') and
          len(cxx_type.args) >= 1 and
          isinstance(cxx_type.args[0].type, bc.BuiltinType) and
          (cxx_type.args[0].type.spelling == 'char' or
           cxx_type.args[0].type.spelling == 'unsigned char')):
        return cxx_type
    elif isinstance(cxx_type, bc.LValueReferenceType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.pointeeType
        if isinstance(cxx_type, bc.ElaboratedType):
            is_const = _update(is_const, cxx_type)
            cxx_type = cxx_type.namedType
        if isinstance(cxx_type, bc.TypedefType):
            is_const = _update(is_const, cxx_type)
            cxx_type = cxx_type.decl.underlyingType
        is_const = _update(is_const, cxx_type)
        a = getString(cxx_type)
        _, isc = parseString(cxx_type)
        # if (isc or is_const) and a:
        if a:
            return a
    return False


def parseString(cxx_type):
    def _update(c, t):
        if hasattr(t, 'isConstQualified'):
            c = c or t.isConstQualified
        return c

    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type

    is_const = False
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
        isinstance(cxx_type.sugar, bc.RecordType) and
        (cxx_type.sugar.decl.path == 'std::basic_string' or
         cxx_type.sugar.decl.path == 'std::__1::basic_string')and
        len(cxx_type.args) >= 1 and
        isinstance(cxx_type.args[0].type, bc.BuiltinType) and
            cxx_type.args[0].type.spelling == 'char'):
        is_const = _update(is_const, cxx_type)
        return cxx_type, is_const
    elif isinstance(cxx_type, bc.LValueReferenceType):
        cxx_type = cxx_type.pointeeType
        is_const = _update(is_const, cxx_type)
        if isinstance(cxx_type, bc.ElaboratedType):
            cxx_type = cxx_type.namedType
            is_const = _update(is_const, cxx_type)
        if isinstance(cxx_type, bc.TypedefType):
            cxx_type = cxx_type.decl.underlyingType
            is_const = _update(is_const, cxx_type)
        t, is_c = parseString(cxx_type)
        return t, is_c or is_const
    return None, False


class StringArgConverter(arg_converter.ArgConverter):
    def dumpCCallPre(self, source):
        source << "std::string %s_str_ = std::string([%s UTF8String]);" % (
            self.getArgName(),
            self.getArgName(), )

    def getCCall(self):
        s = '%s_str_' % self.getArgName()
        if isString(self.arg) == CONST_CHAR_PTR:
            s += ".c_str()"
        return s


class StringReturnConverter(return_converter.ReturnConverter):
    def dumpCReturn(self, source):
        s = "_ret_"
        if isString(self.cxx_type) == CXX_STRING:
            s += ".c_str()"
        source << "return [NSString stringWithUTF8String:%s];" % s


class StringPlugin(plugin.Plugin):
    def linkStart(self):
        self.flag = False

    def resolveFilter(self, decl_or_type):
        return isString(decl_or_type)

    def resolveClass(self, decl_or_type):
        return True, "NSString"

    def converterFilter(self, *args):
        return isString(args[0])

    def getArgConverter(self, arg_decl, func_conv):
        return StringArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return StringReturnConverter(self.creator, ret_type, func_conv)
