/**
 * Copyright Shogo Sawai
 * @file extractor_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:31:33
 */
#include "extractor.hpp"

#include "util.hpp"

std::string Extractor::parseDecl(const clang::Decl *decl, bool deep) {
    deep |= full_mode;
    if (decl == nullptr) {
        return util::getUSRPrefix();
    }

    std::string usr = util::getDeclUSR(decl);

    {
        auto pi = processed_decls.find(decl);
        if (pi != processed_decls.end()) {
            if (pi->second || (!deep)) {
                return usr;
            }
        }
        processed_decls[decl] = deep;
    }
    std::shared_ptr<Json> o;
    auto usr_iter = usr_map.find(usr);
    if (usr_iter != usr_map.end()) {
        o = usr_map[usr];
    } else {
        o = Json::mkObject();
    }

    usr_map[usr] = o;
    o->set(CLASS_STRING, "Decl");
    // o->set("isInvalidDecl", decl->isInvalidDecl());
    o->set("isImplicit", decl->isImplicit());
    // o->set("isTemplateDecl", decl->isTemplateDecl());
    // o->set("isReferenced", decl->isReferenced());
    // o->set("isThisDeclarationReferenced", decl->isThisDeclarationReferenced());
    switch (decl->getAccess()) {
        case clang::AccessSpecifier::AS_public:
            o->set("access", "public");
            break;
        case clang::AccessSpecifier::AS_protected:
            o->set("access", "protected");
            break;
        case clang::AccessSpecifier::AS_private:
            o->set("access", "private");
            break;
        case clang::AccessSpecifier::AS_none:
            o->set("access", "none");
            break;
    }
    bool processed = true;
    if (clang::isa<clang::AccessSpecDecl>(decl)) {
        processed &= parseAccessSpecDecl(
            clang::dyn_cast<clang::AccessSpecDecl>(decl), o, deep);
    } else if (clang::isa<clang::BlockDecl>(decl)) {
        processed &= parseBlockDecl(clang::dyn_cast<clang::BlockDecl>(decl), o, deep);
    } else if (clang::isa<clang::CapturedDecl>(decl)) {
        processed &=
            parseCapturedDecl(clang::dyn_cast<clang::CapturedDecl>(decl), o, deep);
    } else if (clang::isa<clang::ClassScopeFunctionSpecializationDecl>(decl)) {
        processed &= parseClassScopeFunctionSpecializationDecl(
            clang::dyn_cast<clang::ClassScopeFunctionSpecializationDecl>(decl),
            o, deep);
    } else if (clang::isa<clang::EmptyDecl>(decl)) {
        processed &= parseEmptyDecl(clang::dyn_cast<clang::EmptyDecl>(decl), o, deep);
    } else if (clang::isa<clang::ExternCContextDecl>(decl)) {
        processed &= parseExternCContextDecl(
            clang::dyn_cast<clang::ExternCContextDecl>(decl), o, deep);
    } else if (clang::isa<clang::FileScopeAsmDecl>(decl)) {
        processed &= parseFileScopeAsmDecl(
            clang::dyn_cast<clang::FileScopeAsmDecl>(decl), o, deep);
    } else if (clang::isa<clang::FriendDecl>(decl)) {
        processed &=
            parseFriendDecl(clang::dyn_cast<clang::FriendDecl>(decl), o, deep);
    } else if (clang::isa<clang::FriendTemplateDecl>(decl)) {
        processed &= parseFriendTemplateDecl(
            clang::dyn_cast<clang::FriendTemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::ImportDecl>(decl)) {
        processed &=
            parseImportDecl(clang::dyn_cast<clang::ImportDecl>(decl), o, deep);
    } else if (clang::isa<clang::LinkageSpecDecl>(decl)) {
        processed &= parseLinkageSpecDecl(
            clang::dyn_cast<clang::LinkageSpecDecl>(decl), o, deep);
    } else if (clang::isa<clang::NamedDecl>(decl)) {
        processed &= parseNamedDecl(clang::dyn_cast<clang::NamedDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCPropertyImplDecl>(decl)) {
        processed &= parseObjCPropertyImplDecl(
            clang::dyn_cast<clang::ObjCPropertyImplDecl>(decl), o, deep);
    } else if (clang::isa<clang::OMPThreadPrivateDecl>(decl)) {
        processed &= parseOMPThreadPrivateDecl(
            clang::dyn_cast<clang::OMPThreadPrivateDecl>(decl), o, deep);
    } else if (clang::isa<clang::PragmaCommentDecl>(decl)) {
        processed &= parsePragmaCommentDecl(
            clang::dyn_cast<clang::PragmaCommentDecl>(decl), o, deep);
    } else if (clang::isa<clang::PragmaDetectMismatchDecl>(decl)) {
        processed &= parsePragmaDetectMismatchDecl(
            clang::dyn_cast<clang::PragmaDetectMismatchDecl>(decl), o, deep);
    } else if (clang::isa<clang::StaticAssertDecl>(decl)) {
        processed &= parseStaticAssertDecl(
            clang::dyn_cast<clang::StaticAssertDecl>(decl), o, deep);
    } else if (clang::isa<clang::TranslationUnitDecl>(decl)) {
        processed &= parseTranslationUnitDecl(
            clang::dyn_cast<clang::TranslationUnitDecl>(decl), o, deep);
    }
    if (!processed) {
        std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << " Unsupported."
                  << std::endl;
        decl->dump();
        std::cerr << "========================================================="
                  << std::endl;
    }
    return usr;
}

bool Extractor::parseAccessSpecDecl(const clang::AccessSpecDecl *decl,
                                    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseBlockDecl(const clang::BlockDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseCapturedDecl(const clang::CapturedDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseClassScopeFunctionSpecializationDecl(
    const clang::ClassScopeFunctionSpecializationDecl *decl,
    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseEmptyDecl(const clang::EmptyDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseExternCContextDecl(const clang::ExternCContextDecl *decl,
                                        const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseFileScopeAsmDecl(const clang::FileScopeAsmDecl *decl,
                                      const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseFriendDecl(const clang::FriendDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "FriendDecl");
    o->set("friendDecl", parseDecl(decl->getFriendDecl(), deep));
    return true;
}

bool Extractor::parseFriendTemplateDecl(const clang::FriendTemplateDecl *decl,
                                        const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseImportDecl(const clang::ImportDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseLinkageSpecDecl(const clang::LinkageSpecDecl *decl,
                                     const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseObjCPropertyImplDecl(const clang::ObjCPropertyImplDecl *decl,
                                          const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseOMPThreadPrivateDecl(const clang::OMPThreadPrivateDecl *decl,
                                          const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parsePragmaCommentDecl(const clang::PragmaCommentDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parsePragmaDetectMismatchDecl(
    const clang::PragmaDetectMismatchDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseStaticAssertDecl(const clang::StaticAssertDecl *decl,
                                      const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseTranslationUnitDecl(const clang::TranslationUnitDecl *decl,
                                         const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
