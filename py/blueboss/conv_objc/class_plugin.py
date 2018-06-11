# coding: utf-8
import plugin
from blueboss import writer as bw
from blueboss import common as bc
import base
import objc_class
import arg_converter
import return_converter
import function_converter


class CXXGetterDecl(bc.CXXMethodDecl):
    pass


class CXXSetterDecl(bc.CXXMethodDecl):
    pass


class CXXCopyDecl(bc.CXXMethodDecl):
    pass


class CXXAssignOperatorDecl(bc.CXXMethodDecl):
    pass


class BridgeClass(objc_class.ObjCClass):
    def objcSourceHeader(self):
        k = super(BridgeClass, self).objcSourceHeader()
        if self.impl:
            k << bw.objc.Property(
                self.impl.cname(), '*i', "_bb_get_impl_", "_bb_set_impl_")
        return k

    def objcSourcePublic(self):
        k = super(BridgeClass, self).objcSourcePublic()
        if self.impl:
            p = self.creator.getPlugin(ClassPlugin)
            children = p.listChildren(self.impl)
            f = bw.objc.Func(self.impl.cname() + '*', "_bb_get_impl_", [])
            for idx, i in enumerate(children):
                cond = 'self->tag == %d' % getTag(self, i)
                if idx == 0:
                    ii = bw.objc.If(cond)
                else:
                    ii = bw.objc.ElseIf(cond)
                ii << "return reinterpret_cast<%s*>(self->impl);" % i.cname()
                f << ii
            f << "return reinterpret_cast<%s*>(self->impl);" % self.impl.cname()
            k << f
            f = bw.objc.Func("void", '_bb_set_impl_',
                             [('arg', self.impl.cname() + '*', 'arg')])
            f << "self->tag = %d;" % getTag(self, self.impl)
            f << "self->impl = arg;"
            k << f
        return k


def parseType(decl_or_type):
    is_const = False
    if isinstance(decl_or_type, bc.ParmVarDecl):
        decl_or_type = decl_or_type.type
    if isinstance(decl_or_type, bc.PointerType):
        decl_or_type = decl_or_type.pointeeType
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
        # print("-" * 80)
        # print(decl.path)
        # print(decl.type)
        # print(type(decl.type))
    if isinstance(decl_or_type, bc.ClassTemplateSpecializationDecl):
        decl_or_type = None
    return decl_or_type, is_const


def getTag(obj, decl):
    p = obj.creator.getPlugin(ClassPlugin)
    tag = p.class_indexes[decl]
    return tag


class ClassArgConverter(arg_converter.ArgConverter):

    @classmethod
    def check(klass, creator, arg, func_conv):
        decl, is_const = parseType(arg)
        if decl is not None:
            return klass(creator, arg, func_conv)

    def __init__(self, *args, **kw):
        super(ClassArgConverter, self).__init__(*args, **kw)
        self.with_id = True

    def getCCall(self):
        cxx_type = self.arg.type
        a = self.getArgName()
        if self.with_id:
            d, n = self.creator.resolveClass(cxx_type)
            if isinstance(cxx_type, bc.LValueReferenceType):
                return '*(((%s*)%s).i)' % (n, a)
            elif isinstance(cxx_type, bc.PointerType):
                return '((%s*)%s).i' % (n, a)
            else:
                return '*(((%s*)%s).i)' % (n, a)
        else:
            if isinstance(cxx_type, bc.LValueReferenceType):
                return '*((%s).i)' % (a, )
            elif isinstance(cxx_type, bc.PointerType):
                return '%s.i' % (a, )
            else:
                return '*((%s).i)' % (a, )

    def getObjCType(self):
        if self.with_id:
            d, n = self.creator.resolveClass(self.arg.type)
            return 'NSObject<Api_%s> *' % n
        else:
            return super(ClassArgConverter, self).getObjCType()


