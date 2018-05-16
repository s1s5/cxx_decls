/**
 * Copyright 2015- Co. Ltd. sizebook
 * @file cb_pack.hpp
 * @brief
 * @author sawai@sizebook.co.jp (Shogo Sawai)
 * @date 2016-04-13 19:48:22
 */
#ifndef CB_PACK_HPP_
#define CB_PACK_HPP_

#include <iostream>

#include <clang/AST/ASTConsumer.h>
#include <clang/Basic/TargetInfo.h>
#include <clang/Driver/Compilation.h>
#include <clang/Driver/Driver.h>
#include <clang/Driver/Tool.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendDiagnostic.h>
#include <clang/Lex/Preprocessor.h>
#include <clang/Tooling/Tooling.h>

class CbPack {
 private:
    class CH : public clang::CommentHandler {
     public:
        explicit CH(CbPack *cp_) : cp(cp_) {}
        virtual bool HandleComment(clang::Preprocessor &PP, clang::SourceRange Loc) {
            return cp->HandleComment(PP, Loc);
        }

     private:
        CbPack *cp;
    };
    class PC : public clang::PPCallbacks {
     public:
        PC(CbPack *cp_, clang::Preprocessor *pp_) : cp(cp_), pp(pp_) {}
        virtual void MacroDefined(const clang::Token &MacroNameTok, const clang::MacroDirective *MD) override {
            cp->MacroDefined(*pp, MacroNameTok, MD);
        }

     private:
        CbPack *cp;
        clang::Preprocessor *pp;
    };
    class DC : public clang::DiagnosticConsumer {
     public:
        explicit DC(CbPack *cp_) : cp(cp_) {}
        virtual void HandleDiagnostic(clang::DiagnosticsEngine::Level DiagLevel,
                                      const clang::Diagnostic &Info) override {
            cp->HandleDiagnostic(DiagLevel, Info);
        }

     private:
        CbPack *cp;
    };
    class AC : public clang::ASTConsumer {
     public:
        explicit AC(CbPack *cp_) : cp(cp_) {}
        virtual void HandleTranslationUnit(clang::ASTContext &context) override {
            if (cp) {
                cp->HandleTranslationUnit(context);
            }
        }

     private:
        CbPack *cp;
    };

 public:
    virtual ~CbPack() {}
    clang::CommentHandler *newCH() { return new CH(this); }
    clang::PPCallbacks *newPC(clang::Preprocessor *pp) { return new PC(this, pp); }
    clang::DiagnosticConsumer *newDC() { return new DC(this); }
    clang::ASTConsumer *newAC() { return new AC(this); }

    virtual void setTargetFilename(const std::string &filename) = 0;
    virtual void setTargetInfo(clang::TargetInfo *targetInfo) = 0;
    virtual bool HandleComment(clang::Preprocessor &PP, clang::SourceRange Loc) = 0;
    virtual void MacroDefined(clang::Preprocessor &PP, const clang::Token &MacroNameTok,
                              const clang::MacroDirective *MD) = 0;
    virtual void HandleDiagnostic(clang::DiagnosticsEngine::Level DiagLevel, const clang::Diagnostic &Info) = 0;
    virtual void HandleTranslationUnit(clang::ASTContext &context) = 0;
};

#endif  // CB_PACK_HPP_
