# coding: utf-8
import sys
import json
import inspect
import StringIO
import re


class T(object):

    def show(self, fp=sys.stdout):
        for i in dir(self):
            if i.startswith('_'):
                continue
            print >> fp, i, '=>', getattr(self, i)


class ClangRoot(object):

    def __init__(self, *args, **kw):
        super(ClangRoot, self).__init__()
        self.type = self.__class__.__name__

    def _update(self, attrs, **kw):
        for key, default_value in attrs:
            setattr(self, key, kw.get(key, default_value))

    def copy(self, m={}):
        n = self.__class__()
        m[self] = n
        for key in dir(self):
            if key.startswith('_'):
                continue
            v = getattr(self, key)
            try:
                v = m[v]
            except:
                if isinstance(v, ClangRoot):
                    v = v.copy(m)
            setattr(n, key, v)
        return n

    def shallowCopy(self, m={}):
        n = self.__class__()
        m[self] = n
        for key in dir(self):
            if key.startswith('_'):
                continue
            v = getattr(self, key)
            try:
                v = m[v]
            except:
                if (isinstance(v, ClangRoot) and
                        not isinstance(v, Decl)):
                    v = v.shallowCopy(m)
            setattr(n, key, v)
        return n

    def show(self, fp=sys.stdout):
        for i in dir(self):
            if i.startswith('_'):
                continue
            print >> fp, i, '=>', getattr(self, i)


class Decl(ClangRoot):
    __ATTRS = [("isImplicit", False), ]

    def __init__(self, *args, **kw):
        super(Decl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)


class AccessSpecDecl(Decl):
    pass


class BlockDecl(Decl):
    pass


class CapturedDecl(Decl):
    pass


class ClassScopeFunctionSpecializationDecl(Decl):
    pass


class EmptyDecl(Decl):
    pass


class ExternCContextDecl(Decl):
    pass


class FileScopeAsmDecl(Decl):
    pass


class FriendDecl(Decl):
    pass


class FriendTemplateDecl(Decl):
    pass


class ImportDecl(Decl):
    pass


class LinkageSpecDecl(Decl):
    pass


