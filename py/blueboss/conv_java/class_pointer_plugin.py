# coding: utf-8
from blueboss import common as bc
import plugin
import jclass
import jpath
import class_plugin
import arg_converter
# import bridge
import function_converter


class PointerAtDecl(bc.CXXMethodDecl):
    pass


class getPointerFunctionDecl(bc.CXXMethodDecl):
    pass


class PointerClass(jclass.Class):
    pass
    # def __init__(self, *args, **kw):
    #     super(PointerClass, self).__init__(*args, **kw)
    #     self.base_class = self.creator.getBaseClass()

    # def setBaseClass(self, klass):
    #     self.base_class = klass

    # def getBaseClass(self):
    #     return self.base_class


def parseType(decl_or_type):
    is_const = False
    if isinstance(decl_or_type, bc.ParmVarDecl):
        decl_or_type = decl_or_type.type
    if isinstance(decl_or_type, bc.PointerType):
        decl_or_type = decl_or_type.pointeeType
    else:
        return None, False
    if isinstance(decl_or_type, bc.ElaboratedType):
        is_const = decl_or_type.isConstQualified
        decl_or_type = decl_or_type.namedType
    if isinstance(decl_or_type, bc.RecordType):
        is_const = is_const or decl_or_type.isConstQualified
        decl_or_type = decl_or_type.decl
    if not isinstance(decl_or_type, bc.RecordDecl):
        decl_or_type = None
    return decl_or_type, is_const


