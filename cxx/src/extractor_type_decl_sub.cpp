/**
 * Copyright Shogo Sawai
 * @file extractor_type_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:51:10
 */
#include "extractor.hpp"

bool Extractor::parseTypeDecl(const clang::TypeDecl *decl,
                              const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "TypeDecl");

    if (clang::isa<clang::TagDecl>(decl)) {
        processed &= parseTagDecl(clang::dyn_cast<clang::TagDecl>(decl), o, deep);
    } else if (clang::isa<clang::TemplateTypeParmDecl>(decl)) {
        processed &= parseTemplateTypeParmDecl(
            clang::dyn_cast<clang::TemplateTypeParmDecl>(decl), o, deep);
    } else if (clang::isa<clang::TypedefNameDecl>(decl)) {
        processed &= parseTypedefNameDecl(
            clang::dyn_cast<clang::TypedefNameDecl>(decl), o, deep);
    } else if (clang::isa<clang::UnresolvedUsingTypenameDecl>(decl)) {
        processed &= parseUnresolvedUsingTypenameDecl(
            clang::dyn_cast<clang::UnresolvedUsingTypenameDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseTemplateTypeParmDecl(
    const clang::TemplateTypeParmDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "TemplateTypeParmDecl");
    o->set("wasDeclaredWithTypename", decl->wasDeclaredWithTypename());
    o->set("hasDefaultArgument", decl->hasDefaultArgument());
    if (decl->hasDefaultArgument()) {
        o->set("getDefaultArgument", parseQualType(decl->getDefaultArgument(), deep));
    }
    o->set("depth", Json::mkInt(decl->getDepth()));
    o->set("index", Json::mkInt(decl->getIndex()));
    o->set("isParameterPack", decl->isParameterPack());
    return true;
}
bool Extractor::parseTypedefNameDecl(const clang::TypedefNameDecl *decl,
                                     const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "TypedefNameDecl");
    o->set("isModed", decl->isModed());
    o->set("underlyingType", parseQualType(decl->getUnderlyingType(), deep));
    if (clang::isa<clang::ObjCTypeParamDecl>(decl)) {
        processed &= parseObjCTypeParamDecl(
            clang::dyn_cast<clang::ObjCTypeParamDecl>(decl), o, deep);
    } else if (clang::isa<clang::TypeAliasDecl>(decl)) {
        processed &=
            parseTypeAliasDecl(clang::dyn_cast<clang::TypeAliasDecl>(decl), o, deep);
    } else if (clang::isa<clang::TypedefDecl>(decl)) {
        processed &=
            parseTypedefDecl(clang::dyn_cast<clang::TypedefDecl>(decl), o, deep);
    }

    return processed;
}
bool Extractor::parseUnresolvedUsingTypenameDecl(
    const clang::UnresolvedUsingTypenameDecl *decl,
    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseObjCTypeParamDecl(const clang::ObjCTypeParamDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseTypeAliasDecl(const clang::TypeAliasDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep) {
    return true;
}
bool Extractor::parseTypedefDecl(const clang::TypedefDecl *decl,
                                 const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "TypedefDecl");
    return true;
}
