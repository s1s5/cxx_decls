# coding: utf-8
from blueboss import common as bc


def getName(creator, decl):
    # l = decl.path.split('::')
    # if len(l) == 1:
    #     return creator.settings['global_prefix'] + l[0]
    # else:
    #     return l[-1]
    l = '_'.join(decl.path.split('::'))
    return creator.settings['global_prefix'] + l


def eraseTypedef(t):
    if isinstance(t, bc.ElaboratedType):
        t = t.namedType
    if isinstance(t, bc.TypedefType):
        t = t.decl.underlyingType
    return t
