/**
 * Copyright Shogo Sawai
 * @file extractor_tag_decl_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 12:59:47
 */
#include "extractor.hpp"

bool Extractor::parseTagDecl(const clang::TagDecl *decl,
                             const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "TagDecl");
    if (clang::isa<clang::EnumDecl>(decl)) {
        processed &=
            parseEnumDecl(clang::dyn_cast<clang::EnumDecl>(decl), o, deep);
    } else if (clang::isa<clang::RecordDecl>(decl)) {
        processed &=
            parseRecordDecl(clang::dyn_cast<clang::RecordDecl>(decl), o, deep);
    }
    return processed;
}

bool Extractor::parseEnumDecl(const clang::EnumDecl *decl,
                              const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "EnumDecl");
    o->set("isScoped", decl->isScoped());
    o->set("isScopedUsingClassTag", decl->isScopedUsingClassTag());
    o->set("isFixed", decl->isFixed());
    o->set("isComplete", decl->isComplete());
    auto enumerators = Json::mkArray();
    for (auto &&iter : decl->enumerators()) {
        enumerators->add(parseDecl(iter, deep));
    }
    o->set("enumerators", enumerators);
    return true;
}
bool Extractor::parseRecordDecl(const clang::RecordDecl *decl,
                                const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "RecordDecl");
    if (deep) {

        o->set("hasFlexibleArrayMember", decl->hasFlexibleArrayMember());
        o->set("isAnonymousStructOrUnion", decl->isAnonymousStructOrUnion());
        o->set("hasObjectMember", decl->hasObjectMember());
        o->set("hasVolatileMember", decl->hasVolatileMember());
        o->set("hasLoadedFieldsFromExternalStorage",
               decl->hasLoadedFieldsFromExternalStorage());
        o->set("isInjectedClassName", decl->isInjectedClassName());
        o->set("isLambda", decl->isLambda());
        o->set("isCapturedRecord", decl->isCapturedRecord());

        auto fields = Json::mkArray();
        for (auto &&field : decl->fields()) {
            fields->add(parseDecl(field, deep));
        }
        o->set("fields", fields);
    }

    if (clang::isa<clang::CXXRecordDecl>(decl)) {
        processed &= parseCXXRecordDecl(
            clang::dyn_cast<clang::CXXRecordDecl>(decl), o, deep);
    }
    return processed;
}
bool Extractor::parseCXXRecordDecl(const clang::CXXRecordDecl *decl,
                                   const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "CXXRecordDecl");
    if (!decl->hasDefinition()) {
        if (clang::isa<clang::ClassTemplateSpecializationDecl>(decl)) {
            processed &= parseClassTemplateSpecializationDecl(
                clang::dyn_cast<clang::ClassTemplateSpecializationDecl>(decl),
                o, deep);
        }
        return processed;
    }

    // std::cerr << "--------------------------------------------------------------------------------" << std::endl;
    // decl->dump();
    // std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << std::endl;

    o->set("hasDefaultConstructor", decl->hasDefaultConstructor());
    o->set("hasMoveConstructor", decl->hasMoveConstructor());
    if (deep) {
        o->set("hasFriends", decl->hasFriends());
        o->set("hasSimpleMoveConstructor", decl->hasSimpleMoveConstructor());
        o->set("hasSimpleMoveAssignment", decl->hasSimpleMoveAssignment());
        o->set("hasSimpleDestructor", decl->hasSimpleDestructor());
        o->set("needsImplicitDefaultConstructor",
               decl->needsImplicitDefaultConstructor());
        o->set("hasUserDeclaredConstructor",
               decl->hasUserDeclaredConstructor());
        o->set("hasUserProvidedDefaultConstructor",
               decl->hasUserProvidedDefaultConstructor());
        o->set("hasUserDeclaredCopyConstructor",
               decl->hasUserDeclaredCopyConstructor());
        o->set("needsImplicitDefaultConstructor",
               decl->needsImplicitCopyConstructor());
        o->set("needsOverloadResolutionForCopyConstructor",
               decl->needsOverloadResolutionForCopyConstructor());
        o->set("implicitCopyConstructorHasConstParam",
               decl->implicitCopyConstructorHasConstParam());
        o->set("hasCopyConstructorWithConstParam",
               decl->hasCopyConstructorWithConstParam());
        o->set("hasUserDeclaredMoveOperation",
               decl->hasUserDeclaredMoveOperation());
        o->set("hasUserDeclaredCopyConstructor",
               decl->hasUserDeclaredMoveConstructor());
        o->set("hasUserDeclaredCopyAssignment",
               decl->hasUserDeclaredCopyAssignment());
        o->set("needsImplicitCopyAssignment",
               decl->needsImplicitCopyAssignment());
        o->set("needsOverloadResolutionForCopyAssignment",
               decl->needsOverloadResolutionForCopyAssignment());
        o->set("implicitCopyAssignmentHasConstParam",
               decl->implicitCopyAssignmentHasConstParam());
        o->set("hasCopyAssignmentWithConstParam",
               decl->hasCopyAssignmentWithConstParam());
        o->set("hasUserDeclaredMoveAssignment",
               decl->hasUserDeclaredMoveAssignment());
        o->set("hasMoveAssignment", decl->hasMoveAssignment());
        o->set("needsImplicitMoveAssignment",
               decl->needsImplicitMoveAssignment());
        o->set("needsOverloadResolutionForMoveAssignment",
               decl->needsOverloadResolutionForMoveAssignment());
        o->set("hasUserDeclaredDestructor", decl->hasUserDeclaredDestructor());
        o->set("needsImplicitDestructor", decl->needsImplicitDestructor());
        o->set("needsOverloadResolutionForDestructor",
               decl->needsOverloadResolutionForDestructor());
        o->set("isLambda", decl->isLambda());
        o->set("isGenericLambda", decl->isGenericLambda());
        o->set("isAggregate", decl->isAggregate());
        o->set("hasInClassInitializer", decl->hasInClassInitializer());
        o->set("hasUninitializedReferenceMember",
               decl->hasUninitializedReferenceMember());
        o->set("isPOD", decl->isPOD());
        o->set("isCLike", decl->isCLike());
        o->set("isEmpty", decl->isEmpty());
        o->set("isPolymorphic", decl->isPolymorphic());
        o->set("isAbstract", decl->isAbstract());
        o->set("isStandardLayout", decl->isStandardLayout());
        o->set("hasMutableFields", decl->hasMutableFields());
        o->set("hasVariantMembers", decl->hasVariantMembers());
        o->set("hasTrivialDefaultConstructor",
               decl->hasTrivialDefaultConstructor());
        o->set("hasNonTrivialDefaultConstructor",
               decl->hasNonTrivialDefaultConstructor());
        o->set("hasConstexprNonCopyMoveConstructor",
               decl->hasConstexprNonCopyMoveConstructor());
        o->set("defaultedDefaultConstructorIsConstexpr",
               decl->defaultedDefaultConstructorIsConstexpr());
        o->set("hasConstexprDefaultConstructor",
               decl->hasConstexprDefaultConstructor());
        o->set("hasTrivialCopyConstructor", decl->hasTrivialCopyConstructor());
        o->set("hasNonTrivialCopyConstructor",
               decl->hasNonTrivialCopyConstructor());
        o->set("hasTrivialMoveConstructor", decl->hasTrivialMoveConstructor());
        o->set("hasNonTrivialMoveConstructor",
               decl->hasNonTrivialMoveConstructor());
        o->set("hasTrivialCopyAssignment", decl->hasTrivialCopyAssignment());
        o->set("hasNonTrivialCopyAssignment",
               decl->hasNonTrivialCopyAssignment());
        o->set("hasTrivialMoveAssignment", decl->hasTrivialMoveAssignment());
        o->set("hasNonTrivialMoveAssignment",
               decl->hasNonTrivialMoveAssignment());
        o->set("hasTrivialDestructor", decl->hasTrivialDestructor());
        o->set("hasNonTrivialDestructor", decl->hasNonTrivialDestructor());
        o->set("hasIrrelevantDestructor", decl->hasIrrelevantDestructor());
        o->set("hasNonLiteralTypeFieldsOrBases",
               decl->hasNonLiteralTypeFieldsOrBases());
        o->set("isTriviallyCopyable", decl->isTriviallyCopyable());
        o->set("isTrivial", decl->isTrivial());
        o->set("isLiteral", decl->isLiteral());
        o->set("mayBeAbstract", decl->mayBeAbstract());
        // o->set("default_constructor", Json::mkNull());

        auto bases = Json::mkArray();
        auto vbases = Json::mkArray();
        auto methods = Json::mkArray();
        auto ctors = Json::mkArray();
        auto friends = Json::mkArray();
        for (auto &&iter : decl->bases()) {
            bases->add(parseCXXBaseSpecifier(iter, deep));
        }
        for (auto &&iter : decl->vbases()) {
            vbases->add(parseCXXBaseSpecifier(iter, deep));
        }
        for (auto &&iter : decl->methods()) {
            methods->add(parseDecl(iter, deep));
        }
        for (auto &&iter : decl->ctors()) {
            ctors->add(parseDecl(iter, deep));
        }

        for (auto &&iter : decl->friends()) {
            friends->add(parseDecl(iter, deep));
        }

        //     for (auto &&iter : captures){
        // }
        o->set("bases", bases);
        o->set("vbases", vbases);
        o->set("methods", methods);
        o->set("ctors", ctors);
        o->set("friends", friends);
        o->set("destructor", parseDecl(decl->getDestructor(), deep));
        // std::cerr << decl->getGenericLambdaTemplateParameterList() <<
        // std::endl;
        // std::cerr << decl->getDescribedClassTemplate() << std::endl;
        // std::cerr << decl->getTemplateInstantiationPattern() << std::endl;

        o->set("describedClassTemplate",
               parseDecl(decl->getDescribedClassTemplate(), deep));

        switch (decl->getTemplateSpecializationKind()) {
            case clang::TemplateSpecializationKind::TSK_Undeclared:
                o->set("templateSpecializationKind", "Undeclared");
                break;
            case clang::TemplateSpecializationKind::TSK_ImplicitInstantiation:
                o->set("templateSpecializationKind", "ImplicitInstantiation");
                break;
            case clang::TemplateSpecializationKind::TSK_ExplicitSpecialization:
                o->set("templateSpecializationKind", "ExplicitSpecialization");
                break;
            case clang::TemplateSpecializationKind::
                TSK_ExplicitInstantiationDeclaration:
                o->set("templateSpecializationKind",
                       "ExplicitInstantiationDeclaration");
                break;
            case clang::TemplateSpecializationKind::
                TSK_ExplicitInstantiationDefinition:
                o->set("templateSpecializationKind",
                       "ExplicitInstantiationDefinition");
                break;
        }
    }

    if (clang::isa<clang::ClassTemplateSpecializationDecl>(decl)) {
        processed &= parseClassTemplateSpecializationDecl(
            clang::dyn_cast<clang::ClassTemplateSpecializationDecl>(decl), o,
            deep);
    }
    return processed;
}
bool Extractor::parseClassTemplateSpecializationDecl(
    const clang::ClassTemplateSpecializationDecl *decl,
    const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "ClassTemplateSpecializationDecl");
    o->set("isExplicitSpecialization", decl->isExplicitSpecialization());
    o->set("isExplicitInstantiationOrSpecialization",
           decl->isExplicitInstantiationOrSpecialization());
    auto args = Json::mkArray();
    for (auto &&i : decl->getTemplateArgs().asArray()) {
        args->add(parseTemplateArgument(&i, deep));
    }
    o->set("templateArgs", args);

    if (clang::isa<clang::ClassTemplatePartialSpecializationDecl>(decl)) {
        processed &= parseClassTemplatePartialSpecializationDecl(
            clang::dyn_cast<clang::ClassTemplatePartialSpecializationDecl>(
                decl),
            o, deep);
    }
    return processed;
}
bool Extractor::parseClassTemplatePartialSpecializationDecl(
    const clang::ClassTemplatePartialSpecializationDecl *decl,
    const std::shared_ptr<Json> &o, bool deep) {
    return false;
}
