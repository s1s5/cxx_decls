# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import plugin
import bridge
import class_vector_plugin
import builtin_vector_plugin


def isBuiltinType(t):
    if isinstance(t, bc.ParmVarDecl):
        t = t.type
    if isinstance(t, bc.LValueReferenceType):
        t = t.pointeeType
    t = t.elementType
    return isinstance(t, bc.BuiltinType)


def getBuiltinType(t):
    if isinstance(t, bc.ParmVarDecl):
        t = t.type
    if isinstance(t, bc.LValueReferenceType):
        t = t.pointeeType
    t = t.elementType
    if not isinstance(t, bc.BuiltinType):
        t = None
    return t


def isConst(t):
    is_const = False
    if isinstance(t, bc.ParmVarDecl):
        t = t.type
    is_const = is_const or t.isConstQualified
    if isinstance(t, bc.LValueReferenceType):
        is_const = is_const or t.isConstQualified
        t = t.pointeeType
    is_const = is_const or t.isConstQualified
    t = t.elementType
    is_const = is_const or t.isConstQualified
    return is_const


def getArraySize(t):
    if isinstance(t, bc.ParmVarDecl):
        t = t.type
    if isinstance(t, bc.LValueReferenceType):
        t = t.pointeeType
    return t.size


class ReturnConverter(class_vector_plugin.VectorReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isBuiltinType(cxx_type):
            return klass(creator, cxx_type, func_conv)

    def getElemType(self):
        return bc.LValueReferenceType(getBuiltinType(self.cxx_type))

    def dumpJniCallPost(self, source):
        size = getArraySize(self.cxx_type)
        source << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
        source << ('jobjectArray _ret_ = '
                   '_jenv->NewObjectArray(%d, bbcls, nullptr);' % size)
        f = bw.cxx.For("unsigned int _i = 0", "_i < %d" % size, "_i++")
        f << "jobject _bb_ = %s(_jenv);" % bridge.CREATE_FUNC_NAME
        f << '%s *p = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                 bridge.STRUCT_NAME)
        f << '    _jenv->GetDirectBufferAddress(_bb_));'
        f << 'p->p = &(_ret_vec[_i]);'
        f << '_jenv->SetObjectArrayElement(_ret_, _i, _bb_);'
        f << '_jenv->DeleteLocalRef(_bb_);'
        source << f


class ConstReturnConverter(builtin_vector_plugin.VectorReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isBuiltinType(cxx_type) and isConst(cxx_type):
            return klass(creator, cxx_type, func_conv)

    def _getBuiltinType(self, type_):
        return getBuiltinType(type_)

    def dumpJniCallPost(self, source):
        size = getArraySize(self.cxx_type)
        source << ('j%sArray _ret_ = _jenv->New%sArray(%d);' %
                   (self.prim, self.aprim, size))
        source << ('_jenv->Set%sArrayRegion('
                   '_ret_, 0, %d, _ret_tmp);' %
                   (self.aprim, size))


class BuiltinConstantArrayPlugin(plugin.Plugin):
    def converterFilter(self, *args):
        decl_or_type = args[0]
        if isinstance(decl_or_type, bc.ParmVarDecl):
            decl_or_type = decl_or_type.type
        if isinstance(decl_or_type, bc.LValueReferenceType):
            decl_or_type = decl_or_type.pointeeType
        return isinstance(decl_or_type, bc.ConstantArrayType)

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getReturnConverter(self, ret_type, func_conv):
        l = [ConstReturnConverter.check, ReturnConverter.check, ]
        return self.__getConverter(l, ret_type, func_conv)
