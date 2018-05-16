# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import plugin
import bridge
import class_vector_plugin


def parseType(decl_or_type):
    def _update(c, t):
        if hasattr(t, 'isConstQualified'):
            c = c or t.isConstQualified
        return c

    is_const = False
    if isinstance(decl_or_type, bc.ParmVarDecl):
        decl_or_type = decl_or_type.type
    if isinstance(decl_or_type, bc.LValueReferenceType):
        is_const = _update(is_const, decl_or_type)
        decl_or_type = decl_or_type.pointeeType
    is_const = _update(is_const, decl_or_type)
    if not isinstance(decl_or_type, bc.ConstantArrayType):
        return None, False, 0
    is_const = _update(is_const, decl_or_type)
    return decl_or_type.elementType, is_const, decl_or_type.size


class ReturnConverter(class_vector_plugin.VectorReturnConverter):

    def getElemType(self):
        et, is_const, size = parseType(self.cxx_type)
        return bc.LValueReferenceType(et, isConstQualified=is_const)

    def dumpJniCallPost(self, source):
        et, is_const, size = parseType(self.cxx_type)
        et = self.getElemType()
        print et, is_const, size
        source << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
        source << ('jobjectArray _ret_ = '
                   '_jenv->NewObjectArray(%d, bbcls, nullptr);' % size)
        f = bw.cxx.For("unsigned int _i = 0", "_i < %d" % size, "_i++")
        # f << 'jobject _bb_ = %s(_jenv);' % class_plugin.declCreateFuncName(
        #     et)
        f << '%s *_p_ = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                   bridge.STRUCT_NAME)
        f << '    _jenv->GetDirectBufferAddress(_bb_));'
        f << ('_p_->p = (&(_ret_vec[_i]));')
        # f << ('_p_->p = (&(_ret_vec[_i]));' %
        #       (self.getElemType().decl.path, ))
        f << '_jenv->SetObjectArrayElement(_ret_, _i, _bb_);'
        f << '_jenv->DeleteLocalRef(_bb_);'
        source << f


class Plugin(plugin.Plugin):
    def converterFilter(self, *args):
        decl, _, _ = parseType(args[0])
        return decl is not None

    def getReturnConverter(self, ret_type, func_conv):
        return ReturnConverter(self.creator, ret_type, func_conv)
