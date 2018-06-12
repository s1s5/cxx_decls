# coding: utf-8
from blueboss import common as bc
import plugin


def _get(decl_or_type):
    is_const = decl_or_type.isConstQualified
    if isinstance(decl_or_type, bc.ElaboratedType):
        decl_or_type = decl_or_type.namedType
        is_const = is_const | decl_or_type.isConstQualified
    decl_or_type = decl_or_type.decl.underlyingType
    is_const = decl_or_type.isConstQualified
    return decl_or_type, is_const


class TypedefPlugin(plugin.Plugin):
    def resolveFilter(self, decl_or_type):
        if isinstance(decl_or_type, bc.ElaboratedType):
            decl_or_type = decl_or_type.namedType
        if isinstance(decl_or_type, bc.TypedefType):
            return True

    def resolveClass(self, decl_or_type):
        return self.creator.resolveClass(_get(decl_or_type)[0])

    def getArgConverter(self, arg_decl, func_decl):
        cxx_type = arg_decl.type
        is_l = False
        is_c = cxx_type.isConstQualified
        if isinstance(cxx_type, bc.LValueReferenceType):
            cxx_type = cxx_type.pointeeType
            is_l = True
            is_c = is_c or cxx_type.isConstQualified
        if isinstance(cxx_type, bc.ElaboratedType):
            cxx_type = cxx_type.namedType
            is_c = is_c or cxx_type.isConstQualified
        # print arg_decl, isinstance(
        # arg_decl.type, bc.TypedefType), type(arg_decl.type)
        if not isinstance(cxx_type, bc.TypedefType):
            return

        if is_l:
            t, c = _get(cxx_type)
            t = t.shallowCopy()
            t.isConstQualified = t.isConstQualified or is_c or c
            cxx_type = bc.LValueReferenceType(t)
        else:
            t, c = _get(cxx_type)
            t = t.shallowCopy()
            t.isConstQualified = t.isConstQualified or is_c or c
            cxx_type = t

        arg_decl = bc.ParmVarDecl(arg_decl.name,
                                  cxx_type,
                                  hasDefaultArg=arg_decl.hasDefaultArg)
        return self.creator.getArgConverter(arg_decl, func_decl)

    def getReturnConverter(self, ret_type, func_decl):
        is_c = False
        if isinstance(ret_type, bc.ElaboratedType):
            ret_type = ret_type.namedType
            is_c = ret_type.isConstQualified
        if not isinstance(ret_type, bc.TypedefType):
            return
        t, c = _get(ret_type)
        t = t.shallowCopy()
        t.isConstQualified = t.isConstQualified or is_c or c
        return self.creator.getReturnConverter(t, func_decl)
