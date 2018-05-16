# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import base
import plugin
import bridge
import class_plugin
import arg_converter
import return_converter


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

    # print type(cxx_type), cxx_type
    # print (isinstance(cxx_type, bc.TemplateSpecializationType) and
    #         cxx_type.sugar.decl.path == 'std::vector')
    # print ((isinstance(cxx_type, bc.TemplateSpecializationType) and
    #         cxx_type.sugar.decl.path == 'std::vector' and
    #         isinstance(cxx_type.args[0].type, bc.RecordType)))
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
            cxx_type.sugar.decl.path == 'std::vector' and
        isinstance(base.eraseTypedef(cxx_type.args[0].type),
                   bc.RecordType)):
        is_const = is_const or cxx_type.isConstQualified
        if is_lvalue and not is_const:
            return False
        return base.eraseTypedef(cxx_type.args[0].type), is_const, is_lvalue
    return False


def getVectorElem(cxx_type):
    elem_type, is_const, _ = isVector(cxx_type)
    # is_const = False
    # if isinstance(cxx_type, bc.LValueReferenceType):
    #     is_const = is_const or cxx_type.isConstQualified
    #     cxx_type = cxx_type.pointeeType
    # if isinstance(cxx_type, bc.ElaboratedType):
    #     is_const = is_const or cxx_type.isConstQualified
    #     cxx_type = cxx_type.namedType
    # is_const = is_const or cxx_type.isConstQualified
    t = bc.RecordType(elem_type.decl, isConstQualified=is_const)
    return t


class VectorArgConverter(arg_converter.ArgConverter):
    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        # if isinstance(cxx_type, bc.LValueReferenceType):
        #     return False
        if isVector(cxx_type):
            return klass(creator, arg, func_conv)

    def getJClass(self):
        e = getVectorElem(self.arg.type)
        e.isConstQualified = True
        return self.creator.getInterface(e)

    def getJavaPubType(self):
        return super(VectorArgConverter, self).getJavaPubType() + ' []'

    def getJavaPrivType(self):
        return 'ByteBuffer []'

    def dumpJavaPrivCallPre(self, source):
        source << ("ByteBuffer [] _bb_%s = new ByteBuffer[%s.length];" %
                   (self.getArgName(), self.getArgName()))
        f = bw.java.For("int _i_ = 0",
                        "_i_ < _bb_%s.length" % self.getArgName(), "_i_++")
        f << "_bb_%s[_i_] = %s[_i_].__getBB();" % (self.getArgName(),
                                                   self.getArgName(), )
        source << f

    def getJavaPrivCall(self):
        return "_bb_%s" % self.getArgName()

    def getJniType(self):
        return 'jobjectArray'

    def dumpJniCallPre(self, source):
        an = self.getArgName()
        source << ('jsize %s_elems_length_ = _jenv->GetArrayLength(%s);' %
                   (an, an))
        elem_type, is_const, is_lvalue = isVector(self.arg)
        if is_lvalue:
            source << ('std::vector<%s> %s_vec_;' % (elem_type.cname(), an))
        else:
            source << ('%s %s_vec_;' % (self.arg.type.cname(), an))

        f = bw.cxx.For("jsize _i = 0", "_i < %s_elems_length_" % an, "_i++")
        f << ('jobject _jobj = _jenv->GetObjectArrayElement(%s, _i);' % an)
        f << ('%s_vec_.push_back(*%s(_jenv, _jobj));' %
              (an, class_plugin.declGetInstanceFuncName(getVectorElem(
                  self.arg.type).decl)))
        f << ('_jenv->DeleteLocalRef(_jobj);')

        source << f

    def getJniCall(self):
        return '%s_vec_' % self.getArgName()

    def dumpJniCallPost(self, source):
        pass


class VectorReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isVector(cxx_type):
            return klass(creator, cxx_type, func_conv)

    def getElemType(self):
        return getVectorElem(self.cxx_type)

    def getJInterface(self):
        return self.creator.getInterface(self.getElemType())

    def getJClass(self):
        return self.creator.getClass(self.getElemType())

    def getJavaPubType(self):
        return super(VectorReturnConverter, self).getJavaPubType() + ' []'

    def getJavaPrivType(self):
        return 'ByteBuffer []'

    def dumpJavaPrivCall(self, source, call_string):
        source << ('%s _ret_vec = %s;' % (self.getJavaPrivType(), call_string))

    def dumpJavaPrivCallPost(self, source):
        jcls = self.jclass.getClassPath()
        ref = "(Object)this"
        if self.func_conv.isStatic():
            ref = "new Object()"
        # ref = "null"
        source << ('%s _ret_ = new %s[_ret_vec.length];' %
                   (self.getJavaPubType(),
                    super(VectorReturnConverter, self).getJavaPubType(), ))
        f = bw.java.For("int _i_ = 0", "_i_ < _ret_vec.length", "_i_++")
        f << ("_ret_[_i_] = new %s(_ret_vec[_i_], %s);" % (jcls, ref))
        source << f

    def getJniType(self):
        return 'jobjectArray'

    def dumpJniCall(self, source, call_string):
        source << ('auto _ret_vec = %s;' % (call_string, ))

    def dumpJniCallPost(self, source):
        is_ref = isinstance(self.cxx_type, bc.LValueReferenceType)
        source << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
        source << ('jobjectArray _ret_ = '
                   '_jenv->NewObjectArray(_ret_vec.size(), bbcls, nullptr);')
        f = bw.cxx.For("unsigned int _i = 0", "_i < _ret_vec.size()", "_i++")
        f << 'jobject _bb_ = %s(_jenv);' % class_plugin.declCreateFuncName(
            self.getElemType().decl)
        f << '%s *_p_ = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                   bridge.STRUCT_NAME)
        f << '    _jenv->GetDirectBufferAddress(_bb_));'
        if False and is_ref:
            f << ('_p_->p = const_cast<%s*>(&(_ret_vec[_i]));' %
                  (self.getElemType().decl.path, ))
        else:
            f << ('_p_->p = new %s(_ret_vec[_i]);' %
                  (self.getElemType().decl.path, ))
        f << '_jenv->SetObjectArrayElement(_ret_, _i, _bb_);'
        f << '_jenv->DeleteLocalRef(_bb_);'
        source << f


class ClassVectorPlugin(plugin.Plugin):
    def depends(self):
        return [class_plugin.ClassPlugin]

    def resolveFilter(self, decl_or_type):
        return isVector(decl_or_type)

    def resolveInterfacePath(self, decl_or_type):
        el = getVectorElem(decl_or_type)
        return self.creator.resolveInterfacePath(el)

    def resolveClassPath(self, decl_or_type):
        el = getVectorElem(decl_or_type)
        return self.creator.resolveClassPath(el)

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
