/**
 * Copyright (c)
 * @file extractor.hpp
 * @brief
 * @author Shogo Sawai (sawai@sizebook.co.jp)
 * @date 2015-11-19 17:31:46
 */
#ifndef EXTRACTOR_HPP_
#define EXTRACTOR_HPP_

#include <clang/AST/LocInfoType.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <set>

#include "json.hpp"

#define CLASS_STRING ("class")

class Extractor : public clang::RecursiveASTVisitor<Extractor> {
 public:
    Extractor() : ast_context(nullptr), full_mode(false) {}
    void setASTContext(clang::ASTContext *_ast_context) {
        ast_context = _ast_context;
        results.clear();
        usr_map.clear();
        processed_decls.clear();
    }
    void setSourceFilename(const std::string &filename) { source = filename; }

    bool VisitEnumDecl(clang::EnumDecl *decl);
    bool VisitRecordDecl(clang::RecordDecl *decl);
    bool VisitFunctionDecl(clang::FunctionDecl *decl);

    std::shared_ptr<Json> getResults();
    std::shared_ptr<Json> getUsrMap();

 private:
    bool declsInSourceFile(clang::Decl *decl) const;

    std::string parseDecl(const clang::Decl *decl, bool deep);
    bool parseAccessSpecDecl(const clang::AccessSpecDecl *decl,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseBlockDecl(const clang::BlockDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseCapturedDecl(const clang::CapturedDecl *decl,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseClassScopeFunctionSpecializationDecl(
        const clang::ClassScopeFunctionSpecializationDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseEmptyDecl(const clang::EmptyDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseExternCContextDecl(const clang::ExternCContextDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseFileScopeAsmDecl(const clang::FileScopeAsmDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep);
    bool parseFriendDecl(const clang::FriendDecl *decl,
                         const std::shared_ptr<Json> &o, bool deep);
    bool parseFriendTemplateDecl(const clang::FriendTemplateDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseImportDecl(const clang::ImportDecl *decl,
                         const std::shared_ptr<Json> &o, bool deep);
    bool parseLinkageSpecDecl(const clang::LinkageSpecDecl *decl,
                              const std::shared_ptr<Json> &o, bool deep);
    bool parseNamedDecl(const clang::NamedDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCPropertyImplDecl(const clang::ObjCPropertyImplDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep);
    bool parseOMPThreadPrivateDecl(const clang::OMPThreadPrivateDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep);
    bool parsePragmaCommentDecl(const clang::PragmaCommentDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parsePragmaDetectMismatchDecl(
        const clang::PragmaDetectMismatchDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseStaticAssertDecl(const clang::StaticAssertDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep);
    bool parseTranslationUnitDecl(const clang::TranslationUnitDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep);

    bool parseLabelDecl(const clang::LabelDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseNamespaceAliasDecl(const clang::NamespaceAliasDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseNamespaceDecl(const clang::NamespaceDecl *decl,
                            const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCCompatibleAliasDecl(
        const clang::ObjCCompatibleAliasDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCContainerDecl(const clang::ObjCContainerDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCMethodDecl(const clang::ObjCMethodDecl *decl,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCPropertyDecl(const clang::ObjCPropertyDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep);
    bool parseTemplateDecl(const clang::TemplateDecl *decl,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseTypeDecl(const clang::TypeDecl *decl,
                       const std::shared_ptr<Json> &o, bool deep);
    bool parseUsingDecl(const clang::UsingDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseUsingDirectiveDecl(const clang::UsingDirectiveDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseUsingShadowDecl(const clang::UsingShadowDecl *decl,
                              const std::shared_ptr<Json> &o, bool deep);
    bool parseValueDecl(const clang::ValueDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);

    bool parseObjCCategoryDecl(const clang::ObjCCategoryDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCImplDecl(const clang::ObjCImplDecl *decl,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCInterfaceDecl(const clang::ObjCInterfaceDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCProtocolDecl(const clang::ObjCProtocolDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep);

    bool parseBuiltinTemplateDecl(const clang::BuiltinTemplateDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseRedeclarableTemplateDecl(
        const clang::RedeclarableTemplateDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseTemplateTemplateParmDecl(
        const clang::TemplateTemplateParmDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);

    bool parseTagDecl(const clang::TagDecl *decl,
                      const std::shared_ptr<Json> &o, bool deep);
    bool parseTemplateTypeParmDecl(const clang::TemplateTypeParmDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep);
    bool parseTypedefNameDecl(const clang::TypedefNameDecl *decl,
                              const std::shared_ptr<Json> &o, bool deep);
    bool parseUnresolvedUsingTypenameDecl(
        const clang::UnresolvedUsingTypenameDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);

    bool parseDeclaratorDecl(const clang::DeclaratorDecl *decl,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseEnumConstantDecl(const clang::EnumConstantDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep);
    bool parseIndirectFieldDecl(const clang::IndirectFieldDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseOMPDeclareReductionDecl(
        const clang::OMPDeclareReductionDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseUnresolvedUsingValueDecl(
        const clang::UnresolvedUsingValueDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);

    bool parseObjCCategoryImplDecl(const clang::ObjCCategoryImplDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCImplementationDecl(const clang::ObjCImplementationDecl *decl,
                                     const std::shared_ptr<Json> &o, bool deep);

    bool parseClassTemplateDecl(const clang::ClassTemplateDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseFunctionTemplateDecl(const clang::FunctionTemplateDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep);
    bool parseTypeAliasTemplateDecl(const clang::TypeAliasTemplateDecl *decl,
                                    const std::shared_ptr<Json> &o, bool deep);
    bool parseVarTemplateDecl(const clang::VarTemplateDecl *decl,
                              const std::shared_ptr<Json> &o, bool deep);

    bool parseEnumDecl(const clang::EnumDecl *decl,
                       const std::shared_ptr<Json> &o, bool deep);
    bool parseRecordDecl(const clang::RecordDecl *decl,
                         const std::shared_ptr<Json> &o, bool deep);
    bool parseCXXRecordDecl(const clang::CXXRecordDecl *decl,
                            const std::shared_ptr<Json> &o, bool deep);
    bool parseClassTemplateSpecializationDecl(
        const clang::ClassTemplateSpecializationDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseClassTemplatePartialSpecializationDecl(
        const clang::ClassTemplatePartialSpecializationDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);

    bool parseObjCTypeParamDecl(const clang::ObjCTypeParamDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseTypeAliasDecl(const clang::TypeAliasDecl *decl,
                            const std::shared_ptr<Json> &o, bool deep);
    bool parseTypedefDecl(const clang::TypedefDecl *decl,
                          const std::shared_ptr<Json> &o, bool deep);

    bool parseFieldDecl(const clang::FieldDecl *decl,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseFunctionDecl(const clang::FunctionDecl *decl,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseMSPropertyDecl(const clang::MSPropertyDecl *decl,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseNonTypeTemplateParmDecl(
        const clang::NonTypeTemplateParmDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseVarDecl(const clang::VarDecl *decl,
                      const std::shared_ptr<Json> &o, bool deep);

    bool parseObjCAtDefsFieldDecl(const clang::ObjCAtDefsFieldDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCIvarDecl(const clang::ObjCIvarDecl *decl,
                           const std::shared_ptr<Json> &o, bool deep);

    bool parseCXXMethodDecl(const clang::CXXMethodDecl *decl,
                            const std::shared_ptr<Json> &o, bool deep);
    bool parseCXXConstructorDecl(const clang::CXXConstructorDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseCXXConversionDecl(const clang::CXXConversionDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseCXXDestructorDecl(const clang::CXXDestructorDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);

    bool parseImplicitParamDecl(const clang::ImplicitParamDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseOMPCapturedExprDecl(const clang::OMPCapturedExprDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseParmVarDecl(const clang::ParmVarDecl *decl,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseVarTemplateSpecializationDecl(
        const clang::VarTemplateSpecializationDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseVarTemplatePartialSpecializationDecl(
        const clang::VarTemplatePartialSpecializationDecl *decl,
        const std::shared_ptr<Json> &o, bool deep);

    std::shared_ptr<Json> parseQualType(const clang::QualType &type, bool deep);
    bool parseType(const clang::Type *type, const std::shared_ptr<Json> &o, bool deep);
    bool parseAdjustedType(const clang::AdjustedType *type,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseArrayType(const clang::ArrayType *type,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parseAtomicType(const clang::AtomicType *type,
                         const std::shared_ptr<Json> &o, bool deep);
    bool parseAttributedType(const clang::AttributedType *type,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseAutoType(const clang::AutoType *type,
                       const std::shared_ptr<Json> &o, bool deep);
    bool parseBlockPointerType(const clang::BlockPointerType *type,
                               const std::shared_ptr<Json> &o, bool deep);
    bool parseBuiltinType(const clang::BuiltinType *type,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseComplexType(const clang::ComplexType *type,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseDecltypeType(const clang::DecltypeType *type,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseDependentSizedExtVectorType(
        const clang::DependentSizedExtVectorType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseFunctionType(const clang::FunctionType *type,
                           const std::shared_ptr<Json> &o, bool deep);
    bool parseInjectedClassNameType(const clang::InjectedClassNameType *type,
                                    const std::shared_ptr<Json> &o, bool deep);
    bool parseLocInfoType(const clang::LocInfoType *type,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseMemberPointerType(const clang::MemberPointerType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCObjectPointerType(const clang::ObjCObjectPointerType *type,
                                    const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCObjectType(const clang::ObjCObjectType *type,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parsePackExpansionType(const clang::PackExpansionType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseParenType(const clang::ParenType *type,
                        const std::shared_ptr<Json> &o, bool deep);
    bool parsePipeType(const clang::PipeType *type,
                       const std::shared_ptr<Json> &o, bool deep);
    bool parsePointerType(const clang::PointerType *type,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseReferenceType(const clang::ReferenceType *type,
                            const std::shared_ptr<Json> &o, bool deep);
    bool parseSubstTemplateTypeParmPackType(
        const clang::SubstTemplateTypeParmPackType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseSubstTemplateTypeParmType(
        const clang::SubstTemplateTypeParmType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseTagType(const clang::TagType *type,
                      const std::shared_ptr<Json> &o, bool deep);
    bool parseTemplateTypeParmType(const clang::TemplateTypeParmType *type,
                                   const std::shared_ptr<Json> &o, bool deep);
    bool parseTypedefType(const clang::TypedefType *type,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseTypeOfExprType(const clang::TypeOfExprType *type,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseTypeOfType(const clang::TypeOfType *type,
                         const std::shared_ptr<Json> &o, bool deep);
    // bool parseTypeWithKeyword(const clang::TypeWithKeyword *type, const
    // std::shared_ptr<Json> &o, bool deep);
    bool parseUnaryTransformType(const clang::UnaryTransformType *type,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseUnresolvedUsingType(const clang::UnresolvedUsingType *type,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseVectorType(const clang::VectorType *type,
                         const std::shared_ptr<Json> &o, bool deep);
    bool parseTemplateSpecializationType(
        const clang::TemplateSpecializationType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseDecayedType(const clang::DecayedType *type,
                          const std::shared_ptr<Json> &o, bool deep);
    bool parseConstantArrayType(const clang::ConstantArrayType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseDependentSizedArrayType(
        const clang::DependentSizedArrayType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseIncompleteArrayType(const clang::IncompleteArrayType *type,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseVariableArrayType(const clang::VariableArrayType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    // bool parseDependentDeclType(const clang::DependentDeclType *type, const
    // std::shared_ptr<Json> &o, bool deep);
    bool parseFunctionNoProtoType(const clang::FunctionNoProtoType *type,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseFunctionProtoType(const clang::FunctionProtoType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCInterfaceType(const clang::ObjCInterfaceType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseObjCObjectTypeImpl(const clang::ObjCObjectTypeImpl *type,
                                 const std::shared_ptr<Json> &o, bool deep);
    bool parseLValueReferenceType(const clang::LValueReferenceType *type,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseRValueReferenceType(const clang::RValueReferenceType *type,
                                  const std::shared_ptr<Json> &o, bool deep);
    bool parseEnumType(const clang::EnumType *type,
                       const std::shared_ptr<Json> &o, bool deep);
    bool parseRecordType(const clang::RecordType *type,
                         const std::shared_ptr<Json> &o, bool deep);
    bool parseDependentTypeOfExprType(
        const clang::DependentTypeOfExprType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseDependentNameType(const clang::DependentNameType *type,
                                const std::shared_ptr<Json> &o, bool deep);
    bool parseElaboratedType(const clang::ElaboratedType *type,
                             const std::shared_ptr<Json> &o, bool deep);
    bool parseDependentUnaryTransformType(
        const clang::DependentUnaryTransformType *type,
        const std::shared_ptr<Json> &o, bool deep);
    bool parseExtVectorType(const clang::ExtVectorType *type,
                            const std::shared_ptr<Json> &o, bool deep);

    std::shared_ptr<Json> parseCXXBaseSpecifier(
        const clang::CXXBaseSpecifier &bs, bool deep);
    std::shared_ptr<Json> parseIdentifier(const clang::IdentifierInfo *ii, bool deep);
    std::shared_ptr<Json> parseExpr(const clang::Expr *expr, bool deep);
    std::shared_ptr<Json> parseTemplateArgument(
        const clang::TemplateArgument *ta, bool deep);
    std::shared_ptr<Json> parseExtParameterInfo(
        const clang::FunctionProtoType::ExtParameterInfo &epi, bool deep);
    std::shared_ptr<Json> parseFunctionTemplateSpecializationInfo(
        const clang::FunctionTemplateSpecializationInfo *fts, bool deep);

 private:
    std::set<std::string> results;
    std::map<std::string, std::shared_ptr<Json>> usr_map;
    std::map<const void *, bool> processed_decls;

    clang::ASTContext *ast_context;
    std::string source;
    bool full_mode;
};

#endif  // EXTRACTOR_HPP_
