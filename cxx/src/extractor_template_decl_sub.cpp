/**
 * Copyright Shogo Sawai
 * @file extractor_template_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:49:25
 */
#include "extractor.hpp"

bool Extractor::parseTemplateDecl(const clang::TemplateDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "TemplateDecl");
    auto template_parameters = Json::mkArray();
    for (auto &&iter : decl->getTemplateParameters()->asArray()) {
        template_parameters->add(parseDecl(iter, deep));
    }
    o->set("templateParameters", template_parameters);
    o->set("templateDecl", parseDecl(decl->getTemplatedDecl(), deep));
    o->set("isConcept", decl->isConcept());

    if (clang::isa<clang::BuiltinTemplateDecl>(decl)) {
        processed &= parseBuiltinTemplateDecl(
            clang::dyn_cast<clang::BuiltinTemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::RedeclarableTemplateDecl>(decl)) {
        processed &= parseRedeclarableTemplateDecl(
            clang::dyn_cast<clang::RedeclarableTemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::TemplateTemplateParmDecl>(decl)) {
        processed &= parseTemplateTemplateParmDecl(
            clang::dyn_cast<clang::TemplateTemplateParmDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseBuiltinTemplateDecl(const clang::BuiltinTemplateDecl *decl,
                                         const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseRedeclarableTemplateDecl(
    const clang::RedeclarableTemplateDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "RedeclarableTemplateDecl");
    if (clang::isa<clang::ClassTemplateDecl>(decl)) {
        processed &= parseClassTemplateDecl(
            clang::dyn_cast<clang::ClassTemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::FunctionTemplateDecl>(decl)) {
        processed &= parseFunctionTemplateDecl(
            clang::dyn_cast<clang::FunctionTemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::TypeAliasTemplateDecl>(decl)) {
        processed &= parseTypeAliasTemplateDecl(
            clang::dyn_cast<clang::TypeAliasTemplateDecl>(decl), o, deep);
    } else if (clang::isa<clang::VarTemplateDecl>(decl)) {
        processed &= parseVarTemplateDecl(
            clang::dyn_cast<clang::VarTemplateDecl>(decl), o, deep);
    }
    return processed;
}
bool Extractor::parseTemplateTemplateParmDecl(
    const clang::TemplateTemplateParmDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseClassTemplateDecl(const clang::ClassTemplateDecl *decl,
                                       const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "ClassTemplateDecl");
    auto specializations = Json::mkArray();
    for (auto &&iter : decl->specializations()) {
        specializations->add(parseDecl(iter, deep));
    }
    o->set("specializations", specializations);
    return true;
}
bool Extractor::parseFunctionTemplateDecl(const clang::FunctionTemplateDecl *decl,
                                          const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "FunctionTemplateDecl");
    o->set("templatedDecl", parseDecl(decl->getTemplatedDecl(), deep));
    o->set("isThisDeclarationADefinition", decl->isThisDeclarationADefinition());

    auto specializations = Json::mkArray();
    for (auto &&i : decl->specializations()) {
        // specializations->add(parseFunctionTemplateSpecializationInfo(i));
        specializations->add(parseDecl(i, deep));
    }
    o->set("specializations", specializations);
    // auto injectedTemplateArgs = Json::mkArray();
    // for (auto &&i : decl->getInjectedTemplateArgs()) {
    //     injectedTemplateArgs->add(parseTemplateArgument(i));
    // }
    // o->set("injectedTemplateArgs", injectedTemplateArgs);
    return true;
}

bool Extractor::parseTypeAliasTemplateDecl(const clang::TypeAliasTemplateDecl *decl,
                                           const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseVarTemplateDecl(const clang::VarTemplateDecl *decl,
                                     const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
