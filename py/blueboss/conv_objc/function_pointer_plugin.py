# coding: utf-8
import plugin
from blueboss import common as bc
import arg_converter


def isFunction(cxx_type):
    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type
    is_const = False
    if isinstance(cxx_type, bc.ElaboratedType):
        is_const = is_const or cxx_type.isConstQualified
        cxx_type = cxx_type.namedType
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
            (bc.is_std_function(cxx_type.sugar.decl))):
        # print("=" * 80)
        # cxx_type.show()
        # print("-" * 40)
        # cxx_type.args[0].show()
        # print("-" * 20)
        # cxx_type.args[0].type.show()
        # print("-" * 10)
        # cxx_type.args[0].type.returnType.show()
        # cxx_type.args[0].type.param_types.show()
        return True, cxx_type.args[0].type
    return False, cxx_type


class ArgConverter(arg_converter.ArgConverter):
    def __init__(self, *args, **kw):
        super(ArgConverter, self).__init__(*args, **kw)
        _, cxx_type = isFunction(self.arg)
        self.cxx_type = cxx_type

    def dumpCCallPre(self, source):
        return_type = self.creator.resolveClass(self.cxx_type.returnType)
        args = []
        for i in self.cxx_type.param_types:
            args.append(self.creator.resolveClass(i))

        def _type_str(x):
            if x[0]:
                return '{} *'.format(x[1])
            return x[1]

        fdecl = "{}(^{}_objc)({})".format(_type_str(return_type), self.getArgName(),
                                          ', '.join(_type_str(x) for x in args))

        source << "{0} = [{1} copy];".format(fdecl, self.getArgName())
        source << "auto {arg_name}_ = [{arg_name}_objc]({arg_string}){brace}".format(
            arg_name=self.getArgName(),
            arg_string=', '.join('auto arg{}'.format(x)
                                 for x in range(len(self.cxx_type.param_types))),
            brace='{')

        for param_idx, param_type in enumerate(self.cxx_type.param_types):
            c = self.creator.getReturnConverter(param_type, self)
            source << "%s objc_arg%d = [](auto x) {" % (c.getObjCType(), param_idx)
            c.dumpCCallPre(source)
            c.dumpCCall(source, 'x')
            c.dumpCCallPost(source)
            c.dumpCReturn(source)
            source << "}(arg%d);" % param_idx

        call_string = "{}_objc({})".format(
            self.getArgName(), ', '.join('objc_arg{}'.format(x)
                                         for x in range(len(self.cxx_type.param_types))))
        if (isinstance(self.cxx_type.returnType, bc.BuiltinType) and
                self.cxx_type.returnType.spelling == 'void'):
            source << "{};".format(call_string)
        else:
            source << "auto _ret = {};".format(call_string)
            ac = self.creator.getArgConverter(
                bc.ParmVarDecl(name='_ret', type=self.cxx_type.returnType),
                self)
            ac.dumpCCallPre(source)
            source << "auto _ret_c = {};".format(ac.getCCall())
            ac.dumpCCallPost(source)
            source << "return _ret_c;"
        source << "};"

    def getCCall(self):
        return self.getArgName() + '_'


class FunctionPointerPlugin(plugin.Plugin):

    def resolveFilter(self, decl_or_type):
        flag, cxx_type = isFunction(decl_or_type)
        return flag

    def resolveClass(self, decl_or_type):
        flag, cxx_type = isFunction(decl_or_type)
        if not flag:
            return False, None

        return_type = self.creator.resolveClass(cxx_type.returnType)
        args = []
        for i in cxx_type.param_types:
            args.append(self.creator.resolveClass(i))

        def _type_str(x):
            if x[0]:
                return '{} *'.format(x[1])
            return x[1]

        return None, "{}(^)({})".format(_type_str(return_type), ', '.join(_type_str(x) for x in args))

    def converterFilter(self, *args):
        flag, cxx_type = isFunction(args[0])
        return flag

    def getArgConverter(self, arg_decl, func_conv):
        return ArgConverter(self.creator, arg_decl, func_conv)
