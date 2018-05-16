/**
 * Copyright Shogo Sawai
 * @file extractor_type_sub.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-14 13:19:49
 */
#include "extractor.hpp"

std::shared_ptr<Json> Extractor::parseQualType(const clang::QualType &qt, bool deep) {
    auto o = Json::mkObject();
    o->set("isCanonical", qt.isCanonical());
    o->set("isCanonicalAsParam", qt.isCanonicalAsParam());
    o->set("isNull", qt.isNull());
    o->set("isLocalConstQualified", qt.isLocalConstQualified());
    o->set("isConstQualified", qt.isConstQualified());
    o->set("isLocalRestrictQualified", qt.isLocalRestrictQualified());
    o->set("isRestrictQualified", qt.isRestrictQualified());
    o->set("isLocalVolatileQualified", qt.isLocalVolatileQualified());
    o->set("isVolatileQualified", qt.isVolatileQualified());
    o->set("hasLocalQualifiers", qt.hasLocalQualifiers());
    o->set("hasQualifiers", qt.hasQualifiers());
    o->set("hasLocalNonFastQualifiers", qt.hasLocalNonFastQualifiers());
    o->set("isConstant", qt.isConstant(*ast_context));
    o->set("isPODType", qt.isPODType(*ast_context));
    o->set("isCXX98PODType", qt.isCXX98PODType(*ast_context));
    o->set("isCXX11PODType", qt.isCXX11PODType(*ast_context));
    o->set("isTrivialType", qt.isTrivialType(*ast_context));
    o->set("isTriviallyCopyableType", qt.isTriviallyCopyableType(*ast_context));
    o->set("string", qt.getAsString());
    parseType(qt.getTypePtr(), o, deep);
    return o;
}

