# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import base
import plugin
import jpath
import string_plugin
# import builtin_plugin
import arg_converter
import return_converter


def isVector(cxx_type):
    # print "-" * 100
    # print type(cxx_type), cxx_type
    if isinstance(cxx_type, bc.LValueReferenceType):
        cxx_type = cxx_type.pointeeType
    if isinstance(cxx_type, bc.ElaboratedType):
        cxx_type = cxx_type.namedType
    # print type(cxx_type), cxx_type
    # print (isinstance(cxx_type, bc.TemplateSpecializationType) and
    #         cxx_type.sugar.decl.path == 'std::vector')
    # print ((isinstance(cxx_type, bc.TemplateSpecializationType) and
    #         cxx_type.sugar.decl.path == 'std::vector' and
    #         isinstance(cxx_type.args[0].type, bc.RecordType)))
    # if isinstance(cxx_type, bc.TemplateSpecializationType):
    #     cxx_type.show()
    # if (isinstance(cxx_type, bc.TemplateSpecializationType) and
    #         cxx_type.sugar.decl.path == 'std::vector'):
    #     print "-" * 100
    #     print cxx_type
    #     print cxx_type.args[0].type
    #     print string_plugin.isString(cxx_type.args[0].type)
    #     print base.eraseTypedef(cxx_type.args[0].type)
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
            cxx_type.sugar.decl.path == 'std::vector' and
            string_plugin.isString(
                base.eraseTypedef(cxx_type.args[0].type))):
        return True
    return False


def getVectorElem(cxx_type):
    if isinstance(cxx_type, bc.LValueReferenceType):
        cxx_type = cxx_type.pointeeType
    if isinstance(cxx_type, bc.ElaboratedType):
        cxx_type = cxx_type.namedType
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
            cxx_type.sugar.decl.path == 'std::vector' and
            string_plugin.isString(
                base.eraseTypedef(cxx_type.args[0].type))):
        return cxx_type.args[0].type


class VectorArgConverter(arg_converter.ArgConverter):
    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        # print cxx_type, ">" * 80
        # f = isVector(cxx_type)
        # print f
        # print "<" * 80
        if isVector(cxx_type):
            # print "--" * 100
            # print getVectorElem(cxx_type)
            creator.getReturnConverter(getVectorElem(cxx_type), func_conv)
            return klass(creator, arg, func_conv)

    def imports(self):
        return []

    def getJInterface(self):
        return jpath.String

    def getJClass(self):
        return jpath.String

    def getJavaPubType(self):
        return super(VectorArgConverter, self).getJavaPubType() + ' []'

    def getJavaPrivType(self):
        return super(VectorArgConverter, self).getJavaPrivType() + ' []'

    def getJniType(self):
        return 'jobjectArray'

    def dumpJniCallPre(self, source):
        an = self.getArgName()
        source << ('jsize %s_elems_length_ = _jenv->GetArrayLength(%s);' %
                   (an, an))
        source << ('std::vector<std::string> %s_vec_;' % (an))
        f = bw.cxx.For("jsize _i = 0", "_i < %s_elems_length_" % an, "_i++")
        f << ('jstring _s_ = (jstring)'
              '_jenv->GetObjectArrayElement(%s, _i);' % an)
        f << ('%s_vec_.push_back(%s(_jenv, _s_));' %
              (an, string_plugin.J2C_FUNC))
        f << ('_jenv->DeleteLocalRef(_s_);')
        source << f

    def getJniCall(self):
        return '%s_vec_' % self.getArgName()


class VectorReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isVector(cxx_type):
            creator.getReturnConverter(getVectorElem(cxx_type), func_conv)
            return klass(creator, cxx_type, func_conv)

    def imports(self):
        return []

    def getJInterface(self):
        return jpath.String

    def getJClass(self):
        return jpath.String

    def getJavaPubType(self):
        return super(VectorReturnConverter, self).getJavaPubType() + ' []'

    def getJavaPrivType(self):
        return super(VectorReturnConverter, self).getJavaPrivType() + ' []'

    def getJniType(self):
        return 'jobjectArray'

    def dumpJniCall(self, source, call_string):
        source << ('auto _ret_tmp = %s;' % (call_string, ))

    def dumpJniCallPost(self, source):
        source << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
        source << ('jobjectArray _ret_ = (jobjectArray)_jenv->NewObjectArray('
                   '_ret_tmp.size(), _jenv->FindClass("java/lang/String"), '
                   '_jenv->NewStringUTF(""));')
        f = bw.cxx.For("unsigned int _i = 0", "_i < _ret_tmp.size()", "_i++")
        f << 'jstring _s_ = %s(_jenv, _ret_tmp[_i]);' % string_plugin.C2J_FUNC
        f << '_jenv->SetObjectArrayElement(_ret_, _i, _s_);'
        f << '_jenv->DeleteLocalRef(_s_);'
        source << f


class StringVectorPlugin(plugin.Plugin):
    def depends(self):
        return [string_plugin.StringPlugin]

    def resolveFilter(self, decl_or_type):
        return isVector(decl_or_type)

    def resolveInterfacePath(self, decl_or_type):
        return self.creator.resolveInterfacePath(getVectorElem(decl_or_type))

    def resolveClassPath(self, decl_or_type):
        return self.creator.resolveClassPath(getVectorElem(decl_or_type))

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