class ClassReturnConverter(return_converter.ReturnConverter):

    @classmethod
    def check(klass, creator, cxx_type, func_conv):
        decl, is_const = parseType(cxx_type)
        if decl is not None:
            return klass(creator, cxx_type, func_conv)

    def dumpCCallPre(self, source):
        decl, is_const = parseType(self.cxx_type)
        ot = self.creator.resolveClass(bc.RecordType(decl))[1]
        source << ("%s* _ret_val = [%s alloc];" % (ot, ot))

    def dumpCCall(self, source, call_string):
        source << ('%s _ret_ = %s;' % (self.getCType(), call_string, ))

    def dumpCReturn(self, source):
        decl, is_const = parseType(self.cxx_type)
        cc = 'const_cast<%s*>' % decl.cname()
        source << "_ret_val->tag = %d;" % getTag(self, decl)
        if isinstance(self.cxx_type, bc.LValueReferenceType):
            source << "_ret_val->impl = %s(&(_ret_));" % cc
            source << "_ret_val->ref = self;"
            source << "_ret_val->is_ref = YES;"
        elif isinstance(self.cxx_type, bc.PointerType):
            source << "_ret_val->impl = %s(_ret_);" % cc
            source << "_ret_val->ref = self;"
            source << "_ret_val->is_ref = YES;"
        else:
            source << "_ret_val->impl = new %s(_ret_);" % (decl.cname(), )
            source << "_ret_val->is_ref = NO;"
        source << "return _ret_val;"


class CXXConstructorReturnConverter(return_converter.ReturnConverter):

    def dumpCCall(self, source, call_string):
        decl, is_const = parseType(self.cxx_type)
        i = bw.objc.If("self = [super init]")
        i << "self->tag = %d;" % getTag(self, decl)
        i << "self->impl = %s;" % call_string
        i << "self->is_ref = NO;"
        source << i

    def dumpCReturn(self, source):
        source << "return self;"


class CXXConstructorConverter(function_converter.FunctionConverter):

    @classmethod
    def check(klass, creator, decl):
        if type(decl) is bc.CXXConstructorDecl:
            return klass(creator, decl)

    def isStatic(self):
        return False

    def getName(self):
        return "init"

    def getReturnConverter(self):
        return CXXConstructorReturnConverter(
            self.creator, bc.RecordType(self.decl.parent), self)

    def getCCallString(self):
        l = map(lambda x: x.getCCall(), self.arg_converters)
        return 'new %s(%s)' % (self.decl.path, ', '.join(l))


class CXXGetterConverter(function_converter.FunctionConverter):

    def isStatic(self):
        return False

    # def isPrivate(self):
    #     return True

    def getCCallString(self):
        return "self.i->%s" % self.decl.field_name


class CXXSetterConverter(function_converter.FunctionConverter):

    def __init__(self, *args, **kw):
        super(CXXSetterConverter, self).__init__(*args, **kw)
        self.arg_converters[0].with_id = False

    def isStatic(self):
        return False

    # def isPrivate(self):
    #     return True

    def dumpCCallImpl(self, source):
        l = map(lambda x: x.getCCall(), self.arg_converters)
        source << "self.i->%s = %s;" % (self.decl.field_name, l[0])


class CXXMethodConverter(function_converter.FunctionConverter):
    @classmethod
    def check(klass, creator, decl):
        if type(decl) is bc.CXXMethodDecl:
            return klass(creator, decl)

    def isStatic(self):
        return self.decl.isStatic

    def getCCallString(self):
        if self.isStatic():
            return super(CXXMethodConverter, self).getCCallString()
        l = map(lambda x: x.getCCall(), self.arg_converters)
        return 'self.i->%s(%s)' % (self.decl.name, ', '.join(l))


