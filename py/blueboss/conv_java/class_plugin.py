# coding: utf-8
import base
import plugin
import jpath
import arg_converter
import return_converter
import function_converter
import jclass
import bridge
from blueboss import common as bc
from blueboss import writer as bw


class CXXGetterDecl(bc.CXXMethodDecl):
    pass


class CXXSetterDecl(bc.CXXMethodDecl):
    pass


class CXXCopyDecl(bc.CXXMethodDecl):
    pass


class CXXAssignOperatorDecl(bc.CXXMethodDecl):
    pass


def parseType(decl_or_type):
    is_const = False
    if isinstance(decl_or_type, bc.ParmVarDecl):
        decl_or_type = decl_or_type.type
    if isinstance(decl_or_type, bc.LValueReferenceType):
        decl_or_type = decl_or_type.pointeeType
    if isinstance(decl_or_type, bc.ElaboratedType):
        is_const = decl_or_type.isConstQualified
        decl_or_type = decl_or_type.namedType
    if isinstance(decl_or_type, bc.RecordType):
        is_const = is_const or decl_or_type.isConstQualified
        decl_or_type = decl_or_type.decl
    if not isinstance(decl_or_type, bc.RecordDecl):
        decl_or_type = None
    return decl_or_type, is_const


def _getAllBases(decl):
    s = set()
    for i in decl.bases:
        if i.access == "public":
            t = base.eraseTypedef(i.type)
            if isinstance(t, bc.TemplateSpecializationType):
                t = t.sugar
            d = t.decl
            s.add(d)
            s.update(_getAllBases(d))
    return s


def declId(decl):
    if not isinstance(decl, bc.RecordDecl):
        raise TypeError()
    return '_'.join(decl.cname().split('::')).replace(
        '<', '_lt_').replace('>', '_gt_')


def declCreateFuncName(decl=None):
    if decl:
        return "%s%s" % (bridge.CREATE_FUNC_NAME, declId(decl))
    else:
        return bridge.CREATE_FUNC_NAME


def declGetInstanceFuncName(decl=None):
    if decl is None:
        return bridge.GET_FUNC_NAME
    return "%s%s" % (bridge.GET_FUNC_NAME, declId(decl))


def declDeleteInstanceFuncName(decl=None):
    if decl is None:
        return bridge.DELETE_FUNC_NAME
    return "%s%s" % (bridge.DELETE_FUNC_NAME, declId(decl))


