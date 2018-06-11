/**
 * Copyright (c)
 * @file util.cpp
 * @brief
 * @author
 * @date
 */
#include "util.hpp"

#include <iostream>
#include <sstream>

// #include <clang/Index/USRGeneration.h>
#include <llvm/ADT/SmallString.h>

#include "usr_generator.hpp"

#ifndef PREFIX
#define PREFIX (std::string("__usr_prefix_"))
#endif // PREFIX

std::string util::getUSRPrefix() {
    return PREFIX;
}

std::vector<std::string> util::getDeclContext(const clang::Decl *decl) {
    std::vector<std::string> ns;
    const clang::DeclContext *dc = decl->getDeclContext();
    while (dc && (!dc->isTranslationUnit())) {
        const auto *nd = llvm::dyn_cast<const clang::NamedDecl>(dc);
        if (!nd) {
            const auto *ecd =
                llvm::dyn_cast<const clang::ExternCContextDecl>(dc);
            const auto *fcd = llvm::dyn_cast<const clang::FunctionDecl>(dc);
            const auto *ncd = llvm::dyn_cast<const clang::NamespaceDecl>(dc);
            const auto *tcd = llvm::dyn_cast<const clang::TagDecl>(dc);
            const auto *tu =
                llvm::dyn_cast<const clang::TranslationUnitDecl>(dc);
            const auto *l = llvm::dyn_cast<const clang::BlockDecl>(dc);
            // const auto *tld = llvm::dyn_cast<const clang::ValueDecl>(dc);
            // std::cerr << __FILE__ << ":" << __LINE__ << " => "<< tld << std::endl;
            if (ecd) {
            } else if (fcd) {
            } else if (ncd) {
            } else if (tcd) {
            } else if (tu) {
            } else if (l) {
            } else if (dc->isExternCContext()) {
            } else {
                // std::cerr << "unknown type " << dc << std::endl;
                // std::cerr << "isClosure            = " << dc->isClosure()
                //           << std::endl;
                // std::cerr << "isObjCContainer      = " << dc->isObjCContainer()
                //           << std::endl;
                // std::cerr << "isFunctionOrMethod   = "
                //           << dc->isFunctionOrMethod() << std::endl;
                // std::cerr << "isLookupContext      = " << dc->isLookupContext()
                //           << std::endl;
                // std::cerr << "isFileContext        = " << dc->isFileContext()
                //           << std::endl;
                // std::cerr << "isTranslationUnit    = "
                //           << dc->isTranslationUnit() << std::endl;
                // std::cerr << "isRecord             = " << dc->isRecord()
                //           << std::endl;
                // std::cerr << "isNamespace          = " << dc->isNamespace()
                //           << std::endl;
                // std::cerr << "isStdNamespace       = " << dc->isStdNamespace()
                //           << std::endl;
                // std::cerr << "isInlineNamespace    = "
                //           << dc->isInlineNamespace() << std::endl;
                // std::cerr << "isDependentContext   = "
                //           << dc->isDependentContext() << std::endl;
                // std::cerr << "isTransparentContext = "
                //           << dc->isTransparentContext() << std::endl;
                // std::cerr << "isExternCContext     = " << dc->isExternCContext()
                //           << std::endl;
                // std::cerr << "isExternCXXContext   = "
                //           << dc->isExternCXXContext() << std::endl;
                // dc->dumpDeclContext();
            }
            return std::vector<std::string>();
        }
        ns.push_back(nd->getNameAsString());
        dc = dc->getParent();
    }
    return std::vector<std::string>(ns.rbegin(), ns.rend());
}

std::string util::getAbsPath(const clang::NamedDecl *decl) {
    std::stringstream ss;
    auto ns = util::getDeclContext(decl);
    for (auto &&s : ns) {
        if (s != "") {
            ss << s << "::";
        } else {
            ss << "bb_usr_anonymous_namespace" << "::";
        }
    }
    ss << decl->getNameAsString();
    return ss.str();
}

