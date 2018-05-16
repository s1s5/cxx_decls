/**
 * Copyright 2015- Co. Ltd. sizebook
 * @file simple_compiler.cpp
 * @brief
 * @author sawai@sizebook.co.jp (Shogo Sawai)
 * @date 2016-04-13 15:27:33
 */
#include "simple_compiler.hpp"

#if 0

#include <iostream>

#include <clang/Basic/TargetInfo.h>
#include <clang/Driver/Compilation.h>
#include <clang/Driver/Driver.h>
#include <clang/Driver/Tool.h>
#include <clang/Frontend/CompilerInstance.h>

SimpleCompiler::SimpleCompiler() {
    triple = llvm::sys::getDefaultTargetTriple();
}


bool SimpleCompiler::handleBeginSource(clang::CompilerInstance &CI, llvm::StringRef Filename) {
    if (cb_pack) {
        CI.getPreprocessor().addCommentHandler(cb_pack->newCH());
        CI.getPreprocessor().addPPCallbacks(std::unique_ptr<clang::PPCallbacks>(cb_pack->newPC(&CI.getPreprocessor())));
    }
    return true;
}

void SimpleCompiler::handleEndSource() {
}

void SimpleCompiler::run(const std::string &filename, const std::vector<std::string> &opts) {
    if (cb_pack) {
        cb_pack->setTargetFilename(filename);
        cur_diagnostic_consumer = std::shared_ptr<clang::DiagnosticConsumer>(cb_pack->newDC());
    } else {
        cur_diagnostic_consumer = std::shared_ptr<clang::DiagnosticConsumer>();
    }

    std::vector<std::string> command_line;
    command_line.push_back("simple_compiler");
    command_line.insert(command_line.end(), opts.begin(), opts.end());
    command_line.push_back(filename);

    clang::FileManager *files = new clang::FileManager(clang::FileSystemOptions());

    std::vector<const char *> argv;
    for (auto &&str : command_line) {
        argv.push_back(str.c_str());
    }
    clang::IntrusiveRefCntPtr<clang::DiagnosticOptions> diag_opts = new clang::DiagnosticOptions();
    clang::DiagnosticsEngine diagnostic(clang::IntrusiveRefCntPtr<clang::DiagnosticIDs>(new clang::DiagnosticIDs()),
                                        &*diag_opts, cur_diagnostic_consumer.get(), false);
    const std::unique_ptr<clang::driver::Driver> driver(new clang::driver::Driver(argv[0], triple, diagnostic));
    driver->setCheckInputsExist(false);
    const std::unique_ptr<clang::driver::Compilation> compilation(driver->BuildCompilation(llvm::makeArrayRef(argv)));

    std::shared_ptr<clang::TargetOptions> targetOpts(new clang::TargetOptions());
    targetOpts->Triple = triple;
    clang::TargetInfo *targetInfo = clang::TargetInfo::CreateTargetInfo(diagnostic, targetOpts);
    // printf("Triple %p, %p : %s\n", targetInfo, cb_pack, triple.c_str());
    
    if (cb_pack) {
        cb_pack->setTargetInfo(targetInfo);
    }

    const clang::driver::JobList &Jobs = compilation->getJobs();
    const clang::driver::Command &Cmd = clang::cast<clang::driver::Command>(*Jobs.begin());
    const llvm::opt::ArgStringList *const cc1Args = &Cmd.getArguments();
    clang::CompilerInvocation *invocation = new clang::CompilerInvocation;
    clang::CompilerInvocation::CreateFromArgs(*invocation, cc1Args->data() + 1, cc1Args->data() + cc1Args->size(),
                                              diagnostic);
    invocation->getFrontendOpts().DisableFree = false;
    invocation->getCodeGenOpts().DisableFree = false;
    invocation->getDependencyOutputOpts() = clang::DependencyOutputOptions();
    std::shared_ptr<clang::PCHContainerOperations> PCHContainerOps = std::make_shared<clang::PCHContainerOperations>();

    std::unique_ptr<clang::tooling::FrontendActionFactory> FrontendFactory;
    // FrontendFactory = clang::tooling::newFrontendActionFactory(this, this);
    FrontendFactory = clang::tooling::newFrontendActionFactory(this);
    clang::tooling::ToolAction *action = FrontendFactory.get();
    action->runInvocation(invocation, files, PCHContainerOps, cur_diagnostic_consumer.get());
}

#endif
