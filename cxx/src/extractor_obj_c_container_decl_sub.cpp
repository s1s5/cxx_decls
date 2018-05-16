/**
 * Copyright Shogo Sawai
 * @file extractor_obj_c_container_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:46:37
 */
#include "extractor.hpp"

bool Extractor::parseObjCContainerDecl(const clang::ObjCContainerDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    if (clang::isa<clang::ObjCCategoryDecl>(decl)) {
        return parseObjCCategoryDecl(
            clang::dyn_cast<clang::ObjCCategoryDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCImplDecl>(decl)) {
        return parseObjCImplDecl(clang::dyn_cast<clang::ObjCImplDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCInterfaceDecl>(decl)) {
        return parseObjCInterfaceDecl(
            clang::dyn_cast<clang::ObjCInterfaceDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCProtocolDecl>(decl)) {
        return parseObjCProtocolDecl(
            clang::dyn_cast<clang::ObjCProtocolDecl>(decl), o, deep);
    }
    return false;
}

bool Extractor::parseObjCCategoryDecl(const clang::ObjCCategoryDecl *decl,
                                      const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseObjCImplDecl(const clang::ObjCImplDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep) {
    if (clang::isa<clang::ObjCCategoryImplDecl>(decl)) {
        return parseObjCCategoryImplDecl(clang::dyn_cast<clang::ObjCCategoryImplDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCImplementationDecl>(decl)) {
        return parseObjCImplementationDecl(clang::dyn_cast<clang::ObjCImplementationDecl>(decl), o, deep);
    }

    return false;
}
bool Extractor::parseObjCInterfaceDecl(const clang::ObjCInterfaceDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseObjCProtocolDecl(const clang::ObjCProtocolDecl *decl,
                                      const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseObjCCategoryImplDecl(const clang::ObjCCategoryImplDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseObjCImplementationDecl(const clang::ObjCImplementationDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
