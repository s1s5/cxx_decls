# coding: utf-8
from blueboss import common as bc
import plugin
import jpath
import builtin_plugin
import arg_converter
import return_converter


def isBuiltinVector(cxx_type):
    if isinstance(cxx_type, bc.LValueReferenceType):
        is_const = cxx_type.isConstQualified
        cxx_type = cxx_type.pointeeType
        if (isinstance(cxx_type, bc.ElaboratedType)):
            is_const = is_const or cxx_type.isConstQualified
            cxx_type = cxx_type.namedType
        is_const = is_const or cxx_type.isConstQualified
        # print cxx_type, is_const
        if (isinstance(cxx_type, bc.TemplateSpecializationType) and
                is_const and cxx_type.sugar.decl.path == 'std::vector' and
                isinstance(cxx_type.args[0].type, bc.BuiltinType)):
            return True
        else:
            return False
    if (isinstance(cxx_type, bc.ElaboratedType)):
        cxx_type = cxx_type.namedType
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
            cxx_type.sugar.decl.path == 'std::vector' and
            isinstance(cxx_type.args[0].type, bc.BuiltinType)):
        return True
    return False


def getBuiltinType(cxx_type):
    if isinstance(cxx_type, bc.LValueReferenceType):
        cxx_type = cxx_type.pointeeType
    if (isinstance(cxx_type, bc.ElaboratedType)):
        cxx_type = cxx_type.namedType
    return cxx_type.args[0].type


class VectorArgConverter(arg_converter.ArgConverter):
    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        if isBuiltinVector(cxx_type):
            return klass(creator, arg, func_conv)

    def __init__(self, creator, arg, func_conv):
        self.prim = builtin_plugin.getJavaBuiltinType(
            creator.target_info, self._getBuiltinType(arg.type))
        self.aprim = self.prim[0].upper() + self.prim[1:]
        super(VectorArgConverter, self).__init__(creator, arg, func_conv)

    def _getBuiltinType(self, type_):
        return getBuiltinType(type_)

    def imports(self):
        return []

    def getJInterface(self):
        return jpath.JPath((self.prim, ))

    def getJClass(self):
        return jpath.JPath((self.prim, ))

    def getJavaPubType(self):
        return super(VectorArgConverter, self).getJavaPubType() + ' []'

    def getJavaPrivType(self):
        return super(VectorArgConverter, self).getJavaPrivType() + ' []'

    def getJniType(self):
        return 'j%sArray' % self.prim

    def dumpJniCallPre(self, source):
        source << ('j%s* %s_elems_ = _jenv->Get%sArrayElements(%s, NULL);' %
                   (self.prim, self.getArgName(), self.aprim,
                    self.getArgName()))
        source << ('jsize %s_elems_length_ = _jenv->GetArrayLength(%s);' %
                   (self.getArgName(), self.getArgName()))
        source << ('std::vector<%s> %s_elems_vec_('
                   '%s_elems_, %s_elems_ + %s_elems_length_);' %
                   (self.prim,
                    self.getArgName(),
                    self.getArgName(),
                    self.getArgName(),
                    self.getArgName(), ))

    def getJniCall(self):
        return '%s_elems_vec_' % self.getArgName()

    def dumpJniCallPost(self, source):
        commit_or_abort = "JNI_ABORT"
        source << ('_jenv->Release%sArrayElements(%s, %s_elems_, %s);' %
                   (self.aprim, self.getArgName(), self.getArgName(),
                    commit_or_abort))


class VectorReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isBuiltinVector(cxx_type):
            return klass(creator, cxx_type, func_conv)

    def __init__(self, creator, cxx_type, func_conv):
        self.prim = builtin_plugin.getJavaBuiltinType(
            creator.target_info, self._getBuiltinType(cxx_type))
        self.aprim = self.prim[0].upper() + self.prim[1:]
        super(VectorReturnConverter, self).__init__(creator, cxx_type,
                                                    func_conv)

    def _getBuiltinType(self, type_):
        return getBuiltinType(type_)

    def imports(self):
        return []

    def getJInterface(self):
        return jpath.JPath((self.prim, ))

    def getJClass(self):
        return jpath.JPath((self.prim, ))

    def getJavaPubType(self):
        return super(VectorReturnConverter, self).getJavaPubType() + ' []'

    def getJavaPrivType(self):
        return super(VectorReturnConverter, self).getJavaPrivType() + ' []'

    def getJniType(self):
        return 'j%sArray' % self.prim

    def dumpJniCall(self, source, call_string):
        source << ('auto _ret_tmp = %s;' % (call_string, ))

    def dumpJniCallPost(self, source):
        source << ('j%sArray _ret_ = _jenv->New%sArray(_ret_tmp.size());' %
                   (self.prim, self.aprim))
        source << ('_jenv->Set%sArrayRegion('
                   '_ret_, 0, _ret_tmp.size(), _ret_tmp.data());' % self.aprim)


class BuiltinVectorPlugin(plugin.Plugin):
    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getArgConverter(self, arg_decl, func_conv):
        l = [VectorArgConverter.check]
        return self.__getConverter(l, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        l = [VectorReturnConverter.check]
        return self.__getConverter(l, ret_type, func_conv)