class ClassPointerArgConverter(arg_converter.ArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        decl, _ = parseType(arg)
        if decl:
            return klass(creator, arg, func_conv)

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivType(self):
        return 'ByteBuffer'

    def getJavaPrivCall(self):
        return self.getArgName() + '.__getBB()'

    def getJniCall(self):
        # print self, self.arg, parseType(self.arg)
        cr, is_const = parseType(self.arg)
        name = cr.name
        if is_const:
            name = 'const ' + name
        fn = class_plugin.declGetInstanceFuncName(cr)
        r = '%s(_jenv, %s)' % (fn, self.getArgName())
        if is_const:
            return 'static_cast<const %s*>(%s)' % (cr.name, r)
        else:
            return r


class ClassPointerReturnConverter(class_plugin.ClassReturnConverter):

    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        decl, _ = parseType(cxx_type)
        if decl:
            return klass(creator, cxx_type, func_conv)

    def dumpJniCall(self, source, call_string):
        decl, _ = parseType(self.cxx_type)
        n = decl.path
        source << ('p->p = const_cast<%s*>(%s);' % (n, call_string, ))

    def _getRecord(self):
        decl, _ = parseType(self.cxx_type)
        return decl

    def dumpJavaPrivReturn(self, source):
        jcls = self.jclass.getClassPath()
        if self.func_conv.isStatic():
            source << "return new %s(_ret_, new Object());" % jcls
        else:
            source << "return new %s(_ret_, (Object)this);" % jcls


class InstanceArgConverter(ClassPointerArgConverter):

    def __init__(self, creator, decl, func_conv):
        arg = bc.ParmVarDecl("_this",
                             bc.PointerType(bc.RecordType(decl)))
        super(InstanceArgConverter, self).__init__(creator, arg, func_conv)

    def imports(self):
        return []

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivCall(self):
        return 'this.__getBB()'

    def getJavaPrivType(self):
        return "ByteBuffer"


class PointerAtConverter(class_plugin.CXXMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is PointerAtDecl:
            return klass(creator, decl)

    def __init__(self, creator, decl):
        super(PointerAtConverter, self).__init__(creator, decl)
        self.instance_arg_converter = InstanceArgConverter(creator,
                                                           decl.parent, self)

    def isStatic(self):
        return False

    def getBridgeArgConverters(self):
        if self.isStatic():
            return self.arg_converters
        else:
            return [self.instance_arg_converter] + self.arg_converters

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.arg_converters)
        return '%s[%s]' % (self.instance_arg_converter.getJniCall(), l[0])


class GetPointerFunctionConverter(function_converter.FunctionConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is getPointerFunctionDecl:
            return klass(creator, decl)

    def isStatic(self):
        return False

    def getJavaPrivName(self):
        return None

    def getJavaPrivCallString(self):
        return 'this.__getBB()'


class ClassPointerPlugin(plugin.Plugin):

    def depends(self):
        return [class_plugin.ClassPlugin]

    def linkStart(self):
        self.classes = {}

    def resolveFilter(self, decl_or_type):
        decl, _ = parseType(decl_or_type)
        return decl is not None

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getFunctionConverter(self, func_decl, decl_class=None):
        l = [PointerAtConverter.check, GetPointerFunctionConverter.check, ]
        return self.__getConverter(l, func_decl)

    def getArgConverter(self, arg_decl, func_conv):
        l = [ClassPointerArgConverter.check, ]
        return self.__getConverter(l, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        l = [ClassPointerReturnConverter.check, ]
        return self.__getConverter(l, ret_type, func_conv)

    def resolveInterfacePath(self, decl_or_type):
        decl, is_const = parseType(decl_or_type)
        klass, jp = self.creator.resolveInterfacePath(decl_or_type.pointeeType)
        klass = jclass.Class
        if not is_const:
            self.creator.getClass(bc.PointerType(
                bc.RecordType(decl,
                              isConstQualified=True)))
            klass = PointerClass
        njp = jpath.JPath(jp.path + ('Ptr', ))
        self.classes[jp.path] = decl_or_type
        return klass, njp

    def resolveClassPath(self, decl_or_type):
        return self.resolveInterfacePath(decl_or_type)
        # klass, jp =
        # self.creator.resolveInterfacePath(decl_or_type.pointeeType)
        # klass = jclass.Class
        # if not decl_or_type.pointeeType.isConstQualified:
        #     self.creator.getClass(bc.PointerType(
        # bc.RecordType(decl_or_type.pointeeType.record,
        # isConstQualified=True)))
        #     klass = PointerClass
        # njp = jpath.JPath(jp.package_path, jp.class_path + ('Ptr', ))
        # self.classes[jp.class_path] = decl_or_type
        # return klass, njp

    def linkEnd(self):
        for i in self.classes:
            decl = self.classes[i].pointeeType.decl
            isConstQualified = self.classes[i].pointeeType.isConstQualified
            c = self.creator.getClass(self.classes[i])
            intf = self.creator.getInterface(self.classes[i].pointeeType)
            intf2 = self.creator.getClass(self.classes[i].pointeeType)
            # print ">>", i, self.classes[i]
            fn = 'at'
            if isConstQualified:
                fn = 'cAt'
            f = PointerAtDecl(decl.name + "::" + fn,
                              None,
                              bc.LValueReferenceType(bc.RecordType(
                                  decl,
                                  isConstQualified=isConstQualified)),
                              [bc.ParmVarDecl("index",
                                              bc.BuiltinType("int"), )],
                              decl,
                              isConstQualified=isConstQualified)
            conv = self.creator.getFunctionConverter(f)
            c.addFunction(conv)
            fn = 'ref'
            if isConstQualified:
                fn = 'cref'
            f = getPointerFunctionDecl(decl.name + "::" + fn,
                                       None,
                                       bc.PointerType(bc.RecordType(
                                           decl,
                                           isConstQualified=isConstQualified)),
                                       [],
                                       decl)
            conv = self.creator.getFunctionConverter(f)
            # print intf, intf2, conv
            intf.addFunction(conv)
            intf2.addFunction(conv)
            if not isConstQualified:
                d = self.creator.getClass(bc.PointerType(
                    bc.RecordType(decl,
                                  isConstQualified=True)))
                c.setBaseClass(d)
