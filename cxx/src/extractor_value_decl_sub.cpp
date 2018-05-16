/**
 * Copyright Shogo Sawai
 * @file extractor_value_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:53:32
 */
#include "extractor.hpp"

bool Extractor::parseValueDecl(const clang::ValueDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "ValueDecl");
    o->set("type", parseQualType(decl->getType(), false));
    o->set("isWeak", decl->isWeak());

    if (clang::isa<clang::DeclaratorDecl>(decl)) {
        processed &= parseDeclaratorDecl(clang::dyn_cast<clang::DeclaratorDecl>(decl),
                                   o, deep);
    } else if (clang::isa<clang::EnumConstantDecl>(decl)) {
        processed &= parseEnumConstantDecl(
            clang::dyn_cast<clang::EnumConstantDecl>(decl), o, deep);
    } else if (clang::isa<clang::IndirectFieldDecl>(decl)) {
        processed &= parseIndirectFieldDecl(
            clang::dyn_cast<clang::IndirectFieldDecl>(decl), o, deep);
    } else if (clang::isa<clang::OMPDeclareReductionDecl>(decl)) {
        processed &= parseOMPDeclareReductionDecl(
            clang::dyn_cast<clang::OMPDeclareReductionDecl>(decl), o, deep);
    } else if (clang::isa<clang::UnresolvedUsingValueDecl>(decl)) {
        processed &= parseUnresolvedUsingValueDecl(
            clang::dyn_cast<clang::UnresolvedUsingValueDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseEnumConstantDecl(const clang::EnumConstantDecl *decl,
                                      const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "EnumConstantDecl");
    o->set("value", Json::mkInt(decl->getInitVal().getExtValue()));
    return true;
}
bool Extractor::parseIndirectFieldDecl(const clang::IndirectFieldDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseOMPDeclareReductionDecl(
    const clang::OMPDeclareReductionDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseUnresolvedUsingValueDecl(
    const clang::UnresolvedUsingValueDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
