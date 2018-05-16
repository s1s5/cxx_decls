# coding: utf-8
from blueboss import common as bc


def eraseTypedef(t):
    if isinstance(t, bc.ElaboratedType):
        t = t.namedType
    if isinstance(t, bc.TypedefType):
        t = t.decl.underlyingType
    return t