class NamedDecl(Decl):
    __ATTRS = [
        ("name", None),
        ("path", None),
        ("hasLinkage", False),
        ("isHidden", False),
        ("hasExternalFormalLinkage", False),
        ("isExternallyVisible", False),
        ("isLinkageValid", False),
        ("hasLinkageBeenComputed", False),
    ]

    def __init__(self, *args, **kw):
        u"""NamedDecl()
        NamedDecl(path)
        """
        super(NamedDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if args:
            self.name = args[0].split('::')[-1]
            self.path = args[0]

    def __str__(self):
        return "%s:%s" % (self.__class__.__name__, self.name)


class ObjCPropertyImplDecl(Decl):
    pass


class OMPThreadPrivateDecl(Decl):
    pass


class PragmaCommentDecl(Decl):
    pass


class PragmaDetectMismatchDecl(Decl):
    pass


class StaticAssertDecl(Decl):
    pass


class TranslationUnitDecl(Decl):
    pass


class LabelDecl(NamedDecl):
    pass


class NamespaceAliasDecl(NamedDecl):
    pass


class NamespaceDecl(NamedDecl):
    pass


class ObjCCompatibleAliasDecl(NamedDecl):
    pass


class ObjCContainerDecl(NamedDecl):
    pass


class ObjCMethodDecl(NamedDecl):
    pass


class ObjCPropertyDecl(NamedDecl):
    pass


class TemplateDecl(NamedDecl):
    pass


class TypeDecl(NamedDecl):
    pass


class UsingDecl(NamedDecl):
    pass


class UsingDirectiveDecl(NamedDecl):
    pass


class UsingShadowDecl(NamedDecl):
    pass


class ValueDecl(NamedDecl):
    __ATTRS = [("type", None), ("isWeak", False), ]

    def __init__(self, *args, **kw):
        u"""ValueDecl()
        ValueDecl(path, type)
        """
        super(ValueDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if args:
            self.type = args[1]


class ObjCCategoryDecl(ObjCContainerDecl):
    pass


class ObjCImplDecl(ObjCContainerDecl):
    pass


class ObjCInterfaceDecl(ObjCContainerDecl):
    pass


class ObjCProtocolDecl(ObjCContainerDecl):
    pass


class BuiltinTemplateDecl(TemplateDecl):
    pass


class RedeclarableTemplateDecl(TemplateDecl):
    pass


class TemplateTemplateParmDecl(TemplateDecl):
    pass


class TagDecl(TypeDecl):
    pass


class TemplateTypeParmDecl(TypeDecl):
    pass


class TypedefNameDecl(TypeDecl):
    pass


class UnresolvedUsingTypenameDecl(TypeDecl):
    pass


class DeclaratorDecl(ValueDecl):
    pass


class EnumConstantDecl(ValueDecl):
    def cname(self):
        return self.path


class IndirectFieldDecl(ValueDecl):
    pass


class OMPDeclareReductionDecl(ValueDecl):
    pass


class UnresolvedUsingValueDecl(ValueDecl):
    pass


class ObjCCategoryImplDecl(ObjCImplDecl):
    pass


class ObjCImplementationDecl(ObjCImplDecl):
    pass


class ClassTemplateDecl(RedeclarableTemplateDecl):
    pass


class FunctionTemplateDecl(RedeclarableTemplateDecl):
    pass


class TypeAliasTemplateDecl(RedeclarableTemplateDecl):
    pass


class VarTemplateDecl(RedeclarableTemplateDecl):
    pass


class EnumDecl(TagDecl):
    __ATTRS = [
        ("isScoped", True),
        ("isScopedUsingClassTag", True),
        ("isFixed", False),
        ("isComplete", False),
        ("enumerators", []),
    ]

    def __init__(self, *args, **kw):
        u"""EnumDecl()
        EnumDecl(path)
        """
        super(EnumDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)

    def cname(self):
        return self.path

    def __str__(self):
        sio = StringIO.StringIO()
        sio.write(super(EnumDecl, self).__str__())
        sio.write(', enumerators:(%s)' %
                  (','.join(map(str, self.enumerators))))
        return sio.getvalue()


class RecordDecl(TagDecl):
    __ATTRS = [
        ("hasFlexibleArrayMember", False),
        ("isAnonymousStructOrUnion", False),
        ("hasObjectMember", False),
        ("hasVolatileMember", False),
        ("hasLoadedFieldsFromExternalStorage", False),
        ("isInjectedClassName", False),
        ("isLambda", False),
        ("isCapturedRecord", False),
        ("fields", []),
    ]

    def __init__(self, *args, **kw):
        u"""RecordDecl()
        RecordDecl(path)
        """
        super(RecordDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)


class CXXRecordDecl(RecordDecl):
    __ATTRS = [
        ("hasFriends", False),
        ("hasSimpleMoveConstructor", True),
        ("hasSimpleMoveAssignment", True),
        ("hasSimpleDestructor", True),
        ("hasDefaultConstructor", True),
        ("needsImplicitDefaultConstructor", True),
        ("hasUserDeclaredConstructor", False),
        ("hasUserProvidedDefaultConstructor", False),
        ("hasUserDeclaredCopyConstructor", False),
        ("needsImplicitDefaultConstructor", False),
        ("needsOverloadResolutionForCopyConstructor", False),
        ("implicitCopyConstructorHasConstParam", True),
        ("hasCopyConstructorWithConstParam", True),
        ("hasUserDeclaredMoveOperation", False),
        ("hasUserDeclaredCopyConstructor", False),
        ("hasMoveConstructor", True),
        ("hasUserDeclaredCopyAssignment", False),
        ("needsImplicitCopyAssignment", True),
        ("needsOverloadResolutionForCopyAssignment", False),
        ("implicitCopyAssignmentHasConstParam", True),
        ("hasCopyAssignmentWithConstParam", True),
        ("hasUserDeclaredMoveAssignment", False),
        ("hasMoveAssignment", True),
        ("needsImplicitMoveAssignment", True),
        ("needsOverloadResolutionForMoveAssignment", False),
        ("hasUserDeclaredDestructor", False),
        ("needsImplicitDestructor", True),
        ("needsOverloadResolutionForDestructor", False),
        ("isLambda", False),
        ("isGenericLambda", False),
        ("isAggregate", True),
        ("hasInClassInitializer", False),
        ("hasUninitializedReferenceMember", False),
        ("isPOD", False),
        ("isCLike", False),
        ("isEmpty", True),
        ("isPolymorphic", False),
        ("isAbstract", False),
        ("isStandardLayout", True),
        ("hasMutableFields", False),
        ("hasVariantMembers", False),
        ("hasTrivialDefaultConstructor", True),
        ("hasNonTrivialDefaultConstructor", True),
        ("hasConstexprNonCopyMoveConstructor", True),
        ("defaultedDefaultConstructorIsConstexpr", True),
        ("hasConstexprDefaultConstructor", True),
        ("hasTrivialCopyConstructor", True),
        ("hasNonTrivialCopyConstructor", False),
        ("hasTrivialMoveConstructor", True),
        ("hasNonTrivialMoveConstructor", False),
        ("hasTrivialCopyAssignment", True),
        ("hasNonTrivialCopyAssignment", False),
        ("hasTrivialMoveAssignment", True),
        ("hasNonTrivialMoveAssignment", False),
        ("hasTrivialDestructor", True),
        ("hasNonTrivialDestructor", False),
        ("hasIrrelevantDestructor", True),
        ("hasNonLiteralTypeFieldsOrBases", False),
        ("isTriviallyCopyable", True),
        ("isTrivial", True),
        ("isLiteral", True),
        ("mayBeAbstract", False),
        ("bases", []),
        ("vbases", []),
        ("methods", []),
        ("ctors", []),
        ("friends", []),
        ("destructor", None),
    ]

    def __init__(self, *args, **kw):
        u"""RecordDecl()
        RecordDecl(path)
        """
        super(CXXRecordDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)

    def cname(self):
        return self.path

    def __str__(self):
        sio = StringIO.StringIO()
        sio.write(super(CXXRecordDecl, self).__str__())
        if hasattr(self, 'fields'):
            sio.write(', fields:(%s)' % (','.join(map(str, self.fields))))
        if hasattr(self, 'methods'):
            sio.write(', methods:(%s)' % (','.join(map(str, self.methods))))
        return sio.getvalue()


class ClassTemplateSpecializationDecl(CXXRecordDecl):
    def cname(self):
        a = ','.join(map(lambda x: x.cname(), self.templateArgs))
        return '%s<%s>' % (self.path, a)


class ClassTemplatePartialSpecializationDecl(ClassTemplateSpecializationDecl):
    pass


class ObjCTypeParamDecl(TypedefNameDecl):
    pass


class TypeAliasDecl(TypedefNameDecl):
    pass


class TypedefDecl(TypedefNameDecl):

    def cname(self):
        return self.path

    def __str__(self):
        return str(self.underlyingType)


class FieldDecl(DeclaratorDecl):
    __ATTRS = [
        ("fieldIndex", -1),
        ("isMutable", False),
        ("isBitField", False),
        ("isUnnamedBitfield", False),
        ("isAnonymousStructOrUnion", False),
        ("bitWidthValue", -1),
        ("hasInClassInitializer", False),
        ("hasCapturedVLAType", False),
        ("parent", None),
    ]

    def __init__(self, *args, **kw):
        u"""FieldDecl()
        FieldDecl(path, type, record_decl)
        """
        super(FieldDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if args:
            self.parent = args[2]


class FunctionDecl(DeclaratorDecl):
    __ATTRS = [
        ("isVirtualAsWritten", False),
        ("isPure", False),
        ("isTrivial", False),
        ("isExplicitlyDefaulted", False),
        ("isImplicit", False),
        ("isConstexpr", False),
        ("isDeleted", False),
        ("isMain", False),
        ("isExternC", False),
        ("isInExternCContext", False),
        ("isInExternCXXContext", False),
        ("isGlobal", False),
        ("isNoReturn", False),
        ("isInlineSpecified", False),
        ("isInlined", False),
        ("isFunctionTemplateSpecialization", False),
        ("isTemplateInstantiation", False),
    ]

    def __init__(self, *args, **kw):
        u"""FunctionDecl()
        FunctionDecl(path, type, returnType, params)
        """
        super(FunctionDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if len(args) == 0:
            return
        if not isinstance(args[2], Type):
            raise TypeError("args[0] must be Type")
        for i in args[3]:
            if not isinstance(i, ParmVarDecl):
                raise TypeError(
                    "args[3] must be iterable, element must be ParmVarDecl")
        self.returnType = args[2]
        self.params = args[3]

    def __str__(self):
        return "%s:%s %s(%s)" % (self.__class__.__name__, str(self.returnType),
                                 self.name, ','.join(map(str, self.params)))


class MSPropertyDecl(DeclaratorDecl):
    pass


class NonTypeTemplateParmDecl(DeclaratorDecl):
    pass


class VarDecl(DeclaratorDecl):
    __ATTRS = [
        ("hasLocalStorage", True),
        ("isStaticLocal", False),
        ("hasExternalStorage", False),
        ("hasGlobalStorage ", False),
        ("isExternC", False),
        ("isInExternCContext", False),
        ("isInExternCXXContext", False),
        ("isLocalVarDecl", False),
        ("isLocalVarDeclOrParm", True),
        ("isFunctionOrMethodVarDecl", False),
        ("isStaticDataMember ", False),
        ("isOutOfLine", False),
        ("isFileVarDecl ", False),
        ("hasInit", False),
        ("isInitKnownICE", None),
        ("isInitICE", None),
        ("checkInitIsICE ", None),
        ("init", None),
        ("isDirectInit", False),
        ("isExceptionVariable", False),
        ("isNRVOVariable", False),
        ("isCXXForRangeDecl", False),
        ("isARCPseudoStrong", False),
        ("isConstexpr", False),
        ("isInitCapture", False),
        ("isPreviousDeclInSameBlockScope", False),
    ]

    def __init__(self, *args, **kw):
        u"""VarDecl()
        VarDecl(path, type)
        """
        super(VarDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)


class ObjCAtDefsFieldDecl(FieldDecl):
    pass


class ObjCIvarDecl(FieldDecl):
    pass


class CXXMethodDecl(FunctionDecl):
    __ATTRS = [
        ("isStatic", False),
        ("isInstance", True),
        ("isConst", False),
        ("isVolatile", False),
        ("isVirtual", False),
        ("isUsualDeallocationFunction", False),
        ("isCopyAssignmentOperator", False),
        ("isMoveAssignmentOperator", False),
        ("isUserProvided", True),
        ("hasInlineBody", False),
        ("isLambdaStaticInvoker", False),
        ("overridden_methods", []),
        ("parent", None),
        ("type", None),
    ]

    def __init__(self, *args, **kw):
        u"""CXXMethodDecl()
        CXXMethodDecl(path, type, returnType, params, cxx_record)
        """
        super(CXXMethodDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if args:
            if not isinstance(args[4], CXXRecordDecl):
                raise TypeError()
            self.parent = args[4]


class CXXConstructorDecl(CXXMethodDecl):
    __ATTRS = [
        ("isExplicitSpecified", True),
        ("isExplicit", True),
        ("isDelegatingConstructor", False),
        ("isDefaultConstructor", False),
        ("isCopyConstructor", False),
        ("isMoveConstructor", False),
        ("isCopyOrMoveConstructor", False),
        ("isSpecializationCopyingObject", False),
        ("numCtorInitializers", -1),
        ("inheritedConstructor", -1),
    ]

    def __init__(self, *args, **kw):
        # if len(args):
        #     decl = args[0]
        #     n = decl.name
        #     r = BuiltinType("void")
        #     n = n + '::' + (n.split('::')[-1])
        #     args = args[1]
        #     super(CXXConstructorDecl, self).__init__(decl, r, n, args, **kw)
        # else:
        #     super(CXXConstructorDecl, self).__init__(*args, **kw)
        super(CXXConstructorDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)


class CXXConversionDecl(CXXMethodDecl):
    pass


class CXXDestructorDecl(CXXMethodDecl):
    pass


class ImplicitParamDecl(VarDecl):
    pass


class OMPCapturedExprDecl(VarDecl):
    pass


class ParmVarDecl(VarDecl):
    __ATTRS = [
        ("hasDefaultArg", False),
        ("defaultArg", None),
        ("hasUnparsedDefaultArg", False),
        ("hasUninstantiatedDefaultArg", False),
        ("hasInheritedDefaultArg", False),
        ("originalType", None),
        ("isParameterPack", False),
        ("isObjCMethodParameter", False),
        ("functionScopeDepth", -1),
        ("functionScopeIndex", -1),
    ]

    def __init__(self, *args, **kw):
        u"""ParmVarDecl()
        ParmVarDecl(path, type)
        """
        super(ParmVarDecl, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)

    def __str__(self):
        return ':'.join([super(ParmVarDecl, self).__str__(), str(self.type)])


class VarTemplateSpecializationDecl(VarDecl):
    pass


class VarTemplatePartialSpecializationDecl(VarTemplateSpecializationDecl):
    pass


class Type(ClangRoot):
    __ATTRS = [
        ("isCanonical", True),
        ("isCanonicalAsParam", True),
        ("isNull", False),
        ("isLocalConstQualified", False),
        ("isConstQualified", False),
        ("isLocalRestrictQualified", False),
        ("isRestrictQualified", False),
        ("isLocalVolatileQualified", False),
        ("isVolatileQualified", False),
        ("hasLocalQualifiers", False),
        ("hasQualifiers", False),
        ("hasLocalNonFastQualifiers", False),
        ("isConstant", False),
        ("isPODType", False),
        ("isCXX98PODType", False),
        ("isCXX11PODType", False),
        ("isTrivialType", False),
        ("isTriviallyCopyableType", False),
        ("string", ""),
    ]

    def __init__(self, *args, **kw):
        super(Type, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)


class AdjustedType(Type):
    pass


class ArrayType(Type):
    pass


class AtomicType(Type):
    pass


class AttributedType(Type):
    pass


class AutoType(Type):
    pass


class BlockPointerType(Type):
    pass


class BuiltinType(Type):

    def __init__(self, *args, **kw):
        u"""BuiltinType()
        BuiltinType(spelling)
        """
        super(BuiltinType, self).__init__(*args, **kw)
        if len(args) > 0:
            s = args[0]
            if s.startswith('const '):
                s = s[len('const '):]
                self.isConstQualified = True
            self.spelling = s

    def cname(self):
        return str(self)

    def __str__(self):
        s = ''
        if self.isConstQualified:
            s = 'const '
        return s + self.spelling


class ComplexType(Type):
    pass


class DecltypeType(Type):
    pass


class DependentSizedExtVectorType(Type):
    pass


class FunctionType(Type):
    __ATTRS = [
        ("returnType", None),
        ("hasRegParm", False),
        ("noReturnAttr", False),
        ("isConst", False),
        ("isVolatile", False),
        ("isRestrict", False),
    ]

    def __init__(self, *args, **kw):
        u"""FunctionType()
        FunctionType(returnType)
        """
        super(FunctionType, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if args:
            self.returnType = args[0]


class InjectedClassNameType(Type):
    pass


class LocInfoType(Type):
    pass


class MemberPointerType(Type):
    pass


class ObjCObjectPointerType(Type):
    pass


class ObjCObjectType(Type):
    pass


class PackExpansionType(Type):
    pass


class ParenType(Type):
    pass


class PipeType(Type):
    pass


class PointerType(Type):
    __ATTRS = [("pointeeType", None), ]

    def __init__(self, *args, **kw):
        u"""PointerType()
        PointerType(pointeeType)
        """
        super(PointerType, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if len(args) > 0:
            self.pointeeType = args[0]

    def cname(self):
        if self.isConstQualified:
            return self.pointeeType.cname() + ' const *'
        return self.pointeeType.cname() + '*'

    def __str__(self):
        if self.isConstQualified:
            return str(self.pointeeType) + ' const *'
        return str(self.pointeeType) + '*'


class ReferenceType(Type):
    __ATTRS = [("pointeeType", None), ]

    def __init__(self, *args, **kw):
        u"""ReferenceType()
        ReferenceType(pointeeType)
        """
        super(ReferenceType, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if len(args) > 0:
            self.pointeeType = args[0]


class SubstTemplateTypeParmPackType(Type):
    pass


class SubstTemplateTypeParmType(Type):
    def cname(self):
        return self.sugar.cname()

    def __str__(self):
        return '(SubstTemplateTypeParmType[%s])' % self.cname()


class TagType(Type):
    __ATTRS = [("decl", None), ("isBeingDefined", False), ]

    def __init__(self, *args, **kw):
        u"""TagType()
        TagType(decl)
        """
        super(TagType, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if len(args) > 0:
            self.decl = args[0]


class TemplateTypeParmType(Type):
    pass


class TypedefType(Type):

    def cname(self):
        return self.decl.cname()

    def __str__(self):
        s = ''
        if self.isConstQualified:
            s = 'const '
        return 'typedef(%s(%s))' % (self.string, s + str(self.decl))


class TypeOfExprType(Type):
    pass


class TypeOfType(Type):
    pass


class TypeWithKeyword(Type):
    pass


class UnaryTransformType(Type):
    pass


class UnresolvedUsingType(Type):
    pass


class VectorType(Type):
    pass


class TemplateSpecializationType(Type):

    def cname(self):
        c = ''
        if self.isConstQualified:
            c = 'const '
        return '%s%s<%s>' % (c, self.sugar.cname(),
                             ','.join(map(lambda x: x.cname(), self.args)))

    def __str__(self):
        c = ''
        if self.isConstQualified:
            c = 'const '
        return ('TemplateSpecializationType(%s%s<%s>)' %
                (c, str(self.sugar), ','.join(map(str, self.args))))


class DecayedType(AdjustedType):
    pass


class ConstantArrayType(ArrayType):
    def cname(self):
        return '%s [%d]' % (self.elementType.cname(), self.size)

    def __str__(self):
        return "ConstantArray(%s)" % self.cname()


class DependentSizedArrayType(ArrayType):
    pass


class IncompleteArrayType(ArrayType):
    pass


class VariableArrayType(ArrayType):
    pass


class DependentDeclType(DecltypeType):
    pass


class FunctionNoProtoType(FunctionType):
    pass


class FunctionProtoType(FunctionType):
    __ATTRS = [
        ("hasExceptionSpec", False),
        ("hasDynamicExceptionSpec", False),
        ("hasNoexceptExceptionSpec", False),
        ("hasDependentExceptionSpec", False),
        ("isVariadic", False),
        ("isTemplateVariadic", False),
        ("hasTrailingReturn", False),
        ("param_types", []),
        ("exceptions", []),
        ("extParameterInfos", []),
    ]

    def __init__(self, *args, **kw):
        u"""FunctionProtoType()
        FunctionProtoType(returnType, param_types)
        """
        super(FunctionProtoType, self).__init__(*args, **kw)
        self._update(self.__ATTRS, **kw)
        if args:
            self.param_types = args[1]

    def cname(self):
        return str(self)

    def __str__(self):
        return '%s (%s)' % (str(self.returnType), ', '.join(
            map(str, self.param_types)))


class ObjCInterfaceType(ObjCObjectType):
    pass


class ObjCObjectTypeImpl(ObjCObjectType):
    pass


class LValueReferenceType(ReferenceType):

    def cname(self):
        return self.pointeeType.cname() + '&'

    def __str__(self):
        return str(self.pointeeType) + '&'


class RValueReferenceType(ReferenceType):

    def cname(self):
        return self.pointeeType.cname() + '&&'

    def __str__(self):
        return str(self.pointeeType) + '&&'


class EnumType(TagType):
    def cname(self):
        return self.decl.path

    def __str__(self):
        return 'EnumType(%s)' % self.decl.path


class RecordType(TagType):
    # def __init__(self, *args, **kw):
    #     super(RecordType, self).__init__(*args, **kw)
    #     if len(args) > 0:
    #         if not isinstance(args[0], RecordDecl):
    #             raise Exception()
    #         self.record = args[0]
    #         self.spelling = args[0].name

    def cname(self):
        c = ''
        if self.isConstQualified:
            c = 'const '
        return (c + self.decl.path)

    def __str__(self):
        return "RecordType(%s)" % self.cname()


class DependentTypeOfExprType(TypeOfExprType):
    pass


class DependentNameType(TypeWithKeyword):
    pass


class ElaboratedType(TypeWithKeyword):

    def cname(self):
        c = ''
        if self.isConstQualified:
            c = 'const '
        return c + self.namedType.cname()

    def __str__(self):
        c = ''
        if self.isConstQualified:
            c = 'const '
        return "ElaboratedType(%s%s)" % (c, str(self.namedType))


class DependentUnaryTransformType(UnaryTransformType):
    pass


class ExtVectorType(VectorType):
    pass


class TemplateArgument(ClangRoot):

    def cname(self):
        if self.kind != "Type":
            return self.value
            # return "TemplateArgument::kind::%s" % self.kind
        return self.type.cname()

    def __str__(self):
        return "TemplateArgument(%s)" % str(self.type)


class CXXBaseSpecifier(ClangRoot):
    pass


class FunctionProtoType_colon__colon_ExtParameterInfo(ClangRoot):
    pass


class IdentifierInfo(ClangRoot):
    pass


class Expr(ClangRoot):
    pass


vector_regex = re.compile('std::.*::vector')
string_regex = re.compile('std::.*::(basic_)?string')


def is_std_vector(decl):
    return (
        decl.path == 'std::vector' or
        vector_regex.match(decl.path))


def is_std_string(decl):
    return (
        decl.path == 'std::string' or
        string_regex.match(decl.path))


builtin_types = {
    "void": ("v", "void"),
    "char": ("i", "SignedChar"),
    "unsigned char": ("i", "UnsignedChar"),
    "short": ("i", "SignedShort"),
    "unsigned short": ("i", "UnsignedShort"),
    "int": ("i", "SignedInt"),
    "unsigned int": ("i", "UnsignedInt"),
    "long": ("i", "SignedLong"),
    "unsigned long": ("i", "UnsignedLong"),
    "long long": ("i", "SignedLongLong"),
    "unsigned long long": ("i", "UnsignedLongLong"),
    "float": ("f", "float_width"),
    "double": ("f", "double_width"),
    "long double": ("f", "long_double_width"),
    "bool": ("i", "SignedChar"),
}


def _getUsr(usr, d, usr_prefix):
    if ((isinstance(usr, str) or isinstance(usr, unicode)) and
            usr.startswith(usr_prefix)):
        return d.get(usr, None)
    return usr


class AppendToList:

    def __init__(self, target, value, usr_prefix):
        self.__t = target
        self.__v = value
        self.__p = usr_prefix

    def __call__(self, d):
        self.__t.append(_getUsr(self.__v, d, self.__p))


class SetAttr:

    def __init__(self, target, key, value, usr_prefix):
        self.__t = target
        self.__k = key
        self.__v = value
        self.__p = usr_prefix

    def __call__(self, d):
        setattr(self.__t, self.__k, _getUsr(self.__v, d, self.__p))


def _recursive(value,
               tcm={},
               type_conv=True,
               default_class=T,
               usr_prefix=None):
    cbs = []
    if isinstance(value, list):
        o = list()
        for i in value:
            j, cb = _recursive(i, tcm, type_conv, default_class, usr_prefix)
            cbs.append(AppendToList(o, j, usr_prefix))
            cbs.extend(cb)
    elif isinstance(value, dict):
        if type_conv:
            if 'class' not in value:
                print "class not found !!!!", value
            o = tcm.get(value['class'], default_class)()
            if isinstance(o, default_class):
                print "default class !!!!!!!", value
        else:
            o = default_class()
        for k, v in value.items():
            if k.startswith(usr_prefix):
                continue
            j, cb = _recursive(v, tcm, type_conv, default_class, usr_prefix)
            cbs.append(SetAttr(o, k, j, usr_prefix))
            cbs.extend(cb)
    else:
        o = value
    return o, cbs


def isSameJson(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        if (set(a.keys()).difference(b.keys()) or
                set(b.keys()).difference(a.keys())):
            a.update(b)
            return
            # raise Exception()
        for k in a.keys():
            isSameJson(a[k], b[k])
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            print "ERROR", repr(a) + " diff " + repr(b)
            a.extend(b)
            # raise Exception()
        for i, j in zip(a, b):
            isSameJson(i, j)
    else:
        if a != b:
            print "ERROR", repr(a) + " diff " + repr(b)
            # raise Exception(repr(a) + " diff " + repr(b))


def mergeJson(*args):
    r = {
        'diagnostics': [],
        'includes': [],
        'declarations': set(),
        'target_info': None,
        'usr_map': {},
        'usr_prefix': None,
    }
    for a in args:
        r['diagnostics'].extend(a['diagnostics'])
        r['includes'].append(a['filename'])
        r['declarations'].update(a['declarations'])
        if r['target_info'] is None:
            r['target_info'] = a['target_info']
        else:
            isSameJson(r['target_info'], a['target_info'])

        if r['usr_prefix'] is None:
            r['usr_prefix'] = a['usr_prefix']
        elif r['usr_prefix'] != a['usr_prefix']:
            raise Exception()

        for k, v in a['usr_map'].items():
            if k in r['usr_map']:
                isSameJson(r['usr_map'][k], v)
            else:
                r['usr_map'][k] = v
    return r


def loadJson(d, type_map=None):
    d = dict(d)
    if type_map is None:
        type_map = {}
        m = sys.modules[__name__]
        for i in dir(m):
            v = getattr(m, i)
            if not inspect.isclass(v):
                continue
            key = i.replace('_colon_', ':')
            type_map[key] = v

    usr_prefix = d['usr_prefix']
    d.pop('usr_prefix')
    usr_map = {}
    cbs = []
    for usr, info in d['usr_map'].items():
        o, cb = _recursive(info, type_map, usr_prefix=usr_prefix)
        usr_map[usr] = o
        cbs.extend(cb)
    map(lambda x: x(usr_map), cbs)
    dl = map(lambda x: usr_map[x], d['declarations'])
    d.pop('usr_map')
    d.pop('declarations')
    t, cbs = _recursive(d, type_conv=False, usr_prefix=usr_prefix)
    map(lambda x: x(usr_map), cbs)
    t.usr_map = usr_map
    t.declarations = dl
    return t


def main(args):
    ds = map(lambda x: json.loads(open(x).read()), args)
    d = mergeJson(*ds)
    o = loadJson(d)
    print dir(o.declarations[0])
    for d in o.declarations:
        print d
        # print d.return_type.type
    b = BuiltinType("void")
    print b.__class__.__name__
    print b.type


def __entry_point():
    import argparse
    parser = argparse.ArgumentParser(
        description=u'',  # プログラムの説明
    )
    parser.add_argument("args", nargs="*")
    main(parser.parse_args().args)


if __name__ == '__main__':
    __entry_point()
