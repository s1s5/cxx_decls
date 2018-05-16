# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import plugin
import jpath
import arg_converter
import function_converter
import bridge


class ArgConverter(arg_converter.ArgConverter):
    # def imports(self):
    #     return super(ClassArgConverter, self).imports()

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getArgName(self):
        return "arg"

    def getJClass(self):
        pass

    def getJavaPrivType(self):
        return 'ByteBuffer'

    def getJavaPrivCall(self):
        return 'this.__getBB()'

    def getJniCall(self):
        return self.getArgName()
        # fn = declGetInstanceFuncName(self.cxx_record)
        # return '(*(%s(_jenv, %s)))' % (fn, self.getArgName())


# class FinalizeDecl(bc.CXXMethodDecl):
    # @Override
    # protected void finalize() {
    #     try {
    #         if (!_is_reference) {
    #             f2();
    #         }
    #         super.finalize();
    #     } catch (Throwable t){
    #     }
    # }


class FinalizeFunctionConverter(function_converter.FunctionConverter):
    # def getArgConverters(self):
    #     return []
    def annotations(self):
        return ["@Override"]

    def isStatic(self):
        return False

    def getJavaPubAccess(self):
        return "protected"

    def getJavaPubName(self):
        return "finalize"

    def getBridgeArgConverters(self):
        return [ArgConverter(self.creator, bc.ParmVarDecl(), self.decl)]

    def dumpJavaPrivCall(self, source):
        self.dumpJavaPrivCallPre(source)
        map(lambda x: x.dumpJavaPrivCallPre(source),
            self.getBridgeArgConverters())
        self.return_converter.dumpJavaPrivCallPre(source)
        call_string = self.getJavaPrivCallString()
        tr = bw.java.Try()
        ifs = bw.java.If("__owner == null")
        tr << ifs
        ca = bw.java.Catch("Throwable", "t")
        source << tr
        source << ca
        self.return_converter.dumpJavaPrivCall(ifs, call_string)
        map(lambda x: x.dumpJavaPrivCallPost(source),
            self.getBridgeArgConverters())
        self.return_converter.dumpJavaPrivCallPost(source)
        self.dumpJavaPrivCallPost(source)
        self.return_converter.dumpJavaPrivReturn(source)

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters())
        return '%s(_jenv, %s)' % (bridge.DELETE_FUNC_NAME, ', '.join(l))


class MemoryPlugin(plugin.Plugin):
    def linkEnd(self):
        base = self.creator.getBaseClass()
        f = bc.FunctionDecl("", None, bc.BuiltinType("void"), [])
        f = FinalizeFunctionConverter(self.creator, f)
        base.addFunction(f)
