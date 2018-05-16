/**
 * Copyright Shogo Sawai
 * @file extractor_var_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 13:09:44
 */
#include "extractor.hpp"

bool Extractor::parseVarDecl(const clang::VarDecl *decl,
                             const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "VarDecl");
    o->set("hasLocalStorage", decl->hasLocalStorage());
    o->set("isStaticLocal", decl->isStaticLocal());
    o->set("hasExternalStorage", decl->hasExternalStorage());
    o->set("hasGlobalStorage ", decl->hasGlobalStorage());
    o->set("isExternC", decl->isExternC());
    o->set("isInExternCContext", decl->isInExternCContext());
    o->set("isInExternCXXContext", decl->isInExternCXXContext());
    o->set("isLocalVarDecl", decl->isLocalVarDecl());
    o->set("isLocalVarDeclOrParm", decl->isLocalVarDeclOrParm());
    o->set("isFunctionOrMethodVarDecl", decl->isFunctionOrMethodVarDecl());
    o->set("isStaticDataMember ", decl->isStaticDataMember());
    o->set("isOutOfLine", decl->isOutOfLine());
    o->set("isFileVarDecl ", decl->isFileVarDecl());
    o->set("hasInit", decl->hasInit());

    // crash on mac
    // if (decl->hasInit()) {
    //     o->set("isInitKnownICE", decl->isInitKnownICE());
    //     o->set("isInitICE", decl->isInitICE());
    //     o->set("checkInitIsICE ", decl->checkInitIsICE());
    //     o->set("init", parseExpr(decl->getInit()));
    // } else {
    //     o->set("isInitKnownICE", Json::mkNull());
    //     o->set("isInitICE", Json::mkNull());
    //     o->set("checkInitIsICE ", Json::mkNull());
    //     o->set("init", Json::mkNull());
    // }
    
    o->set("isDirectInit", decl->isDirectInit());
    o->set("isExceptionVariable", decl->isExceptionVariable());
    o->set("isNRVOVariable", decl->isNRVOVariable());
    o->set("isCXXForRangeDecl", decl->isCXXForRangeDecl());
    o->set("isARCPseudoStrong", decl->isARCPseudoStrong());
    o->set("isConstexpr", decl->isConstexpr());
    o->set("isInitCapture", decl->isInitCapture());
    o->set("isPreviousDeclInSameBlockScope",
           decl->isPreviousDeclInSameBlockScope());

    if (clang::isa<clang::ImplicitParamDecl>(decl)) {
        processed &= parseImplicitParamDecl(
            clang::dyn_cast<clang::ImplicitParamDecl>(decl), o, deep);
    } else if (clang::isa<clang::OMPCapturedExprDecl>(decl)) {
        processed &= parseOMPCapturedExprDecl(
            clang::dyn_cast<clang::OMPCapturedExprDecl>(decl), o, deep);
    } else if (clang::isa<clang::ParmVarDecl>(decl)) {
        processed &=
            parseParmVarDecl(clang::dyn_cast<clang::ParmVarDecl>(decl), o, deep);
    } else if (clang::isa<clang::VarTemplateSpecializationDecl>(decl)) {
        processed &= parseVarTemplateSpecializationDecl(
            clang::dyn_cast<clang::VarTemplateSpecializationDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseImplicitParamDecl(const clang::ImplicitParamDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseOMPCapturedExprDecl(const clang::OMPCapturedExprDecl *decl,
                                         const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseParmVarDecl(const clang::ParmVarDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "ParmVarDecl");
    o->set("hasDefaultArg", decl->hasDefaultArg());
    if ((!decl->hasUninstantiatedDefaultArg()) && decl->hasDefaultArg()) {
        o->set("defaultArg", parseExpr(decl->getDefaultArg(), false));
    } else {
        o->set("defaultArg", Json::mkNull());
    }
    o->set("hasUnparsedDefaultArg", decl->hasUnparsedDefaultArg());
    o->set("hasUninstantiatedDefaultArg", decl->hasUninstantiatedDefaultArg());
    o->set("hasInheritedDefaultArg", decl->hasInheritedDefaultArg());
    o->set("originalType", parseQualType(decl->getOriginalType(), false));
    o->set("isParameterPack", decl->isParameterPack());
    o->set("isObjCMethodParameter", decl->isObjCMethodParameter());
    o->set("functionScopeDepth", Json::mkInt(decl->getFunctionScopeDepth()));
    o->set("functionScopeIndex", Json::mkInt(decl->getFunctionScopeIndex()));
    return true;
}
bool Extractor::parseVarTemplateSpecializationDecl(
    const clang::VarTemplateSpecializationDecl *decl,
    const std::shared_ptr<Json> &o, bool deep) {
    if (clang::isa<clang::VarTemplatePartialSpecializationDecl>(decl)) {
        return parseVarTemplatePartialSpecializationDecl(
            clang::dyn_cast<clang::VarTemplatePartialSpecializationDecl>(decl),
            o, deep);
    }
    return false;
}
bool Extractor::parseVarTemplatePartialSpecializationDecl(
    const clang::VarTemplatePartialSpecializationDecl *decl,
    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