std::shared_ptr<Json> util::getTargetInfo(clang::TargetInfo *targetInfo) {
    auto o = Json::mkObject();

    const clang::TargetInfo::IntType types[] = {
        targetInfo->getSizeType(),      targetInfo->getIntMaxType(),
        targetInfo->getUIntMaxType(),   targetInfo->getIntPtrType(),
        targetInfo->getUIntPtrType(),   targetInfo->getWCharType(),
        targetInfo->getWIntType(),      targetInfo->getChar16Type(),
        targetInfo->getChar32Type(),    targetInfo->getInt64Type(),
        targetInfo->getUInt64Type(),    targetInfo->getSigAtomicType(),
        targetInfo->getProcessIDType(),
    };
    const std::string type_strings[] = {
        "SizeType",      "IntMaxType", "UIntMaxType", "IntPtrType",
        "UIntPtrType",   "WCharType",  "WIntType",    "Char16Type",
        "Char32Type",    "Int64Type",  "UInt64Type",  "SigAtomicType",
        "ProcessIDType",
    };
    const clang::TargetInfo::IntType all_types[] = {
        // clang::TargetInfo::IntType::NoInt,
        clang::TargetInfo::IntType::SignedChar,
        clang::TargetInfo::IntType::UnsignedChar,
        clang::TargetInfo::IntType::SignedShort,
        clang::TargetInfo::IntType::UnsignedShort,
        clang::TargetInfo::IntType::SignedInt,
        clang::TargetInfo::IntType::UnsignedInt,
        clang::TargetInfo::IntType::SignedLong,
        clang::TargetInfo::IntType::UnsignedLong,
        clang::TargetInfo::IntType::SignedLongLong,
        clang::TargetInfo::IntType::UnsignedLongLong,
    };
    const std::string all_type_strings[] = {
        // "NoInt",
        "SignedChar",     "UnsignedChar",     "SignedShort",
        "UnsignedShort", "SignedInt",      "UnsignedInt",      "SignedLong",
        "UnsignedLong",  "SignedLongLong", "UnsignedLongLong",
    };
    for (unsigned int i = 0; i < sizeof(types) / sizeof(types[0]); i++) {
        o->objectUpdate(type_strings[i],
                        Json::mkInt(targetInfo->getTypeWidth(types[i])));
    }

    for (unsigned int i = 0; i < sizeof(all_types) / sizeof(all_types[0]);
         i++) {
        o->objectUpdate(all_type_strings[i],
                        Json::mkInt(targetInfo->getTypeWidth(all_types[i])));
    }

    auto &opts = targetInfo->getTargetOpts();
    o->objectUpdate("Triple", Json::mkString(opts.Triple));
    o->objectUpdate("CPU", Json::mkString(opts.CPU));
    o->objectUpdate("FPMath", Json::mkString(opts.FPMath));
    o->objectUpdate("ABI", Json::mkString(opts.ABI));
    o->objectUpdate("LinkerVersion", Json::mkString(opts.LinkerVersion));

    // std::vector< std::string > FeaturesAsWritten
    // std::vector< std::string > Features
    // std::vector< std::string > Reciprocals

    o->objectUpdate("half_width", Json::mkInt(targetInfo->getHalfWidth()));
    o->objectUpdate("float_width", Json::mkInt(targetInfo->getFloatWidth()));
    o->objectUpdate("double_width", Json::mkInt(targetInfo->getDoubleWidth()));
    o->objectUpdate("long_double_width",
                    Json::mkInt(targetInfo->getLongDoubleWidth()));

    return o;
}

void util::setDeclUSR(std::shared_ptr<Json> o, const clang::Decl *decl) {
    // llvm::SmallString<256> buf(clang::index::getUSRSpacePrefix());
    llvm::SmallString<256> buf;
    generateUSRForDecl(decl, buf);
    o->objectUpdate(
        PREFIX + "usr", Json::mkString(PREFIX + buf.str().str()));  // unified_symbol_resolutions
}

std::string util::getDeclUSR(const clang::Decl *decl) {
    llvm::SmallString<256> buf;
    generateUSRForDecl(decl, buf);
    return PREFIX + buf.str().str();
}

bool util::startswith(const char *p0, const char *p1) {
    while ((*p0) && (*p1) && (*p0 == *p1)) {
        p0++;
        p1++;
    }
    return *p1 == '\0';
}
