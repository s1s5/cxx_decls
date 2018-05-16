# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import base
import plugin
import arg_converter
import return_converter
import string_plugin


def isVector(cxx_type):
    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type
    is_lvalue = False
    is_const = False
    if isinstance(cxx_type, bc.ElaboratedType):
        is_const = is_const or cxx_type.isConstQualified
        cxx_type = cxx_type.namedType

    if isinstance(cxx_type, bc.LValueReferenceType):
        is_lvalue = True
        is_const = is_const or cxx_type.isConstQualified
        cxx_type = cxx_type.pointeeType

    if isinstance(cxx_type, bc.ElaboratedType):
        is_const = is_const or cxx_type.isConstQualified
        cxx_type = cxx_type.namedType

    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
        (cxx_type.sugar.decl.path == 'std::vector' or
         cxx_type.sugar.decl.path == 'std::__1::vector')):
        is_const = is_const or cxx_type.isConstQualified
        if is_lvalue and not is_const:
            return False, None, None
        t = base.eraseTypedef(cxx_type.args[0].type)
        return string_plugin.getString(t), is_const, is_lvalue
    return False, None, None


class ArgConverter(arg_converter.ArgConverter):
    def __init__(self, *args, **kw):
        super(ArgConverter, self).__init__(*args, **kw)
        d, ic, il = isVector(self.arg)
        self.d = d
        self.ic = ic
        self.il = il
        self.c = self.creator.getArgConverter(
            bc.ParmVarDecl("_e_", self.d), self.func_conv)

    def dumpCCallPre(self, source):
        arg = self.getArgName()
        source << 'std::vector<%s> %s_;' % (self.d.cname(), arg)
        f = bw.objc.For("unsigned int _i_ = 0",
                        "_i_ < [%s count]" % arg, "_i_++")
        _, n = self.creator.resolveClass(self.d)
        f << "%s *_e_ = [%s objectAtIndex:_i_];" % (n, arg)
        self.c.dumpCCallPre(f)
        f << '%s_.push_back(%s);' % (arg, self.c.getCCall())
        self.c.dumpCCallPost(f)
        source << f

    def getCCall(self):
        return self.getArgName() + '_'


class ReturnConverter(return_converter.ReturnConverter):
    def __init__(self, *args, **kw):
        super(ReturnConverter, self).__init__(*args, **kw)
        d, ic, il = isVector(self.cxx_type)
        self.d = d
        self.ic = ic
        self.il = il
        self.c = self.creator.getReturnConverter(self.d,
                                                 self.func_conv)

    def dumpCReturn(self, source):
        l = bw.cxx.Lambda("_rf_", ["const %s& c" % self.d.cname(), ])
        self.c.dumpCCallPre(l)
        self.c.dumpCCall(l, 'c')
        self.c.dumpCReturn(l)
        self.c.dumpCCallPost(l)
        source << l
        source << ('NSMutableArray *_ar = [NSMutableArray array];')
        f = bw.cxx.ForEach("auto &&_p", "_ret_")
        f << "[_ar addObject:_rf_(_p)];"
        source << f
        source << "return _ar;"


class StringVectorPlugin(plugin.Plugin):
    def resolveFilter(self, decl_or_type):
        f, _, _ = isVector(decl_or_type)
        return f

    def resolveClass(self, decl_or_type):
        postfix = ''
        if self.settings['lightweight_generics']:
            postfix = '<NSString*>'
        return True, "NSArray%s" % postfix

    def converterFilter(self, *args):
        f, _, _ = isVector(args[0])
        return f

    def getArgConverter(self, arg_decl, func_conv):
        return ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        return ReturnConverter(self.creator, ret_type, func_conv)