bool Extractor::parseType(const clang::Type *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "Type");
    if (clang::isa<clang::AdjustedType>(type)) {
        processed &= parseAdjustedType(clang::dyn_cast<clang::AdjustedType>(type), o, deep);
    } else if (clang::isa<clang::ArrayType>(type)) {
        processed &= parseArrayType(clang::dyn_cast<clang::ArrayType>(type), o, deep);
    } else if (clang::isa<clang::AtomicType>(type)) {
        processed &= parseAtomicType(clang::dyn_cast<clang::AtomicType>(type), o, deep);
    } else if (clang::isa<clang::AttributedType>(type)) {
        processed &= parseAttributedType(clang::dyn_cast<clang::AttributedType>(type), o, deep);
    } else if (clang::isa<clang::AutoType>(type)) {
        processed &= parseAutoType(clang::dyn_cast<clang::AutoType>(type), o, deep);
    } else if (clang::isa<clang::BlockPointerType>(type)) {
        processed &= parseBlockPointerType(clang::dyn_cast<clang::BlockPointerType>(type), o, deep);
    } else if (clang::isa<clang::BuiltinType>(type)) {
        processed &= parseBuiltinType(clang::dyn_cast<clang::BuiltinType>(type), o, deep);
    } else if (clang::isa<clang::ComplexType>(type)) {
        processed &= parseComplexType(clang::dyn_cast<clang::ComplexType>(type), o, deep);
    } else if (clang::isa<clang::DecltypeType>(type)) {
        processed &= parseDecltypeType(clang::dyn_cast<clang::DecltypeType>(type), o, deep);
    } else if (clang::isa<clang::DependentSizedExtVectorType>(type)) {
        processed &= parseDependentSizedExtVectorType(clang::dyn_cast<clang::DependentSizedExtVectorType>(type), o, deep);
    } else if (clang::isa<clang::FunctionType>(type)) {
        processed &= parseFunctionType(clang::dyn_cast<clang::FunctionType>(type), o, deep);
    } else if (clang::isa<clang::InjectedClassNameType>(type)) {
        processed &= parseInjectedClassNameType(clang::dyn_cast<clang::InjectedClassNameType>(type), o, deep);
    } else if (clang::isa<clang::LocInfoType>(type)) {
        processed &= parseLocInfoType(clang::dyn_cast<clang::LocInfoType>(type), o, deep);
    } else if (clang::isa<clang::MemberPointerType>(type)) {
        processed &= parseMemberPointerType(clang::dyn_cast<clang::MemberPointerType>(type), o, deep);
    } else if (clang::isa<clang::ObjCObjectPointerType>(type)) {
        processed &= parseObjCObjectPointerType(clang::dyn_cast<clang::ObjCObjectPointerType>(type), o, deep);
    } else if (clang::isa<clang::ObjCObjectType>(type)) {
        processed &= parseObjCObjectType(clang::dyn_cast<clang::ObjCObjectType>(type), o, deep);
    } else if (clang::isa<clang::PackExpansionType>(type)) {
        processed &= parsePackExpansionType(clang::dyn_cast<clang::PackExpansionType>(type), o, deep);
    } else if (clang::isa<clang::ParenType>(type)) {
        processed &= parseParenType(clang::dyn_cast<clang::ParenType>(type), o, deep);
    } else if (clang::isa<clang::PipeType>(type)) {
        processed &= parsePipeType(clang::dyn_cast<clang::PipeType>(type), o, deep);
    } else if (clang::isa<clang::PointerType>(type)) {
        processed &= parsePointerType(clang::dyn_cast<clang::PointerType>(type), o, deep);
    } else if (clang::isa<clang::ReferenceType>(type)) {
        processed &= parseReferenceType(clang::dyn_cast<clang::ReferenceType>(type), o, deep);
    } else if (clang::isa<clang::SubstTemplateTypeParmPackType>(type)) {
        processed &= parseSubstTemplateTypeParmPackType(clang::dyn_cast<clang::SubstTemplateTypeParmPackType>(type), o, deep);
    } else if (clang::isa<clang::SubstTemplateTypeParmType>(type)) {
        processed &= parseSubstTemplateTypeParmType(clang::dyn_cast<clang::SubstTemplateTypeParmType>(type), o, deep);
    } else if (clang::isa<clang::TagType>(type)) {
        processed &= parseTagType(clang::dyn_cast<clang::TagType>(type), o, deep);
    } else if (clang::isa<clang::TemplateTypeParmType>(type)) {
        processed &= parseTemplateTypeParmType(clang::dyn_cast<clang::TemplateTypeParmType>(type), o, deep);
    } else if (clang::isa<clang::TypedefType>(type)) {
        processed &= parseTypedefType(clang::dyn_cast<clang::TypedefType>(type), o, deep);
    } else if (clang::isa<clang::TypeOfExprType>(type)) {
        processed &= parseTypeOfExprType(clang::dyn_cast<clang::TypeOfExprType>(type), o, deep);
    } else if (clang::isa<clang::TypeOfType>(type)) {
        processed &= parseTypeOfType(clang::dyn_cast<clang::TypeOfType>(type), o, deep);
        // } else if (clang::isa<clang::TypeWithKeyword>(type)) {
        //     processed &= parseTypeWithKeyword(
        //         clang::dyn_cast<clang::TypeWithKeyword>(type), o, deep);
    } else if (clang::isa<clang::UnaryTransformType>(type)) {
        processed &= parseUnaryTransformType(clang::dyn_cast<clang::UnaryTransformType>(type), o, deep);
    } else if (clang::isa<clang::UnresolvedUsingType>(type)) {
        processed &= parseUnresolvedUsingType(clang::dyn_cast<clang::UnresolvedUsingType>(type), o, deep);
    } else if (clang::isa<clang::VectorType>(type)) {
        processed &= parseVectorType(clang::dyn_cast<clang::VectorType>(type), o, deep);
    } else if (clang::isa<clang::TemplateSpecializationType>(type)) {
        processed &= parseTemplateSpecializationType(clang::dyn_cast<clang::TemplateSpecializationType>(type), o, deep);
    } else if (clang::isa<clang::DependentNameType>(type)) {
        processed &= parseDependentNameType(clang::dyn_cast<clang::DependentNameType>(type), o, deep);
    } else if (clang::isa<clang::ElaboratedType>(type)) {
        processed &= parseElaboratedType(clang::dyn_cast<clang::ElaboratedType>(type), o, deep);
    } else {
        processed = false;
    }

    if (!processed) {
        std::cerr << __PRETTY_FUNCTION__ << ":" << __LINE__ << " not processed" << std::endl;
        type->dump();
        std::cerr << "============================================================" << std::endl;
    }
    return processed;
}