class ClassPlugin(plugin.Plugin):

    def linkStart(self):
        self.classes = set()
        self.class_indexes = {}

    def resolveFilter(self, decl_or_type):
        decl, is_const = parseType(decl_or_type)
        return isinstance(decl, bc.RecordDecl)

    def resolveClass(self, decl):
        template_args = []
        # print("-" * 80)
        # print(decl)
        # decl.show()
        if hasattr(decl, 'decl') and isinstance(decl.decl, bc.ClassTemplateSpecializationDecl):
            template_args = decl.decl.templateArgs
        decl, is_const = parseType(decl)
        l = decl.path.split('::')
        if is_const:
            l[-1] = 'Const' + l[-1]
        # if len(l) == 1:
        l[0] = self.creator.settings['global_prefix'] + l[0]
        if template_args:
            for i in template_args:
                _, n = self.creator.resolveClass(i.type)
                l.append(n)

        n = '_'.join(l)
        return BridgeClass, n

    def __getConverter(self, l, *args):
        for i in l:
            r = i(self.creator, *args)
            if r:
                return r

    def getFunctionConverter(self, func_decl):
        l = [CXXConstructorConverter.check,
             CXXMethodConverter.check, ]
        # self.__setRecord(arg_decl)
        return self.__getConverter(l, func_decl)

    def getArgConverter(self, arg_decl, func_conv):
        l = [ClassArgConverter.check, ]
        # self.__setRecord(arg_decl)
        return self.__getConverter(l, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        l = [ClassReturnConverter.check, ]
        # self.__setRecord(ret_type)
        return self.__getConverter(l, ret_type, func_conv)

    def declare(self, decl):
        if not isinstance(decl, bc.RecordDecl):
            return False
        if decl.describedClassTemplate is not None:
            return False
        if decl.access != "public" and decl.access != "none":
            return False

        cc = bc.RecordType(decl, isConstQualified=True)
        nc = bc.RecordType(decl, isConstQualified=False)
        cc = self.creator.getClass(cc)
        nc = self.creator.getClass(nc)

        cc.setImpl(decl)
        nc.addBase(cc)
        nc.priority = 10

        for i in self.listAllMethods(decl, const=True):
            conv = self.creator.getFunctionConverter(i)
            cc.addFunction(conv)

        for i in self.listAllMethods(decl, const=False):
            conv = self.creator.getFunctionConverter(i)
            nc.addFunction(conv)

        for field in self.listAllFields(decl):
            ft = field.type
            if isinstance(ft, bc.SubstTemplateTypeParmType):
                ft = ft.sugar

            if (isinstance(base.eraseTypedef(ft), bc.BuiltinType) or
                    isinstance(base.eraseTypedef(ft), bc.EnumType)):
                rt = ft
            else:
                rt = bc.LValueReferenceType(ft,
                                            isConstQualified=True)

            f = CXXGetterDecl("%s::get_%s" % (decl.path, field.name),
                              None, rt, [], decl)
            f.field_name = field.name
            gconv = CXXGetterConverter(self.creator, f)
            cc.addFunction(gconv)

            if not (isinstance(base.eraseTypedef(ft), bc.BuiltinType) or
                    isinstance(base.eraseTypedef(ft), bc.EnumType)):
                rt = bc.LValueReferenceType(
                    ft,
                    isConstQualified=False)

                f = CXXGetterDecl("%s::get_%s" % (decl.path, field.name),
                                  None, rt, [], decl)
                f.field_name = field.name
                gconv = CXXGetterConverter(self.creator, f)
                nc.addFunction(gconv)

            f = CXXSetterDecl("%s::set_%s" % (decl.path, field.name),
                              None, bc.BuiltinType("void"), [bc.ParmVarDecl(
                                  "arg",
                                  ft), ], decl)

            f.field_name = field.name
            sconv = CXXSetterConverter(self.creator, f)
            nc.addFunction(sconv)
            t = gconv.return_converter.getObjCType()
            if not gconv.return_converter.isValid():
                continue

            if gconv.isValid():
                cc.addProperty(
                    objc_class.Property(
                        t, field.name, getter=gconv.getName(),
                        other_attribs='assign, nonatomic'))
                gname = gconv.getName()
            else:
                gname = None

            if sconv.isValid():
                # t = sconv.arg_converters[0].getObjCType()
                t = gconv.return_converter.getObjCType()
                nc.addProperty(
                    objc_class.Property(
                        t, field.name, getter=gname,
                        setter=sconv.getName(),
                        other_attribs='assign, nonatomic'))

        if False and self.hasCopyConstructor(decl):
            f = CXXCopyDecl(decl.path + "::__copy__", None,
                            bc.RecordType(decl), [], decl)
            conv = self.creator.getFunctionConverter(f)
            cc.addFunction(conv)
            f = CXXAssignOperatorDecl(decl.path + "::__assign__",
                                      None,
                                      bc.BuiltinType("void"),
                                      [bc.ParmVarDecl(
                                          "arg",
                                          bc.LValueReferenceType(bc.RecordType(
                                              decl,
                                              isConstQualified=True)), ), ],
                                      decl)
            conv = self.creator.getFunctionConverter(f)
            nc.addFunction(conv)
        return True

    def hook(self, decl_or_type):
        d, isc = parseType(decl_or_type)
        if not d:
            return
        self.classes.add(d)
        self.class_indexes[d] = len(self.class_indexes)

    def linkEnd(self):
        l = sorted(self.classes, key=lambda x: x.path)
        # m = {}
        # for idx, decl in enumerate(l):
        #     m[decl] = idx
        # self.class_indexes = m

        processed = []
        tmp_map = {}
        while True:
            l = list(self.classes.difference(processed))
            if not l:
                break

            # self.class_indexes = {}
            # for decl in l:
            #     self.class_indexes[decl] = len(self.class_indexes)

            for decl in l:
                cc = bc.RecordType(decl, isConstQualified=True)
                nc = bc.RecordType(decl, isConstQualified=False)
                cc = self.creator.getClass(cc)
                nc = self.creator.getClass(nc)

                if True or cc.funcs:
                    ccp = self.creator.getClass(
                        'Api_' + cc.name, objc_class.ObjCProtocol)
                    map(ccp.addFunction, cc.funcs)
                    cc.addProtocol(ccp)

                else:
                    ccp = None
                if True or nc.funcs:
                    ncp = self.creator.getClass(
                        'Api_' + nc.name, objc_class.ObjCProtocol)
                    map(ncp.addFunction, nc.funcs)
                    nc.addProtocol(ncp)
                else:
                    ncp = None
                tmp_map[decl] = cc, nc, ccp, ncp

                if decl.access != "public" and decl.access != "none":
                    cc.setValid(False)
                    nc.setValid(False)
                if not self.hasPublicDefaultConstructor(decl):
                    cc.hasDelete(False)

                cc.addBase(self.creator.getBaseClass())
                cc.setImpl(decl)
                nc.addBase(cc)
                nc.priority = 10
            processed += l

        for decl in tmp_map:
            bases = self.listBases(decl)
            cc, nc, ccp, ncp = tmp_map[decl]
            for b in bases:
                if b in tmp_map:
                    if tmp_map[b][2]:
                        cc.addProtocol(tmp_map[b][2])
                    if tmp_map[b][3]:
                        nc.addProtocol(tmp_map[b][3])

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

    def listChildren(self, decl):
        children = []
        for i in self.classes:
            l = self.listBases(i)
            if decl in l:
                children.append(i)
        children.sort(key=lambda x: x.path)
        return children

    def hasPublicDefaultConstructor(self, decl):
        if (decl.hasDefaultConstructor and
                (not decl.hasUserDeclaredConstructor)):
            flag = True
            for c in decl.ctors:
                if len(c.params) == 0:
                    flag = False
                    p = c.access
            if flag:
                return True
            return p == 'public' and (not decl.isAbstract)
        else:
            p = None
            for c in decl.ctors:
                if len(c.params) == 0:
                    p = c.access
            return p == 'public' and (not decl.isAbstract)

    def listAllMethods(self, decl, const=False):
        bases = self.listBases(decl)
        declared = set()
        overriden = set()
        if not const:
            if (decl.hasDefaultConstructor and
                    (not decl.hasUserDeclaredConstructor)):
                flag = True
                for c in decl.ctors:
                    if len(c.params) == 0:
                        flag = False
                if flag and (not decl.isAbstract):
                    declared.add(
                        bc.CXXConstructorDecl(decl.path, None, bc.BuiltinType(
                            "void"), [], decl))
            # declared.update(decl.ctors)
        for d in [decl] + bases:
            for i in d.methods:
                if d is not decl and isinstance(i, bc.CXXConstructorDecl):
                    continue
                if const and isinstance(i, bc.CXXConstructorDecl):
                    continue
                if decl.isAbstract and isinstance(i, bc.CXXConstructorDecl):
                    continue
                if i.access != "public":
                    continue
                if ((const is not None) and (i.isConst ^ const)):
                    continue
                if i.name.startswith('operator'):
                    continue
                declared.add(i)
                map(overriden.add, i.overridden_methods)

        declared.difference_update(overriden)
        m = list(declared)
        return sorted(m, key=lambda x: x.path)

    def listAllFields(self, decl):
        bases = self.listBases(decl)
        fields = []
        for d in [decl] + bases:
            for i in d.fields:
                if i.access != "public":
                    continue
                fields.append(i)
        return sorted(fields, key=lambda x: x.path)

    def hasCopyConstructor(self, decl):
        # for i in dir(decl):
        #     print i, '=>', getattr(decl, i)
        return True
