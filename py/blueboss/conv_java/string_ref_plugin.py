# coding: utf-8
from blueboss import common as bc
import plugin
import string_plugin
import jpath
import jclass
import builtin_reference_plugin


STRING_REF_CLASS_PATH = jpath.JPath(("primitives", "StringRef"))
STRING_TYPE = bc.TemplateSpecializationType()
STRING_TYPE.sugar = bc.RecordType(bc.RecordDecl('std::basic_string'))
STRING_TYPE.args = [
    bc.TemplateArgument()
]
STRING_TYPE.args[0].type = bc.BuiltinType("char")


class StringRefGetDecl(bc.CXXMethodDecl):
    pass


class StringRefSetDecl(bc.CXXMethodDecl):
    pass


class InstanceArgConverter(builtin_reference_plugin.InstanceArgConverter):
    def getCTypeName(self):
        return "std::string"


class GetConverter(
        builtin_reference_plugin.BuiltinReferenceGetMethodConverter):
    def getInstanceArgConverter(self):
        return InstanceArgConverter(self.creator, self.decl.parent, self)


class SetConverter(
        builtin_reference_plugin.BuiltinReferenceAssignMethodConverter):
    def getInstanceArgConverter(self):
        return InstanceArgConverter(self.creator, self.decl.parent, self)


class ReturnConverter(
        builtin_reference_plugin.BuiltinReferenceReturnConverter):
    pass


class StringRefPlugin(plugin.Plugin):

    def linkStart(self):
        self.__flag = False

    def resolveFilter(self, decl_or_type):
        if not isinstance(decl_or_type, bc.LValueReferenceType):
            return False
        t, c = string_plugin.parseString(decl_or_type)
        return t and (not c)

    def resolveInterfacePath(self, decl_or_type):
        self.__flag = True
        return jclass.Class, STRING_REF_CLASS_PATH

    def resolveClassPath(self, decl_or_type):
        self.__flag = True
        return jclass.Class, STRING_REF_CLASS_PATH

    def getFunctionConverter(self, func_decl, decl_class=None):
        if isinstance(func_decl, StringRefGetDecl):
            return GetConverter(self.creator, func_decl)
        elif isinstance(func_decl, StringRefSetDecl):
            return SetConverter(self.creator, func_decl)
        return None

    def getReturnConverter(self, ret_type, func_conv):
        if not self.resolveFilter(ret_type):
            return None
        return ReturnConverter(self.creator, ret_type, func_conv)

    def linkEnd(self):
        if not self.__flag:
            return
        klass = self.creator.getClass(STRING_REF_CLASS_PATH)
        f = StringRefGetDecl("StringRef::get", None,
                             STRING_TYPE, [], bc.CXXRecordDecl("int"))
        conv = self.creator.getFunctionConverter(f)
        klass.addFunction(conv)
        f = StringRefSetDecl("StringRef::set", None,
                             bc.BuiltinType("void"), [
                                 bc.ParmVarDecl("arg", STRING_TYPE)],
                             bc.CXXRecordDecl("int"))
        conv = self.creator.getFunctionConverter(f)
        klass.addFunction(conv)
