# coding: utf-8
from blueboss import writer as bw
import plugin

STRUCT_NAME = "_bb_br_class"
CREATE_FUNC_NAME = "_bb_br_createInstance"
GET_FUNC_NAME = "_bb_br_getInstance"
DELETE_FUNC_NAME = "_bb_br_delete"


class BridgePlugin(plugin.Plugin):
    def jniHeader(self):
        sl = bw.cxx.StatementList()
        sl << self.generalClass()
        sl << self.createInstanceCodeBase()
        sl << self.getTemplateInstanceCode()
        sl << self.callDeleteCode()
        return sl

    def jniSource(self):
        pass

    def generalClass(self):
        st = bw.cxx.Struct(STRUCT_NAME)
        st << "int tag;"
        st << "void *p;"
        st << "void (*_delete)(void *);"
        return st

    def createInstanceCodeBase(self):
        func = bw.cxx.Func("jobject", CREATE_FUNC_NAME, ["JNIEnv *_jenv", ])
        func << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
        func << 'jmethodID mid = _jenv->GetStaticMethodID('
        func << '    bbcls, "allocateDirect", "(I)Ljava/nio/ByteBuffer;");'
        func << 'jobject bb = _jenv->CallStaticObjectMethod('
        func << '    bbcls, mid, sizeof(%s));' % STRUCT_NAME
        func << '%s *p = reinterpret_cast<%s*>(' % (STRUCT_NAME, STRUCT_NAME)
        func << '    _jenv->GetDirectBufferAddress(bb));'
        func << 'p->_delete = nullptr;'
        func << 'return bb;'
        return func

    def getTemplateInstanceCode(self):
        func = bw.cxx.Func("template<class T> T *", GET_FUNC_NAME,
                           ["JNIEnv *_jenv", "jobject _this"])
        func << '%s *p = reinterpret_cast<%s*>(' % (STRUCT_NAME, STRUCT_NAME)
        func << '    _jenv->GetDirectBufferAddress(_this));'
        func << "return reinterpret_cast<T*>(p->p);"
        return func

    def callDeleteCode(self):
        func = bw.cxx.Func("void", DELETE_FUNC_NAME,
                           ["JNIEnv *_jenv", "jobject _this"])
        func << '%s *p = reinterpret_cast<%s*>(' % (STRUCT_NAME, STRUCT_NAME)
        func << '    _jenv->GetDirectBufferAddress(_this));'
        func << "p->_delete(p->p);"
        return func