class ClassArgConverter(arg_converter.ArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        decl, is_const = parseType(arg)
        if decl is not None:
            return klass(creator, arg, func_conv)

    def __init__(self, *args, **kw):
        super(ClassArgConverter, self).__init__(*args, **kw)
        self.cxx_record, _ = parseType(self.arg)

    # def imports(self):
    #     return super(ClassArgConverter, self).imports()

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivType(self):
        return 'ByteBuffer'

    def getJavaPrivCall(self):
        return self.getArgName() + '.__getBB()'

    def getJniCall(self):
        fn = declGetInstanceFuncName(self.cxx_record)
        return '(*(%s(_jenv, %s)))' % (fn, self.getArgName())


class ClassReturnConverter(return_converter.ReturnConverter):

    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        decl, is_const = parseType(cxx_type)
        if decl is not None:
            return klass(creator, cxx_type, func_conv)

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivType(self):
        return "ByteBuffer"

    def dumpJavaPrivReturn(self, source):
        jcls = self.jclass.getClassPath()
        if isinstance(self.cxx_type, bc.LValueReferenceType):
            if self.func_conv.isStatic():
                source << "return new %s(_ret_, new Object());" % jcls
            else:
                source << "return new %s(_ret_, (Object)this);" % jcls
        else:
            source << "return new %s(_ret_, null);" % jcls

    def dumpJniCallPre(self, source):
        fn = declCreateFuncName(self._getRecord())
        source << "jobject _bb_ = %s(_jenv);" % fn
        source << '%s *p = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                      bridge.STRUCT_NAME)
        source << '    _jenv->GetDirectBufferAddress(_bb_));'

    def dumpJniCall(self, source, call_string):
        if isinstance(self.cxx_type, bc.LValueReferenceType):
            source << ('p->p = const_cast<void*>('
                       'reinterpret_cast<const void*>(&(%s)));' % call_string)
        else:
            source << ('p->p = new %s(%s);' % (self._getRecord().cname(),
                                               call_string, ))

    def dumpJniReturn(self, source):
        source << "return _bb_;"

    def _getRecord(self):
        decl, is_const = parseType(self.cxx_type)
        return decl


class InstanceArgConverter(ClassArgConverter):

    def __init__(self, creator, decl, func_conv):
        arg = bc.ParmVarDecl("_this",
                             bc.LValueReferenceType(bc.RecordType(decl)))
        super(InstanceArgConverter, self).__init__(creator, arg, func_conv)

    def imports(self):
        return []

    def importsSys(self):
        return [jpath.ByteBuffer]

    def getJavaPrivCall(self):
        return 'this.__getBB()'

    def getJavaPrivType(self):
        return "ByteBuffer"


class ConstructorReturnConverter(ClassReturnConverter):

    def __init__(self, creator, cxx_type, func_conv):
        ty = bc.RecordType(cxx_type.decl)
        super(ConstructorReturnConverter, self).__init__(creator, ty,
                                                         func_conv)

    def dumpJavaPrivReturn(self, source):
        source << "__set(_ret_, null);"

    def getJavaPubType(self):
        return ""


class CopyReturnConverter(ClassReturnConverter):

    def __init__(self, creator, cxx_type, func_conv):
        ty = bc.RecordType(cxx_type.decl)
        super(CopyReturnConverter, self).__init__(creator, ty, func_conv)
        # self.ijns = creator.getImplClassPath(ty)

    def getJavaPrivReturn(self, source):
        source << ("return new %s(_ret_, (Object)null);" %
                   self.getJavaPrivType())
        # '.'.join(self.ijns.class_path), )

        # def getJavaPubType(self):
        #     return '.'.join(self.jns.class_path)


class AssignArgConverter(ClassArgConverter):

    def getJavaPubType(self):
        jp = self.creator.getBaseInterface().jpt
        return jp.getClassPath()

    def getJavaPrivCall(self):
        return '((%s)%s).__getBB()' % (self.jclass.getClassPath(),
                                       self.getArgName())


class CXXMethodConverter(function_converter.FunctionConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is bc.CXXMethodDecl:
            return klass(creator, decl)

    def __init__(self, creator, decl):
        super(CXXMethodConverter, self).__init__(creator, decl)
        self.instance_arg_converter = InstanceArgConverter(creator,
                                                           decl.parent, self)

    def isStatic(self):
        return self.decl.isStatic

    def getBridgeArgConverters(self):
        if self.isStatic():
            return self.arg_converters
        else:
            return [self.instance_arg_converter] + self.arg_converters

    def getJniCallString(self):
        if self.isStatic():
            return super(CXXMethodConverter, self).getJniCallString()
        else:
            l = map(lambda x: x.getJniCall(), self.arg_converters)
            return '%s.%s(%s)' % (self.instance_arg_converter.getJniCall(),
                                  self.decl.name, ', '.join(l))


class CXXGetterConverter(CXXMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is CXXGetterDecl:
            return klass(creator, decl)

    def isStatic(self):
        return False

    def getJniCallString(self):
        n = self.decl.name
        if (self.decl.returnType.isConstQualified or
                self.decl.returnType.pointeeType.isConstQualified):
            n = n[4:]
        if n.endswith('_copy'):
            n = n[:-5]
        return '%s.%s' % (self.instance_arg_converter.getJniCall(), n, )


class CXXSetterConverter(CXXMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is CXXSetterDecl:
            return klass(creator, decl)

    def isStatic(self):
        return False

    def getJniCallString(self):
        n = self.decl.name[4:]
        l = map(lambda x: x.getJniCall(), self.getBridgeArgConverters()[1:])
        return '%s.%s = (%s)' % (
            self.instance_arg_converter.getJniCall(), n, ', '.join(l))


class CXXConstructorConverter(CXXMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is bc.CXXConstructorDecl:
            return klass(creator, decl)

    def getReturnConverter(self):
        return ConstructorReturnConverter(
            self.creator, bc.RecordType(self.decl.parent), self)

    def isStatic(self):
        return False

    def getJavaPubName(self):
        return "Impl"

    def getJniCallString(self):
        l = map(lambda x: x.getJniCall(), self.arg_converters)
        return ', '.join(l)


class CXXCopyConverter(CXXConstructorConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is CXXCopyDecl:
            return klass(creator, decl)

    def getReturnConverter(self):
        return CopyReturnConverter(self.creator,
                                   bc.RecordType(self.decl.parent), self)

    def getJavaPubName(self):
        return "copy"

    def getJniCallString(self):
        fn = declGetInstanceFuncName(self.decl.parent)
        return '*%s(_jenv, _this)' % fn


class CXXAssignOperatorConverter(CXXMethodConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is CXXAssignOperatorDecl:
            return klass(creator, decl)

    def getArgConverters(self):
        return [AssignArgConverter(self.creator, self.decl.params[0], self)]

    def isStatic(self):
        return False

    def getJavaPubName(self):
        return "assign"

    def getJniCallString(self):
        fn = declGetInstanceFuncName(self.decl.parent)
        l = map(lambda x: x.getJniCall(), self.arg_converters)
        r = '*%s(_jenv, _this) = %s' % (fn, l[0])
        return r


class ClassPlugin(plugin.Plugin):

    def depends(self):
        return [bridge.BridgePlugin]

    def linkStart(self):
        self.classes = set()
        self.class_names = {}
        self.declared_classes = set(self.creator.getDeclarations())

    def __addClassDecl(self, decl):
        if decl in self.classes:
            return
        if decl.path in map(lambda x: x.path, self.classes):
            # print decl
            # print self.classes
            # raise Exception()
            return
        self.classes.add(decl)

    def __setRecord(self, d):
        decl, is_const = parseType(d)
        if decl is None:
            return
        # print d.name
        self.resolveInterfacePath(bc.LValueReferenceType(
            bc.RecordType(decl,
                          isConstQualified=True)))
        self.resolveInterfacePath(decl)
        self.resolveClassPath(decl)
        self.__addClassDecl(decl)

    def resolveFilter(self, decl_or_type):
        decl, is_const = parseType(decl_or_type)
        return decl is not None

    def resolveInterfacePath(self, decl_or_type):
        decl, is_const = parseType(decl_or_type)
        c = ''
        if is_const:
            c = 'Const'
        n = decl.cname().split('::')
        n[-1] = n[-1].replace('<', '_lt_').replace('>', '_gt_')
        if n[-1] == 'Object':
            n[-1] = '_' + n[-1] + '_'
        # package = self.class_names[tuple(n)]
        # if package:
        #     ns = package
        #     n = n[len(package):]
        # else:
        #     ns = ()
        n[-1] = c + n[-1]
        self.__addClassDecl(decl)
        # return jclass.Interface, jpath.JPath(tuple(ns) + tuple(n))
        return jclass.Interface, jpath.JPath(tuple(n))

    def resolveClassPath(self, decl_or_type):
        decl, is_const = parseType(decl_or_type)
        f, jp = self.creator.resolveInterfacePath(decl)
        self.__addClassDecl(decl)
        return jclass.Class, jpath.JPath(jp.path + ('Impl', ))

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getFunctionConverter(self, func_decl, decl_class=None):
        l = [
            CXXMethodConverter.check,
            CXXConstructorConverter.check,
            CXXGetterConverter.check,
            CXXSetterConverter.check,
            CXXCopyConverter.check,
            CXXAssignOperatorConverter.check,
        ]
        return self.__getConverter(l, func_decl)

    def getArgConverter(self, arg_decl, func_conv):
        l = [ClassArgConverter.check, ]
        self.__setRecord(arg_decl)
        return self.__getConverter(l, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        l = [ClassReturnConverter.check, ]
        self.__setRecord(ret_type)
        return self.__getConverter(l, ret_type, func_conv)

    def walkUsr(self, decl):
        if not isinstance(decl, bc.RecordDecl):
            return
        self.class_names[tuple(decl.cname().split('::'))] = None

    def walkUsrEnd(self):
        c = set(self.class_names.keys())
        for key in self.class_names:
            t = key
            while t in c:
                t = t[:-1]
            self.class_names[key] = t

    def declare(self, decl):
        if not isinstance(decl, bc.RecordDecl):
            return False
        if decl.access != "public" and decl.access != "none":
            return False
        # print decl, "!" * 10
        # decl.show()
        if decl.describedClassTemplate is not None:
            return False

        self.classes.add(decl)
        for i in self.listBases(decl):
            self.classes.add(i)

        cc = bc.RecordType(decl, isConstQualified=True)
        nc = bc.RecordType(decl, isConstQualified=False)
        cls = [
            self.creator.getInterface(cc),
            self.creator.getInterface(nc),
            self.creator.getClass(nc),
        ]

        cls[2].is_valid = not decl.isAbstract

        cls[1].addBase(cls[0])
        cls[2].addBase(cls[1])

        # for i in self.listMethods(decl, const=True):
        for i in self.listAllMethods(decl, const=True):
            conv = self.creator.getFunctionConverter(i, decl)
            if not conv.isStatic():
                cls[0].addFunction(conv)
            # cls[2].addFunction(conv)
        # for i in self.listMethods(decl, const=False):
        for i in self.listAllMethods(decl, const=False):
            conv = self.creator.getFunctionConverter(i, decl)
            if not conv.isStatic():
                cls[1].addFunction(conv)
            # cls[2].addFunction(conv)

        if not decl.isAbstract:
            for i in self.listAllMethods(decl):
                conv = self.creator.getFunctionConverter(i, decl)
                cls[2].addFunction(conv)
            for i in self.listConstructors(decl):
                conv = self.creator.getFunctionConverter(i, decl)
                cls[2].addFunction(conv)

        if self.hasCopyConstructor(decl):
            f = CXXCopyDecl(decl.cname() + "::__copy__", None,
                            bc.RecordType(decl), [], decl)
            conv = self.creator.getFunctionConverter(f, decl)
            cls[0].addFunction(conv)
            if not decl.isAbstract:
                cls[2].addFunction(conv)
            f = CXXAssignOperatorDecl(decl.cname() + "::__assign__",
                                      None,
                                      bc.BuiltinType("void"),
                                      [bc.ParmVarDecl(
                                          "arg",
                                          bc.LValueReferenceType(bc.RecordType(
                                              decl,
                                              isConstQualified=True)), ), ],
                                      decl)
            conv = self.creator.getFunctionConverter(f, decl)
            cls[1].addFunction(conv)
            if not decl.isAbstract:
                cls[2].addFunction(conv)
        return True

    def linkEnd(self):
        try:
            self.classes.remove(None)
        except:
            pass

        self.decls = []
        self.decl_indexes = {}
        self.decl_bases = {}
        for decl in sorted(self.classes, key=lambda x: x.path):
            # print type(decl)
            # print decl
            cc = bc.RecordType(decl, isConstQualified=True)
            nc = bc.RecordType(decl, isConstQualified=False)
            cls = [
                self.creator.getInterface(cc),
                self.creator.getInterface(nc),
                self.creator.getClass(nc),
            ]
            cls[1].addBase(cls[0])
            cls[2].addBase(cls[1])

            declared = filter(lambda x: x in self.declared_classes,
                              self.listBases(decl))
            for i in declared:
                cci = bc.RecordType(i, isConstQualified=True)
                nci = bc.RecordType(i, isConstQualified=False)
                cls[0].addBase(self.creator.getInterface(cci))
                cls[1].addBase(self.creator.getInterface(nci))

            self.decl_indexes[decl] = len(self.decls)
            self.decls.append(decl)
            self.decl_bases[decl] = _getAllBases(decl)

    def jniHeader(self):
        sl = bw.cxx.StatementList()
        # if self.classes:
        #     sl << self.generalClass()
        #     sl << self.createInstanceCodeBase()
        for i in self.classes:
            if self.canCallDestructor(i) and not i.isAbstract:
                sl << self.deleteInstanceCode(i)
            if not i.isAbstract:
                sl << self.createInstanceCode(i)
            sl << self.getInstanceCode(i)
        return sl

    def jniSource(self):
        pass

    def listBases(self, decl, with_declared=True):
        l = [decl]
        res = []
        while l:
            d = l.pop()
            for b in d.bases:
                if b.access == 'public':
                    t = base.eraseTypedef(b.type)
                    if isinstance(t, bc.TemplateSpecializationType):
                        t = t.sugar
                    ct = t.decl
                    if (not with_declared) and ct in self.declared_classes:
                        continue
                    l.append(ct)
                    res.append(ct)
        return res

    def listConstructors(self, decl):
        l = []
        # if decl.hasDefaultConstructor:
        #     dd = filter(lambda x: x.isDefaultConstructor, decl.ctors)
        #     if not dd:
        #         l.append(bc.CXXConstructorDecl(
        #             decl.path, None, bc.BuiltinType(
        #             "void"), [], decl))
        if decl.hasDefaultConstructor and not decl.hasUserDeclaredConstructor:
            l.append(bc.CXXConstructorDecl(decl.cname(), None, bc.BuiltinType(
                "void"), [], decl))
        return l  # + decl.ctors

    def listMethods(self, decl, const=False):
        bases = self.listBases(decl, False)
        m = []
        for i in decl.methods:
            if const is not None and isinstance(i, bc.CXXConstructorDecl):
                continue
            if i.isImplicit:
                continue
            if i.access != "public":
                continue
            if (const is not None) and (i.isConst ^ const):
                continue
            m.append(i)

        for d in bases:
            for i in d.methods:
                if i.access != "public":
                    continue
                if i.isImplicit:
                    continue

                if isinstance(i, bc.CXXConstructorDecl):
                    continue
                m.append(i)

        for i in decl.fields:
            if i.access != "public":
                continue
            # h = self.getFieldHandler(i)
            # m += (h.getter(const) + h.setter(const))
            m += self.getter(decl, i, const)
            m += self.setter(decl, i, const)

        for d in bases:
            for i in d.fields:
                if i.access != "public":
                    continue
                # h = self.getFieldHandler(i)
                # m += (h.getter(const) + h.setter(const))
                m += self.getter(decl, i, const)
                m += self.setter(decl, i, const)

        return m

    def listAllMethods(self, decl, without_implicit=True, const=None):
        bases = self.listBases(decl, const is None)
        declared = set()
        overriden = set()

        for i in decl.methods:
            if const is not None and isinstance(i, bc.CXXConstructorDecl):
                continue
            if without_implicit and i.access != "public":
                continue
            if without_implicit and i.isImplicit:
                continue
            if (const is not None) and (i.isConst ^ const):
                continue
            declared.add(i)
            map(overriden.add, i.overridden_methods)

        for d in bases:
            for i in d.methods:
                if without_implicit and i.access != "public":
                    continue
                if without_implicit and i.isImplicit:
                    continue
                if isinstance(i, bc.CXXConstructorDecl):
                    continue
                if (const is not None) and (i.isConst ^ const):
                    continue

                declared.add(i)
                map(overriden.add, i.overridden_methods)

        declared.difference_update(overriden)
        m = list(declared)
        for i in decl.fields:
            if i.access != "public":
                continue
            # h = self.getFieldHandler(i)
            # m += (h.getter(None) + h.setter(None))
            m += self.getter(decl, i, const)
            m += self.setter(decl, i, const)

        for d in bases:
            for i in d.fields:
                if i.access != "public":
                    continue
                # h = self.getFieldHandler(i)
                # m += (h.getter(const) + h.setter(const))
                m += self.getter(decl, i, const)
                m += self.setter(decl, i, const)
        return m

    def hasCopyConstructor(self, decl):
        # print ">>>", decl, "<<<"
        flag = True
        for i in self.listAllMethods(decl, without_implicit=False):
            # print i, i.isCopyAssignmentOperator, i.isCopyAssignmentOperator
            # and i.access == 'private' or i.isDeleted
            if i.isCopyAssignmentOperator:
                if (i.access != 'public') or i.isDeleted:
                    flag = False
                    break
        # for i in dir(decl):
        #     print i, '=>', getattr(decl, i)
        return flag

    def getter(self, class_decl, decl, const):
        if const is None:
            return (self.getter(class_decl, decl, False) +
                    self.getter(class_decl, decl, True))
        name = decl.path
        if const:
            n = name.split('::')
            name = 'get_' + n[-1]
            if len(n) > 1:
                name = '::'.join(n[:-1] + [name])
        ret_type = decl.type
        if isinstance(ret_type, bc.SubstTemplateTypeParmType):
            ret_type = ret_type.sugar
        ret_type = ret_type.shallowCopy()
        ret_type.isConstQualified = const
        l = []
        if const:
            l.append(CXXGetterDecl(
                name + "_copy", None, ret_type, [], class_decl))
        if not isinstance(ret_type, bc.LValueReferenceType):
            ret_type = bc.LValueReferenceType(ret_type)
        l.append(CXXGetterDecl(name, None, ret_type, [], class_decl))
        return l

    def setter(self, class_decl, decl, const):
        if const:
            return []
        name = decl.path
        n = name.split('::')
        name = 'set_' + n[-1]
        if len(n) > 1:
            name = '::'.join(n[:-1] + [name])
        arg_type = decl.type
        if isinstance(arg_type, bc.SubstTemplateTypeParmType):
            arg_type = arg_type.sugar
        arg_type = arg_type.shallowCopy()
        arg_type.isConstQualified = True
        l = []
        l.append(CXXSetterDecl(name, None, bc.BuiltinType("void"),
                               [bc.ParmVarDecl("var", arg_type)], class_decl))
        if not isinstance(arg_type, bc.LValueReferenceType):
            arg_type = bc.LValueReferenceType(arg_type)
            l.append(CXXSetterDecl(name, None, bc.BuiltinType("void"),
                                   [bc.ParmVarDecl("var", arg_type)],
                                   class_decl))
        return l

    # def generalClass(self):
    #     st = bw.cxx.Struct(STRUCT_NAME)
    #     st << "int id;"
    #     st << "void *p;"
    #     return st

    # def createInstanceCodeBase(self):
    #     func = bw.cxx.Func("jobject", CREATE_FUNC_NAME, ["JNIEnv *_jenv", ])
    #     func << 'jclass bbcls = _jenv->FindClass("java/nio/ByteBuffer");'
    #     func << 'jmethodID mid = _jenv->GetStaticMethodID('
    #     func << '    bbcls, "allocateDirect", "(I)Ljava/nio/ByteBuffer;");'
    #     func << 'jobject bb = _jenv->CallStaticObjectMethod('
    #     func << '    bbcls, mid, sizeof(%s));' % STRUCT_NAME
    #     func << 'return bb;'
    #     return func

    def createInstanceCode(self, decl):
        index = self.decl_indexes[decl]
        func = bw.cxx.Func("jobject", declCreateFuncName(decl),
                           ["JNIEnv *_jenv", ])
        func << ('jobject bb = %s(_jenv);' % bridge.CREATE_FUNC_NAME)
        func << '%s *p = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                    bridge.STRUCT_NAME)
        func << '    _jenv->GetDirectBufferAddress(bb));'
        func << 'p->tag = %d;' % index
        if self.canCallDestructor(decl):
            func << ('p->_delete = (void (*)(void *))%s;' %
                     declDeleteInstanceFuncName(decl))
        func << 'return bb;'
        return func

    def getInstanceCode(self, decl):
        func = bw.cxx.Func(
            "%s *" % decl.cname(), declGetInstanceFuncName(decl),
            ["JNIEnv *_jenv", "jobject _this"])
        func << '%s *p = reinterpret_cast<%s*>(' % (bridge.STRUCT_NAME,
                                                    bridge.STRUCT_NAME)
        func << '    _jenv->GetDirectBufferAddress(_this));'
        l = []
        for key, value in sorted(self.decl_bases.items(),
                                 key=lambda x: x[0].path):
            if decl in value:
                l.append((self.decl_indexes[key], key))
        for i in xrange(len(l)):
            if i:
                j = bw.cxx.ElseIf("p->tag == %d" % l[i][0])
            else:
                j = bw.cxx.If("p->tag == %d" % l[i][0])
            func << (
                j << "return reinterpret_cast<%s*>(p->p);" % l[i][1].cname())
        func << "return reinterpret_cast<%s*>(p->p);" % decl.cname()
        return func

    def deleteInstanceCode(self, decl):
        func = bw.cxx.Func("void", declDeleteInstanceFuncName(decl),
                           ["%s *p" % decl.cname(), ])
        func << "delete p;"
        return func

    def canCallDestructor(self, decl):
        return not (decl.destructor and decl.destructor.access != "public")