bool Extractor::parseAdjustedType(const clang::AdjustedType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "AdjustedType");
    if (clang::isa<clang::DecayedType>(type)) {
        processed &= parseDecayedType(clang::dyn_cast<clang::DecayedType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseArrayType(const clang::ArrayType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "ArrayType");
    o->set("elementType", parseQualType(type->getElementType(), deep));
    // Qualifiers getIndexTypeQualifiers () const
    switch (type->getSizeModifier()) {
        case clang::ArrayType::ArraySizeModifier::Normal:
            o->set("sizeModifier", "Normal");
            break;
        case clang::ArrayType::ArraySizeModifier::Static:
            o->set("sizeModifier", "Static");
            break;
        case clang::ArrayType::ArraySizeModifier::Star:
            o->set("sizeModifier", "Star");
            break;
    }
    if (clang::isa<clang::ConstantArrayType>(type)) {
        processed &= parseConstantArrayType(clang::dyn_cast<clang::ConstantArrayType>(type), o, deep);
    } else if (clang::isa<clang::DependentSizedArrayType>(type)) {
        processed &= parseDependentSizedArrayType(clang::dyn_cast<clang::DependentSizedArrayType>(type), o, deep);
    } else if (clang::isa<clang::IncompleteArrayType>(type)) {
        processed &= parseIncompleteArrayType(clang::dyn_cast<clang::IncompleteArrayType>(type), o, deep);
    } else if (clang::isa<clang::VariableArrayType>(type)) {
        processed &= parseVariableArrayType(clang::dyn_cast<clang::VariableArrayType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseAtomicType(const clang::AtomicType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseAttributedType(const clang::AttributedType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseAutoType(const clang::AutoType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "AutoType");
    o->set("isSugared", type->isSugared());
    o->set("isDeduced", type->isDeduced());
    if (type->isDeduced()) {
        // Segmentation Fault...
        // o->set("deducedType", parseQualType(type->getDeducedType(), deep));
    }
    return true;
}

bool Extractor::parseBlockPointerType(const clang::BlockPointerType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseBuiltinType(const clang::BuiltinType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "BuiltinType");
    switch (type->getKind()) {
        default: { return false; }
        case clang::BuiltinType::Kind::Void: {
            o->set("spelling", "void");
            break;
        }
        case clang::BuiltinType::Kind::Bool: {
            o->set("spelling", "bool");
            break;
        }
        case clang::BuiltinType::Kind::Char_U:
        case clang::BuiltinType::Kind::UChar: {
            o->set("spelling", "unsigned char");
            break;
        }
        case clang::BuiltinType::Kind::WChar_U: {
            o->set("spelling", "unsigned wchar");
            break;
        }
        case clang::BuiltinType::Kind::Char16: {
            o->set("spelling", "char16");
            break;
        }
        case clang::BuiltinType::Kind::Char32: {
            o->set("spelling", "char32");
            break;
        }
        case clang::BuiltinType::Kind::UShort: {
            o->set("spelling", "unsigned short");
            break;
        }
        case clang::BuiltinType::Kind::UInt: {
            o->set("spelling", "unsigned int");
            break;
        }
        case clang::BuiltinType::Kind::ULong: {
            o->set("spelling", "unsigned long");
            break;
        }
        case clang::BuiltinType::Kind::ULongLong: {
            o->set("spelling", "unsigned long long");
            break;
        }
        // case clang::BuiltinType::Kind::UInt128: {
        //     break;
        // }
        case clang::BuiltinType::Kind::Char_S:
        case clang::BuiltinType::Kind::SChar: {
            o->set("spelling", "char");
            break;
        }
        case clang::BuiltinType::Kind::WChar_S: {
            o->set("spelling", "wchar");
            break;
        }

        case clang::BuiltinType::Kind::Short: {
            o->set("spelling", "short");
            break;
        }
        case clang::BuiltinType::Kind::Int: {
            o->set("spelling", "int");
            break;
        }
        case clang::BuiltinType::Kind::Long: {
            o->set("spelling", "long");
            break;
        }
        case clang::BuiltinType::Kind::LongLong: {
            o->set("spelling", "long long");
            break;
        }
        // case clang::BuiltinType::Kind::Int128: {
        //     break;
        // }
        case clang::BuiltinType::Kind::Half: {
            o->set("spelling", "half");
            break;
        }
        case clang::BuiltinType::Kind::Float: {
            o->set("spelling", "float");
            break;
        }
        case clang::BuiltinType::Kind::Double: {
            o->set("spelling", "double");
            break;
        }
        case clang::BuiltinType::Kind::LongDouble: {
            o->set("spelling", "long double");
            break;
        }
        case clang::BuiltinType::Kind::Dependent: {
            o->set("spelling", "dependent");
            break;
        }
        case clang::BuiltinType::Kind::NullPtr: {
            o->set("spelling", "nullptr");
            break;
        }
    }

    return true;
}

bool Extractor::parseComplexType(const clang::ComplexType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseDecltypeType(const clang::DecltypeType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "DecltypeType");
    o->set("underlyingExpr", parseExpr(type->getUnderlyingExpr(), deep));
    o->set("underlyingType", parseQualType(type->getUnderlyingType(), deep));
    // if (clang::isa<clang::DependentDeclType>(type)) {
    //     return parseDependentDeclType(
    //         clang::dyn_cast<clang::DependentDeclType>(type), o, deep);
    // }
    return true;
}

bool Extractor::parseDependentSizedExtVectorType(const clang::DependentSizedExtVectorType *type,
                                                 const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseFunctionType(const clang::FunctionType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "FunctionType");
    o->set("returnType", parseQualType(type->getReturnType(), false));
    o->set("hasRegParm", type->getHasRegParm());
    o->set("noReturnAttr", type->getNoReturnAttr());
    o->set("isConst", type->isConst());
    o->set("isVolatile", type->isVolatile());
    o->set("isRestrict", type->isRestrict());
    if (clang::isa<clang::FunctionNoProtoType>(type)) {
        processed &= parseFunctionNoProtoType(clang::dyn_cast<clang::FunctionNoProtoType>(type), o, deep);
    } else if (clang::isa<clang::FunctionProtoType>(type)) {
        processed &= parseFunctionProtoType(clang::dyn_cast<clang::FunctionProtoType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseInjectedClassNameType(const clang::InjectedClassNameType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "InjectedClassNameType");
    o->set("decl", parseDecl(type->getDecl(), false));
    o->set("injectedSpecializationType", parseQualType(type->getInjectedSpecializationType(), deep));
    return true;
}

bool Extractor::parseLocInfoType(const clang::LocInfoType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseMemberPointerType(const clang::MemberPointerType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set("isMemberFunctionPointer", type->isMemberFunctionPointer());
    o->set("isMemberDataPointer", type->isMemberDataPointer());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    return true;
}

bool Extractor::parseObjCObjectPointerType(const clang::ObjCObjectPointerType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseObjCObjectType(const clang::ObjCObjectType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = false;
    if (clang::isa<clang::ObjCInterfaceType>(type)) {
        processed &= parseObjCInterfaceType(clang::dyn_cast<clang::ObjCInterfaceType>(type), o, deep);
    } else if (clang::isa<clang::ObjCObjectTypeImpl>(type)) {
        processed &= parseObjCObjectTypeImpl(clang::dyn_cast<clang::ObjCObjectTypeImpl>(type), o, deep);
    }
    return processed;
}

bool Extractor::parsePackExpansionType(const clang::PackExpansionType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "PackExpansionType");
    o->set("pattern", parseQualType(type->getPattern(), deep));
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    // Optional< unsigned > getNumExpansions () const
    return true;
}

bool Extractor::parseParenType(const clang::ParenType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "ParenType");
    o->set("innterType", parseQualType(type->getInnerType(), deep));
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    return true;
}

bool Extractor::parsePipeType(const clang::PipeType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parsePointerType(const clang::PointerType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "PointerType");
    o->set("pointeeType", parseQualType(type->getPointeeType(), deep));
    o->set("isSugared", type->isSugared());
    return true;
}

bool Extractor::parseReferenceType(const clang::ReferenceType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "ReferenceType");
    o->set("isSpelledAsLValue", type->isSpelledAsLValue());
    o->set("isInnerRef", type->isInnerRef());
    o->set("pointeeType", parseQualType(type->getPointeeType(), deep));
    if (clang::isa<clang::LValueReferenceType>(type)) {
        processed &= parseLValueReferenceType(clang::dyn_cast<clang::LValueReferenceType>(type), o, deep);
    } else if (clang::isa<clang::RValueReferenceType>(type)) {
        processed &= parseRValueReferenceType(clang::dyn_cast<clang::RValueReferenceType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseSubstTemplateTypeParmPackType(const clang::SubstTemplateTypeParmPackType *type,
                                                   const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseSubstTemplateTypeParmType(const clang::SubstTemplateTypeParmType *type,
                                               const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "SubstTemplateTypeParmType");
    // TemplateTypeParmType * getReplacedParameter () const
    o->set("replacementType", parseQualType(type->getReplacementType(), deep));
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    return true;
}

bool Extractor::parseTagType(const clang::TagType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "TagType");
    o->set("decl", parseDecl(type->getDecl(), deep));
    o->set("isBeingDefined", type->isBeingDefined());
    if (clang::isa<clang::EnumType>(type)) {
        processed &= parseEnumType(clang::dyn_cast<clang::EnumType>(type), o, deep);
    } else if (clang::isa<clang::RecordType>(type)) {
        processed &= parseRecordType(clang::dyn_cast<clang::RecordType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseTemplateTypeParmType(const clang::TemplateTypeParmType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "TemplateTypeParmType");
    o->set("depth", Json::mkInt(type->getDepth()));
    o->set("index", Json::mkInt(type->getIndex()));
    o->set("isParameterPack", type->isParameterPack());
    o->set("isSugared", type->isSugared());
    o->set("decl", parseDecl(type->getDecl(), deep));
    o->set("identifier", parseIdentifier(type->getIdentifier(), deep));
    return true;
}

bool Extractor::parseTypedefType(const clang::TypedefType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "TypedefType");
    o->set("decl", parseDecl(type->getDecl(), deep));
    o->set("isSugared", type->isSugared());
    return true;
}

bool Extractor::parseTypeOfExprType(const clang::TypeOfExprType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = true;
    o->set(CLASS_STRING, "TypeOfExprType");
    o->set("underlyingExpr", parseExpr(type->getUnderlyingExpr(), deep));
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    if (clang::isa<clang::DependentTypeOfExprType>(type)) {
        processed &= parseDependentTypeOfExprType(clang::dyn_cast<clang::DependentTypeOfExprType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseTypeOfType(const clang::TypeOfType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

// bool Extractor::parseTypeWithKeyword(const clang::TypeWithKeyword *type,
//                                      const std::shared_ptr<Json> &o, bool deep) {
//     if (clang::isa<clang::DependentNameType>(type)) {
//         return parseDependentNameType(
//             clang::dyn_cast<clang::DependentNameType>(type), o, deep);
//     } else if (clang::isa<clang::ElaboratedType>(type)) {
//         return
//         parseElaboratedType(clang::dyn_cast<clang::ElaboratedType>(type),
//                                    o, deep);
//     }
//     return false;
// }

bool Extractor::parseUnaryTransformType(const clang::UnaryTransformType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = false;
    if (clang::isa<clang::DependentUnaryTransformType>(type)) {
        processed &= parseDependentUnaryTransformType(clang::dyn_cast<clang::DependentUnaryTransformType>(type), o, deep);
    }
    return processed;
}

bool Extractor::parseUnresolvedUsingType(const clang::UnresolvedUsingType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseVectorType(const clang::VectorType *type, const std::shared_ptr<Json> &o, bool deep) {
    bool processed = false;
    if (clang::isa<clang::ExtVectorType>(type)) {
        processed &= parseExtVectorType(clang::dyn_cast<clang::ExtVectorType>(type), o, deep);
    }

    return processed;
}

bool Extractor::parseTemplateSpecializationType(const clang::TemplateSpecializationType *type,
                                                const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "TemplateSpecializationType");

    o->set("isCurrentInstantiation", type->isCurrentInstantiation());
    o->set("isTypeAlias", type->isTypeAlias());
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    o->set("numArgs", Json::mkInt(type->getNumArgs()));
    if (type->isTypeAlias()) {
        o->set("aliasedType", parseQualType(type->getAliasedType(), deep));
    }
    // o->set("getTemplateName", parseTemplateName(type->getTemplateName()));
    auto args = Json::mkArray();
    for (auto iter = type->begin(), end = type->end(); iter != end; iter++) {
        args->add(parseTemplateArgument(iter, deep));
    }
    o->set("args", args);
    return true;
}

bool Extractor::parseDecayedType(const clang::DecayedType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "DecayedType");
    return true;
}

bool Extractor::parseConstantArrayType(const clang::ConstantArrayType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "ConstantArrayType");
    o->set("size", Json::mkInt(type->getSize().getLimitedValue()));
    o->set("isSugared", type->isSugared());
    return true;
}

bool Extractor::parseDependentSizedArrayType(const clang::DependentSizedArrayType *type,
                                             const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseIncompleteArrayType(const clang::IncompleteArrayType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseVariableArrayType(const clang::VariableArrayType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

// bool Extractor::parseDependentDeclType(const clang::DependentDeclType *type,
//                                        const std::shared_ptr<Json> &o, bool deep) {
//     return false;
// }

bool Extractor::parseFunctionNoProtoType(const clang::FunctionNoProtoType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseFunctionProtoType(const clang::FunctionProtoType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "FunctionProtoType");
    o->set("hasExceptionSpec", type->hasExceptionSpec());
    o->set("hasDynamicExceptionSpec", type->hasDynamicExceptionSpec());
    o->set("hasNoexceptExceptionSpec", type->hasNoexceptExceptionSpec());
    o->set("hasDependentExceptionSpec", type->hasDependentExceptionSpec());
    o->set("isVariadic", type->isVariadic());
    o->set("isTemplateVariadic", type->isTemplateVariadic());
    o->set("hasTrailingReturn", type->hasTrailingReturn());

    auto param_types = Json::mkArray();
    auto exceptions = Json::mkArray();
    auto extParameterInfos = Json::mkArray();
    for (auto &&iter : type->param_types()) {
        param_types->add(parseQualType(iter, deep));
    }
    for (auto &&iter : type->exceptions()) {
        exceptions->add(parseQualType(iter, deep));
    }
    // for (auto &&iter : type->getExtParameterInfos()) {
    //     extParameterInfos->add(parseExtParameterInfo(iter));
    // }
    o->set("param_types", param_types);
    o->set("exceptions", exceptions);
    o->set("extParameterInfos", extParameterInfos);
    return true;
}

bool Extractor::parseObjCInterfaceType(const clang::ObjCInterfaceType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseObjCObjectTypeImpl(const clang::ObjCObjectTypeImpl *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseLValueReferenceType(const clang::LValueReferenceType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "LValueReferenceType");
    o->set("isSugared", type->isSugared());
    // type->desugar();
    return true;
}

bool Extractor::parseRValueReferenceType(const clang::RValueReferenceType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "RValueReferenceType");
    o->set("isSugared", type->isSugared());
    return true;
}

bool Extractor::parseEnumType(const clang::EnumType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "EnumType");
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("sugar", parseQualType(type->desugar(), deep));
    }
    return true;
}

bool Extractor::parseRecordType(const clang::RecordType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "RecordType");
    o->set("hasConstFields", type->hasConstFields());
    o->set("isSugared", type->isSugared());
    return true;
}

bool Extractor::parseDependentTypeOfExprType(const clang::DependentTypeOfExprType *type,
                                             const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "DependentTypeOfExprType");
    return true;
}

bool Extractor::parseDependentNameType(const clang::DependentNameType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "DependentNameType");
    // NestedNameSpecifier * getQualifier () const
    // const IdentifierInfo * getIdentifier () const 
    o->set("isSugared", type->isSugared());
    if (type->isSugared()) {
        o->set("namedType", parseQualType(type->desugar(), deep));
    }
    return true;
}

bool Extractor::parseElaboratedType(const clang::ElaboratedType *type, const std::shared_ptr<Json> &o, bool deep) {
    o->set(CLASS_STRING, "ElaboratedType");
    o->set("namedType", parseQualType(type->getNamedType(), deep));
    o->set("isSugared", type->isSugared());
    return true;
}

bool Extractor::parseDependentUnaryTransformType(const clang::DependentUnaryTransformType *type,
                                                 const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

bool Extractor::parseExtVectorType(const clang::ExtVectorType *type, const std::shared_ptr<Json> &o, bool deep) {
    return false;
}

