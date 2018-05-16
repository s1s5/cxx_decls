/**
 * Copyright Shogo Sawai
 * @file extractor_named_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:41:38
 */
#include "extractor.hpp"
#include "util.hpp"

bool Extractor::parseNamedDecl(const clang::NamedDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "NamedDecl");
    o->set("name", decl->getNameAsString());
    o->set("path", util::getAbsPath(decl));
    o->set("hasLinkage", decl->hasLinkage());
    o->set("isHidden", decl->isHidden());
    // o->set("isCXXClassMember", decl->isCXXClassMember());
    // o->set("isCXXInstanceMember", decl->isCXXInstanceMember());
    o->set("hasExternalFormalLinkage", decl->hasExternalFormalLinkage());
    o->set("isExternallyVisible", decl->isExternallyVisible());
    o->set("isLinkageValid", decl->isLinkageValid());
    o->set("hasLinkageBeenComputed", decl->hasLinkageBeenComputed());
    if (clang::isa<clang::LabelDecl>(decl)) {
        processed &= parseLabelDecl(clang::dyn_cast<clang::LabelDecl>(decl), o, deep);
    } else if (clang::isa<clang::NamespaceAliasDecl>(decl)) {
        processed &= parseNamespaceAliasDecl(
            clang::dyn_cast<clang::NamespaceAliasDecl>(decl), o, deep);
    } else if (clang::isa<clang::NamespaceDecl>(decl)) {
        processed &=
            parseNamespaceDecl(clang::dyn_cast<clang::NamespaceDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCCompatibleAliasDecl>(decl)) {
        processed &= parseObjCCompatibleAliasDecl(
            clang::dyn_cast<clang::ObjCCompatibleAliasDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCContainerDecl>(decl)) {
        processed &= parseObjCContainerDecl(
            clang::dyn_cast<clang::ObjCContainerDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCMethodDecl>(decl)) {
        processed &= parseObjCMethodDecl(
            clang::dyn_cast<clang::ObjCMethodDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCPropertyDecl>(decl)) {
        processed &= parseObjCPropertyDecl(
            clang::dyn_cast<clang::ObjCPropertyDecl>(decl), o, deep);
    } else if (clang::isa<clang::TemplateDecl>(decl)) {
        processed &=
            parseTemplateDecl(clang::dyn_cast<clang::TemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::TypeDecl>(decl)) {
        processed &= parseTypeDecl(clang::dyn_cast<clang::TypeDecl>(decl), o, deep);
    } else if (clang::isa<clang::UsingDecl>(decl)) {
        processed &= parseUsingDecl(clang::dyn_cast<clang::UsingDecl>(decl), o, deep);
    } else if (clang::isa<clang::UsingDirectiveDecl>(decl)) {
        processed &= parseUsingDirectiveDecl(
            clang::dyn_cast<clang::UsingDirectiveDecl>(decl), o, deep);
    } else if (clang::isa<clang::UsingShadowDecl>(decl)) {
        processed &= parseUsingShadowDecl(
            clang::dyn_cast<clang::UsingShadowDecl>(decl), o, deep);
    } else if (clang::isa<clang::ValueDecl>(decl)) {
        processed &= parseValueDecl(clang::dyn_cast<clang::ValueDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseLabelDecl(const clang::LabelDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseNamespaceAliasDecl(const clang::NamespaceAliasDecl *decl,
                                        const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseNamespaceDecl(const clang::NamespaceDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseObjCCompatibleAliasDecl(
    const clang::ObjCCompatibleAliasDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseObjCMethodDecl(const clang::ObjCMethodDecl *decl,
                                    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseObjCPropertyDecl(const clang::ObjCPropertyDecl *decl,
                                      const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseUsingDecl(const clang::UsingDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseUsingDirectiveDecl(const clang::UsingDirectiveDecl *decl,
                                        const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseUsingShadowDecl(const clang::UsingShadowDecl *decl,
                                     const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
