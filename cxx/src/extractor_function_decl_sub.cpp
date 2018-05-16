/**
 * Copyright Shogo Sawai
 * @file extractor_function_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 13:08:20
 */
#include "extractor.hpp"

bool Extractor::parseFunctionDecl(const clang::FunctionDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "FunctionDecl");
    o->set("isVirtualAsWritten", decl->isVirtualAsWritten());
    o->set("isPure", decl->isPure());
    o->set("isTrivial", decl->isTrivial());
    o->set("isExplicitlyDefaulted", decl->isExplicitlyDefaulted());
    o->set("isImplicit", decl->isImplicit());
    o->set("isConstexpr", decl->isConstexpr());
    o->set("isDeleted", decl->isDeleted());
    o->set("isMain", decl->isMain());
    o->set("isExternC", decl->isExternC());
    o->set("isInExternCContext", decl->isInExternCContext());
    o->set("isInExternCXXContext", decl->isInExternCXXContext());
    o->set("isGlobal", decl->isGlobal());
    o->set("isNoReturn", decl->isNoReturn());
    o->set("isInlineSpecified", decl->isInlineSpecified());
    o->set("isInlined", decl->isInlined());
    o->set("isFunctionTemplateSpecialization",
           decl->isFunctionTemplateSpecialization());
    o->set("isTemplateInstantiation", decl->isTemplateInstantiation());

    o->set("returnType", parseQualType(decl->getReturnType(), false));
    auto params = Json::mkArray();
    // for (auto &&iter : decl->params()) {
    for (auto &&iter = decl->param_begin(), end = decl->param_end(); iter != end; iter++) {
        params->add(parseDecl(*iter, deep));
    }
    o->set("params", params);
    if (clang::isa<clang::CXXMethodDecl>(decl)) {
        processed &=
            parseCXXMethodDecl(clang::dyn_cast<clang::CXXMethodDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseCXXMethodDecl(const clang::CXXMethodDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "CXXMethodDecl");

    o->set("isStatic", decl->isStatic());
    o->set("isInstance", decl->isInstance());
    o->set("isConst", decl->isConst());
    o->set("isVolatile", decl->isVolatile());
    o->set("isVirtual", decl->isVirtual());
    o->set("isUsualDeallocationFunction", decl->isUsualDeallocationFunction());
    o->set("isCopyAssignmentOperator", decl->isCopyAssignmentOperator());
    o->set("isMoveAssignmentOperator", decl->isMoveAssignmentOperator());
    o->set("isUserProvided", decl->isUserProvided());
    o->set("hasInlineBody", decl->hasInlineBody());
    o->set("isLambdaStaticInvoker", decl->isLambdaStaticInvoker());

    auto overridden_methods = Json::mkArray();
    for (auto iter = decl->begin_overridden_methods(),
              end = decl->end_overridden_methods();
         iter != end; iter++) {
        overridden_methods->add(parseDecl(*iter, deep));
    }
    o->set("overridden_methods", overridden_methods);

    if (!clang::isa<clang::CXXDestructorDecl>(decl)) {
        o->set("parent", parseDecl(decl->getParent(), deep));
    } else {
        // crashed on MAC
        o->set("parent", parseDecl(decl->getParent(), false));
    }
    // crashed on MAC
    // o->set("type", parseQualType(decl->getThisType(*ast_context)));
    if (clang::isa<clang::CXXConstructorDecl>(decl)) {
        processed &= parseCXXConstructorDecl(
            clang::dyn_cast<clang::CXXConstructorDecl>(decl), o, deep);
    } else if (clang::isa<clang::CXXConversionDecl>(decl)) {
        processed &= parseCXXConversionDecl(
            clang::dyn_cast<clang::CXXConversionDecl>(decl), o, deep);
    } else if (clang::isa<clang::CXXDestructorDecl>(decl)) {
        processed &= parseCXXDestructorDecl(
            clang::dyn_cast<clang::CXXDestructorDecl>(decl), o, deep);
    }
    return processed;
}
bool Extractor::parseCXXConstructorDecl(const clang::CXXConstructorDecl *decl,
                                        const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "CXXConstructorDecl");

    o->set("isExplicitSpecified", decl->isExplicitSpecified());
    o->set("isExplicit", decl->isExplicit());
    o->set("isDelegatingConstructor", decl->isDelegatingConstructor());
    o->set("isDefaultConstructor", decl->isDefaultConstructor());
    o->set("isCopyConstructor", decl->isCopyConstructor());
    o->set("isMoveConstructor", decl->isMoveConstructor());
    o->set("isCopyOrMoveConstructor", decl->isCopyOrMoveConstructor());
    o->set("isSpecializationCopyingObject",
           decl->isSpecializationCopyingObject());
    o->set("numCtorInitializers",
           Json::mkInt(decl->getNumCtorInitializers()));
    o->set("inheritedConstructor",
           parseDecl(decl->getInheritedConstructor().getConstructor(), deep));

    return true;
}
bool Extractor::parseCXXConversionDecl(const clang::CXXConversionDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "CXXConversionDecl");
    o->set("isExplicitSpecified", decl->isExplicitSpecified());
    o->set("isExplicit", decl->isExplicit());
    o->set("conversionType", parseQualType(decl->getConversionType(), false));
    o->set("isLambdaToBlockPointerConversion", decl->isLambdaToBlockPointerConversion());
    return true;
}
bool Extractor::parseCXXDestructorDecl(const clang::CXXDestructorDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "CXXDestructorDecl");
    return true;
}
