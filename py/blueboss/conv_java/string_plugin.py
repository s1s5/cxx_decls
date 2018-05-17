# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw
import plugin
import jpath
import arg_converter
import return_converter
import builtin_plugin

J2C_FUNC = "convert_jstring2cstring"
C2J_FUNC = "convert_cstring2jstring"


def isString(cxx_type):
    def _update(c, t):
        if hasattr(t, 'isConstQualified'):
            c = c or t.isConstQualified
        return c
    is_const = False

    if (isinstance(cxx_type, bc.PointerType) and
            isinstance(cxx_type.pointeeType, bc.BuiltinType) and
            cxx_type.pointeeType.spelling == 'char' and
            cxx_type.pointeeType.isConstQualified):
        return True
    elif (isinstance(cxx_type, bc.TemplateSpecializationType) and
          isinstance(cxx_type.sugar, bc.RecordType) and
          bc.is_std_string(cxx_type.sugar.decl) and
          len(cxx_type.args) == 1 and
          isinstance(cxx_type.args[0].type, bc.BuiltinType) and
          (cxx_type.args[0].type.spelling == 'char' or
           cxx_type.args[0].type.spelling == 'unsigned char')):
        return True
    elif isinstance(cxx_type, bc.LValueReferenceType):
        is_const = _update(is_const, cxx_type)
        cxx_type = cxx_type.pointeeType
        if isinstance(cxx_type, bc.ElaboratedType):
            is_const = _update(is_const, cxx_type)
            cxx_type = cxx_type.namedType
        if isinstance(cxx_type, bc.TypedefType):
            is_const = _update(is_const, cxx_type)
            cxx_type = cxx_type.decl.underlyingType
        is_const = _update(is_const, cxx_type)
        a = isString(cxx_type)
        _, isc = parseString(cxx_type)
        if isc or is_const:
            return a
    return False


def parseString(cxx_type):
    def _update(c, t):
        if hasattr(t, 'isConstQualified'):
            c = c or t.isConstQualified
        return c

    if isinstance(cxx_type, bc.ParmVarDecl):
        cxx_type = cxx_type.type

    is_const = False
    if (isinstance(cxx_type, bc.TemplateSpecializationType) and
        isinstance(cxx_type.sugar, bc.RecordType) and
        bc.is_std_string(cxx_type.sugar.decl) and
        len(cxx_type.args) == 1 and
        isinstance(cxx_type.args[0].type, bc.BuiltinType) and
            cxx_type.args[0].type.spelling == 'char'):
        is_const = _update(is_const, cxx_type)
        return cxx_type, is_const
    elif isinstance(cxx_type, bc.LValueReferenceType):
        cxx_type = cxx_type.pointeeType
        is_const = _update(is_const, cxx_type)
        if isinstance(cxx_type, bc.ElaboratedType):
            cxx_type = cxx_type.namedType
            is_const = _update(is_const, cxx_type)
        if isinstance(cxx_type, bc.TypedefType):
            cxx_type = cxx_type.decl.underlyingType
            is_const = _update(is_const, cxx_type)
        t, is_c = parseString(cxx_type)
        return t, is_c or is_const
    return None, False


class StringArgConverter(arg_converter.ArgConverter):
    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        if isString(cxx_type):
            return klass(creator, arg, func_conv)

    def imports(self):
        return []

    def getJClass(self):
        return jpath.String

    def getJniType(self):
        return 'jstring'

    def dumpJniCallPre(self, source):
        source << "std::string %s_str_ = %s(_jenv, %s);" % (
            self.getArgName(),
            J2C_FUNC,
            self.getArgName(), )

    def getJniCall(self):
        s = '%s_str_' % self.getArgName()
        if isinstance(self.arg.type, bc.PointerType):
            s += ".c_str()"
        return s


class StringReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isString(cxx_type):
            return klass(creator, cxx_type, func_conv)

    def imports(self):
        return []

    def getJInterface(self):
        return jpath.String

    def getJClass(self):
        return jpath.String

    def getJniType(self):
        return 'jstring'

    def dumpJniCall(self, source, call_string):
        source << ('%s _ret_ = %s(_jenv, %s);' % (self.getJniType(),
                                                  C2J_FUNC,
                                                  call_string, ))


class StringPlugin(plugin.Plugin):
    def linkStart(self):
        self.flag = False

    def resolveFilter(self, decl_or_type):
        return isString(decl_or_type)

    def resolveInterfacePath(self, decl_or_type):
        self.flag = True
        return builtin_plugin.BuiltinClass, jpath.String

    def resolveClassPath(self, decl_or_type):
        self.flag = True
        return builtin_plugin.BuiltinClass, jpath.String

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                self.flag = True
                return r

    def getArgConverter(self, arg_decl, func_conv):
        l = [StringArgConverter.check]
        return self.__getConverter(l, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        l = [StringReturnConverter.check]
        return self.__getConverter(l, ret_type, func_conv)

    def jniHeader(self):
        if not self.flag:
            return None
        sl = bw.cxx.StatementList()
        f = bw.cxx.Func("std::string", J2C_FUNC,
                        ["JNIEnv *_jenv", "jstring fr"])
        f << 'const char *c1 = _jenv->GetStringUTFChars(fr, 0);'
        f << 'std::string a = c1;'
        f << '_jenv->ReleaseStringUTFChars(fr, c1);'
        f << 'return a;'
        sl << f
        f = bw.cxx.Func("jstring", C2J_FUNC,
                        ["JNIEnv *_jenv", "const std::string &fr"])
        f << 'return _jenv->NewStringUTF(fr.c_str());'
        sl << f
        return sl
