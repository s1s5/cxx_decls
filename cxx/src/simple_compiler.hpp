/**
 * Copyright 2015- Co. Ltd. sizebook
 * @file simple_compiler.hpp
 * @brief
 * @author sawai@sizebook.co.jp (Shogo Sawai)
 * @date 2016-04-13 15:26:36
 */
#ifndef SIMPLE_COMPILER_HPP_
#define SIMPLE_COMPILER_HPP_

#if 0

#include <memory>
#include <string>
#include <vector>

#include <clang/AST/ASTConsumer.h>
#include <clang/Frontend/FrontendDiagnostic.h>
#include <clang/Lex/Preprocessor.h>
#include <clang/Tooling/Tooling.h>
#include "cb_pack.hpp"

#include "json.hpp"

class SimpleCompiler : public clang::tooling::SourceFileCallbacks {
 public:
    SimpleCompiler();
    void run(const std::string &filename, const std::vector<std::string> &opts = std::vector<std::string>());
    
    void setCbPack(CbPack *cb_pack_) {
        cb_pack = cb_pack_;
    }
    std::unique_ptr<clang::ASTConsumer> newASTConsumer() {
        return std::unique_ptr<clang::ASTConsumer>(cb_pack->newAC());
    }
    
    virtual bool handleBeginSource(clang::CompilerInstance &CI, llvm::StringRef Filename) override;
    virtual void handleEndSource() override;

    CbPack *cb_pack;
    std::string triple;
    std::shared_ptr<clang::CommentHandler> cur_comment_handler;
    std::shared_ptr<clang::DiagnosticConsumer> cur_diagnostic_consumer;
};

#endif

#endif  // SIMPLE_COMPILER_HPP_
