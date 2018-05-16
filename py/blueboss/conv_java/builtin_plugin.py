# coding: utf-8
from blueboss import common as bc
import base
import plugin
import jpath
import jclass
import return_converter
import arg_converter

java_primitive_types = {
    ("v", 0): "void",
    ("i", 8): "byte",
    ("i", 16): "short",
    ("i", 32): "int",
    ("i", 64): "long",
    ("c", 16): "char",
    ("f", 32): "float",
    ("f", 64): "double",
    ("f", 128): "double",
    ("i", 1): "boolean",
}


def getJavaBuiltinType(target_info, type_):
    if type_.spelling == 'void':
        return 'void'
    elif type_.spelling == 'bool':
        return 'boolean'
    attr = bc.builtin_types[type_.spelling]
    return java_primitive_types[attr[0], getattr(target_info, attr[1])]


def getJavaBuiltinTypeBits(target_info, type_):
    if type_.spelling == 'void':
        return 0
    elif type_.spelling == 'bool':
        return 1
    attr = bc.builtin_types[type_.spelling]
    return getattr(target_info, attr[1])


class BuiltinInterface(jclass.Interface):
    def __init__(self, creator, jpt):
        super(BuiltinInterface, self).__init__(creator, jpt)
        self.spelling = jpt.path[-1]

    def getClassPath(self):
        return self.spelling

    def isValid(self):
        return False


class BuiltinClass(jclass.Class):
    def __init__(self, creator, jpt):
        super(BuiltinClass, self).__init__(creator, jpt)
        self.spelling = jpt.path[-1]

    def getClassPath(self):
        return self.spelling

    def isValid(self):
        return False


class BuiltinArgConverter(arg_converter.ArgConverter):
    @classmethod
    def check(klass, creator, arg, func_conv):
        cxx_type = arg.type
        if isinstance(cxx_type, bc.BuiltinType):
            k = creator.getClass(cxx_type)
            if isinstance(k, BuiltinClass):
                return klass(creator, arg, func_conv)
        elif (isinstance(cxx_type, bc.LValueReferenceType) and
              isinstance(cxx_type.pointeeType, bc.BuiltinType) and
              cxx_type.pointeeType.isConstQualified):
            k = creator.getClass(cxx_type.pointeeType)
            if isinstance(k, BuiltinClass):
                return klass(creator, arg, func_conv)

    def imports(self):
        return []

    def getJniType(self):
        return 'j%s' % self.jclass.getClassPath()


class VoidReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isinstance(cxx_type, bc.BuiltinType):
            if cxx_type.spelling != "void":
                return
            k = creator.getClass(cxx_type)
            if isinstance(k, BuiltinClass):
                return klass(creator, cxx_type, func_conv)

    def imports(self):
        return []

    def getJavaPubType(self):
        return 'void'

    def getJavaPrivType(self):
        return 'void'

    def dumpJavaPrivCall(self, source, call_string):
        source << '%s;' % call_string

    def dumpJavaPrivReturn(self, source):
        pass

    def getJniType(self):
        return 'void'

    def dumpJniCall(self, source, call_string):
        source << '%s;' % call_string

    def dumpJniReturn(self, source):
        pass


class BuiltinReturnConverter(return_converter.ReturnConverter):
    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        if isinstance(cxx_type, bc.BuiltinType):
            k = creator.getClass(cxx_type)
            if isinstance(k, BuiltinClass) or isinstance(k, BuiltinInterface):
                return klass(creator, cxx_type, func_conv)
        elif (isinstance(cxx_type, bc.LValueReferenceType) and
              isinstance(base.eraseTypedef(
                  cxx_type.pointeeType), bc.BuiltinType) and
              cxx_type.pointeeType.isConstQualified):
            pt = base.eraseTypedef(cxx_type.pointeeType)
            k = creator.getClass(pt)
            if isinstance(k, BuiltinClass) or isinstance(k, BuiltinInterface):
                return klass(creator, pt, func_conv)

    def getJavaPrivType(self):
        return self.getJavaPubType()

    def imports(self):
        return []

    def getJniType(self):
        return 'j%s' % self.jinterface.getClassPath()


class BuiltinPlugin(plugin.Plugin):
    def resolveFilter(self, decl_or_type):
        if isinstance(decl_or_type, bc.BuiltinType):
            return True
        if (isinstance(decl_or_type, bc.LValueReferenceType) and
                isinstance(decl_or_type.pointeeType, bc.BuiltinType) and
                decl_or_type.pointeeType.isConstQualified):
            return True

    def resolveInterfacePath(self, decl_or_type):
        if isinstance(decl_or_type, bc.BuiltinType):
            return BuiltinInterface, jpath.JPath(
                ("__builtins__",
                 getJavaBuiltinType(self.target_info, decl_or_type), ))
        if (isinstance(decl_or_type, bc.LValueReferenceType) and
                isinstance(decl_or_type.pointeeType, bc.BuiltinType) and
                decl_or_type.pointeeType.isConstQualified):
            return BuiltinInterface, jpath.JPath(
                ("__builtins__", getJavaBuiltinType(
                    self.target_info, decl_or_type.pointeeType), ))

    def resolveClassPath(self, decl_or_type):
        # return self.creator.resolveInterfacePath(decl_or_type)
        res = self.creator.resolveInterfacePath(decl_or_type)
        if res:
            return BuiltinClass, jpath.JPath(res[1].path + ('Impl', ))

    def getArgConverter(self, arg_decl, func_decl):
        return BuiltinArgConverter.check(self.creator, arg_decl, func_decl)

    def getReturnConverter(self, ret_type, func_decl):
        a = VoidReturnConverter.check(self.creator, ret_type, func_decl)
        if a:
            return a
        return BuiltinReturnConverter.check(self.creator, ret_type, func_decl)
