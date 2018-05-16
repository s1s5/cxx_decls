/**
 * Copyright Shogo Sawai
 * @file extractor_declarator_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 13:05:36
 */
#include "extractor.hpp"

bool Extractor::parseDeclaratorDecl(const clang::DeclaratorDecl *decl,
                                    const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "DeclaratorDecl");
    if (clang::isa<clang::FieldDecl>(decl)) {
        processed &= parseFieldDecl(clang::dyn_cast<clang::FieldDecl>(decl), o, deep);
    } else if (clang::isa<clang::FunctionDecl>(decl)) {
        processed &=
            parseFunctionDecl(clang::dyn_cast<clang::FunctionDecl>(decl), o, deep);
    } else if (clang::isa<clang::MSPropertyDecl>(decl)) {
        processed &= parseMSPropertyDecl(
            clang::dyn_cast<clang::MSPropertyDecl>(decl), o, deep);
    } else if (clang::isa<clang::NonTypeTemplateParmDecl>(decl)) {
        processed &= parseNonTypeTemplateParmDecl(
            clang::dyn_cast<clang::NonTypeTemplateParmDecl>(decl), o, deep);
    } else if (clang::isa<clang::VarDecl>(decl)) {
        processed &= parseVarDecl(clang::dyn_cast<clang::VarDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseFieldDecl(const clang::FieldDecl *decl,
                               const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "FieldDecl");

    o->set("fieldIndex", Json::mkInt(decl->getFieldIndex()));
    o->set("isMutable", decl->isMutable());
    o->set("isBitField", decl->isBitField());
    o->set("isUnnamedBitfield", decl->isUnnamedBitfield());
    o->set("isAnonymousStructOrUnion", decl->isAnonymousStructOrUnion());
    if (decl->isBitField()) {
        o->set("bitWidthValue", Json::mkInt(decl->getBitWidthValue(*ast_context)));
    } else {
        o->set("bitWidthValue", Json::mkInt(-1));
    }
    o->set("hasInClassInitializer", decl->hasInClassInitializer());
    o->set("hasCapturedVLAType", decl->hasCapturedVLAType());
    o->set("parent", parseDecl(decl->getParent(), deep));

    if (clang::isa<clang::ObjCAtDefsFieldDecl>(decl)) {
        processed &= parseObjCAtDefsFieldDecl(
            clang::dyn_cast<clang::ObjCAtDefsFieldDecl>(decl), o, deep);
    } else if (clang::isa<clang::ObjCIvarDecl>(decl)) {
        processed &=
            parseObjCIvarDecl(clang::dyn_cast<clang::ObjCIvarDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseMSPropertyDecl(const clang::MSPropertyDecl *decl,
                                    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseNonTypeTemplateParmDecl(
    const clang::NonTypeTemplateParmDecl *decl, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "NonTypeTemplateParmDecl");
    o->set("hasDefaultArgument", decl->hasDefaultArgument());
    if (decl->hasDefaultArgument()) {
        o->set("defaultArgument", parseExpr(decl->getDefaultArgument(), false));
    }
    o->set("defaultArgumentWasInherited", decl->defaultArgumentWasInherited());

    o->set("isParameterPack", decl->isParameterPack());
    o->set("isPackExpansion", decl->isPackExpansion());
    // crashed on MAC
    // o->set("numExpansionTypes", Json::mkInt(decl->getNumExpansionTypes()));
    // auto expansionTypes = Json::mkArray();
    // for (unsigned int i = 0; i < decl->getNumExpansionTypes(); i++) {
    //     expansionTypes->add(parseQualType(decl->getExpansionType(i)));
    // }
    // o->set("expansionTypes", expansionTypes);
    return true;
}

bool Extractor::parseObjCAtDefsFieldDecl(const clang::ObjCAtDefsFieldDecl *decl,
                                         const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
bool Extractor::parseObjCIvarDecl(const clang::ObjCIvarDecl *decl,
                                  const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
