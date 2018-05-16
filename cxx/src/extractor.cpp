/**
 * Copyright 2015 Co. Ltd. sizebook
 * @file extractor.cpp
 * @brief
 * @author Shogo Sawai (sawai@sizebook.co.jp)
 * @date 2015-11-19 17:32:58
 */
#include "extractor.hpp"
#include "util.hpp"

#include <clang/AST/ASTContext.h>
#include <llvm/Support/raw_ostream.h>

#include <iostream>

bool Extractor::VisitEnumDecl(clang::EnumDecl *decl) {
    if (!declsInSourceFile(decl)) {
        return true;
    }

    results.insert(parseDecl(decl, true));

    return true;
}

bool Extractor::VisitRecordDecl(clang::RecordDecl *decl) {
    if (!declsInSourceFile(decl)) {
        return true;
    }

    results.insert(parseDecl(decl, true));

    return true;
}

bool Extractor::VisitFunctionDecl(clang::FunctionDecl *decl) {
    if (!declsInSourceFile(decl)) {
        return true;
    }

    if (clang::isa<clang::CXXMethodDecl>(decl)) {
        return true;
    }

    results.insert(parseDecl(decl, true));

    return true;
}

std::shared_ptr<Json> Extractor::getResults() {
    auto a = Json::mkArray();
    for (auto &&iter : results) {
        a->add(iter);
    }
    return a;
}

std::shared_ptr<Json> Extractor::getUsrMap() {
    auto o = Json::mkObject();
    for (auto &&iter : usr_map) {
        o->objectUpdate(iter.first, iter.second);
    }
    return o;
}

bool Extractor::declsInSourceFile(clang::Decl *decl) const {
    auto sl = decl->getLocation();  // <= SourceLocation
    auto fsl = ast_context->getFullLoc(sl);
    if (source != fsl.getManager().getFilename(fsl).str()) {
        if (source != fsl.getManager().getFilename(fsl.getManager().getExpansionLoc(sl)).str()) {
            return false;
        }
    }
    return true;
}

std::shared_ptr<Json> Extractor::parseCXXBaseSpecifier(
    const clang::CXXBaseSpecifier &bs, bool deep) {
    auto o = Json::mkObject();
    o->set(CLASS_STRING, "CXXBaseSpecifier");
    o->set("type", parseQualType(bs.getType(), deep));
    o->set("isVirtual", bs.isVirtual());
    o->set("isBaseOfClass", bs.isBaseOfClass());
    o->set("isPackExpansion", bs.isPackExpansion());
    o->set("inheritConstructors", bs.getInheritConstructors());
    switch (bs.getAccessSpecifier()) {
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
    return o;
}

std::shared_ptr<Json> Extractor::parseIdentifier(
    const clang::IdentifierInfo *ii, bool deep) {
    auto o = Json::mkObject();
    o->set(CLASS_STRING, "IdentifierInfo");
    o->set("name", ii->getName().str());
    return o;
}

std::shared_ptr<Json> Extractor::parseExpr(const clang::Expr *expr, bool deep) {
    if (expr == nullptr) {
        return Json::mkNull();
    }
    auto o = Json::mkObject();
    o->set(CLASS_STRING, "Expr");
    o->set("type", parseQualType(expr->getType(), deep));
    return o;
}

std::shared_ptr<Json> Extractor::parseTemplateArgument(
    const clang::TemplateArgument *ta, bool deep) {
    auto o = Json::mkObject();
    o->set(CLASS_STRING, "TemplateArgument");
    
    std::string type_str;
    llvm::raw_string_ostream rso(type_str);
    ta->dump(rso);
    o->set("value", rso.str());
    
    switch (ta->getKind()) {
        case clang::TemplateArgument::ArgKind::Null: {
            o->set("kind", "Null");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::Type: {
            o->set("kind", "Type");
            o->set("type", parseQualType(ta->getAsType(), deep));
            break;
        }
        case clang::TemplateArgument::ArgKind::Declaration: {
            o->set("kind", "Declaration");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::NullPtr: {
            o->set("kind", "NullPtr");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::Integral: {
            o->set("kind", "Integral");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::Template: {
            o->set("kind", "Template");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::TemplateExpansion: {
            o->set("kind", "TemplateExpansion");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::Expression: {
            o->set("kind", "Expression");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
        case clang::TemplateArgument::ArgKind::Pack: {
            o->set("kind", "Pack");
            // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;
            break;
        }
    }
    return o;
}

std::shared_ptr<Json> Extractor::parseExtParameterInfo(const clang::FunctionProtoType::ExtParameterInfo &epi, bool deep) {
    auto o = Json::mkObject();
    o->set(CLASS_STRING, "FunctionProtoType::ExtParameterInfo");
    return o;
}

std::shared_ptr<Json> Extractor::parseFunctionTemplateSpecializationInfo(const clang::FunctionTemplateSpecializationInfo *fts, bool deep) {
    auto o = Json::mkObject();
    o->set(CLASS_STRING, "FunctionTemplateSpecialization");
    o->set("template", parseDecl(fts->getTemplate(), deep));
    o->set("isExplicitSpecialization", fts->isExplicitSpecialization());
    o->set("isExplicitInstantiationOrSpecialization", fts->isExplicitInstantiationOrSpecialization());
    switch (fts->getTemplateSpecializationKind()) {
        case clang::TemplateSpecializationKind::TSK_Undeclared:
            o->set("templateSpecializationKind", "Undeclared");
            break;
        case clang::TemplateSpecializationKind::TSK_ImplicitInstantiation:
            o->set("templateSpecializationKind", "ImplicitInstantiation");
            break;
        case clang::TemplateSpecializationKind::TSK_ExplicitSpecialization:
            o->set("templateSpecializationKind", "ExplicitSpecialization");
            break;
        case clang::TemplateSpecializationKind::TSK_ExplicitInstantiationDeclaration:
            o->set("templateSpecializationKind", "ExplicitInstantiationDeclaration");
            break;
        case clang::TemplateSpecializationKind::TSK_ExplicitInstantiationDefinition:
            o->set("templateSpecializationKind", "ExplicitInstantiationDefinition");
            break;
    }
    return o;
}
