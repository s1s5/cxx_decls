/**
 * Copyright Shogo Sawai
 * @file to_json.cpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-26 09:35:56
 */
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendPluginRegistry.h"
#include "clang/Sema/Sema.h"
#include "llvm/Support/raw_ostream.h"

#include "cb_pack.hpp"
#include "extractor.hpp"
#include "util.hpp"

using namespace clang;

namespace {

class MyCbPack : public CbPack {
 public:
    MyCbPack() {
        comments = Json::mkArray();
        defines = Json::mkArray();
        diagnostics = Json::mkArray();
        target_info = Json::mkObject();
    }
    virtual void setTargetFilename(const std::string &filename_) { filename = filename_; }
    virtual void setTargetInfo(clang::TargetInfo *targetInfo) { target_info = util::getTargetInfo(targetInfo); }

    virtual bool HandleComment(clang::Preprocessor &PP, clang::SourceRange Loc) {
        clang::SourceManager &SM = PP.getSourceManager();
        if (SM.getFilename(Loc.getBegin()).str() != filename) {
            return false;
        }

        clang::SourceLocation Start = Loc.getBegin();
        std::string C(SM.getCharacterData(Start), SM.getCharacterData(Loc.getEnd()));

        bool Invalid;
        unsigned CLine = SM.getSpellingLineNumber(Start, &Invalid);
        unsigned CCol = SM.getSpellingColumnNumber(Start, &Invalid);

        auto o = Json::mkObject();
        o->objectUpdate("line", Json::mkInt(CLine));
        o->objectUpdate("col", Json::mkInt(CCol));
        o->objectUpdate("comment", Json::mkString(C));
        comments->arrayAppend(o);
        return false;
    }

    std::string token2str(clang::Preprocessor &PP, const clang::Token &token) {
        clang::SourceManager &SM = PP.getSourceManager();
        return std::string(SM.getCharacterData(token.getLocation()), SM.getCharacterData(token.getEndLoc()));
    }

    virtual void MacroDefined(clang::Preprocessor &PP, const clang::Token &MacroNameTok,
                              const clang::MacroDirective *MD) {
        clang::SourceManager &SM = PP.getSourceManager();
        if (SM.getFilename(MacroNameTok.getLocation()).str() != filename) {
            return;
        }
        std::string C(SM.getCharacterData(MacroNameTok.getLocation()), SM.getCharacterData(MacroNameTok.getEndLoc()));
        auto md_def = MD->getDefinition().getMacroInfo();
        auto args = Json::mkArray();

        // for (auto &&t = md_def->arg_begin(), e = md_def->arg_end(); t != e; t++) {
        for (auto &&t = md_def->param_begin(), e = md_def->param_end(); t != e; t++) {
            args->arrayAppend(Json::mkString((*t)->getName().str()));
        }
        auto dt = Json::mkArray();
        for (auto &&t = md_def->tokens_begin(), e = md_def->tokens_end(); t != e; t++) {
            dt->arrayAppend(Json::mkString(token2str(PP, *t)));
        }
        auto o = Json::mkObject();
        o->objectUpdate("macro_name", Json::mkString(std::string(SM.getCharacterData(MacroNameTok.getLocation()),
                                                                 SM.getCharacterData(MacroNameTok.getEndLoc()))));
        o->objectUpdate("macro_def", dt);
        o->objectUpdate("macro_arg", args);
        defines->arrayAppend(o);
    }

    virtual void HandleDiagnostic(clang::DiagnosticsEngine::Level DiagLevel, const clang::Diagnostic &Info) {
        auto d = Json::mkObject();
        std::string level;
        int level_int = -1;
        switch (DiagLevel) {
            case clang::DiagnosticsEngine::Ignored:
                level = "ignored";
                level_int = 0;
                break;
            case clang::DiagnosticsEngine::Note:
                level = "note";
                level_int = 1;
                break;
            case clang::DiagnosticsEngine::Remark:
                level = "remark";
                level_int = 2;
                break;
            case clang::DiagnosticsEngine::Warning:
                level = "warning";
                level_int = 3;
                break;
            case clang::DiagnosticsEngine::Error:
                level = "error";
                level_int = 4;
                break;
            case clang::DiagnosticsEngine::Fatal:
                level = "fatal";
                level_int = 5;
                break;
        }
        llvm::SmallVector<char, 128> hoge;
        Info.FormatDiagnostic(hoge);
        std::string a(hoge.begin(), hoge.end());
        // printf("%s:%d %s\n", __FILE__, __LINE__, a.c_str());

        auto sl = Info.getLocation();  // <= SourceLocation
        if (Info.hasSourceManager()) {
            auto &mng = Info.getSourceManager();
            // std::cout << mng.getFilename(sl).str() << ","
            //           << mng.getSpellingLineNumber(sl) << "," <<std::endl;
            d->objectUpdate("filename", Json::mkString(mng.getFilename(sl).str()));
            d->objectUpdate("line_no", Json::mkInt(mng.getSpellingLineNumber(sl)));
        }
        d->objectUpdate("level", Json::mkString(level));
        d->objectUpdate("level_int", Json::mkInt(level_int));
        d->objectUpdate("message", Json::mkString(a));
        // d->dump(&std::cout); std::cout << std::endl;
        diagnostics->arrayAppend(d);
    }

    virtual void HandleTranslationUnit(clang::ASTContext &context) {
        p_context = &context;
        extractor.setASTContext(&context);
        extractor.setSourceFilename(filename);
        extractor.TraverseDecl(context.getTranslationUnitDecl());
    }
    clang::ASTContext *p_context;
    std::string filename;
    Extractor extractor;

    std::shared_ptr<Json> comments;
    std::shared_ptr<Json> defines;
    std::shared_ptr<Json> diagnostics;
    std::shared_ptr<Json> target_info;
};

std::string abspath(const std::string &path) {
    char *abspath = realpath(path.c_str(), nullptr);
    std::string res(abspath);
    free(abspath);
    return res;
}

class PrintDeclsConsumer : public ASTConsumer {
    CompilerInstance &Instance;
    std::set<std::string> ParsedTemplates;
    std::string source_file;
    std::vector<const Decl *> decls;
    MyCbPack *cb_pack;
    clang::DiagnosticsEngine *diagnostic;
    clang::DiagnosticConsumer *cur_diagnostic_consumer;
    clang::IntrusiveRefCntPtr<clang::DiagnosticOptions> diag_opts;

 public:
    PrintDeclsConsumer(CompilerInstance &Instance, std::set<std::string> ParsedTemplates, const std::string &s)
        : Instance(Instance), ParsedTemplates(ParsedTemplates), source_file(s) {
        cb_pack = new MyCbPack();
        cb_pack->setTargetFilename(source_file);
        cur_diagnostic_consumer = cb_pack->newDC();
        diag_opts = new clang::DiagnosticOptions();
        diagnostic =
            new clang::DiagnosticsEngine(clang::IntrusiveRefCntPtr<clang::DiagnosticIDs>(new clang::DiagnosticIDs()),
                                         &*diag_opts, cur_diagnostic_consumer, false);
        auto target_opts = Instance.getTargetOpts();
        clang::TargetInfo *targetInfo = clang::TargetInfo::CreateTargetInfo(
            *diagnostic, std::shared_ptr<TargetOptions>(new TargetOptions(target_opts)));
        cb_pack->setTargetInfo(targetInfo);

        Instance.getPreprocessor().addCommentHandler(cb_pack->newCH());
        Instance.getPreprocessor().addPPCallbacks(std::unique_ptr<clang::PPCallbacks>(cb_pack->newPC(&Instance.getPreprocessor())));
        Instance.getDiagnostics().setClient(cur_diagnostic_consumer, false);
    }

    bool HandleTopLevelDecl(DeclGroupRef DG) override {
        for (DeclGroupRef::iterator i = DG.begin(), e = DG.end(); i != e; ++i) {
            const Decl *D = *i;
            // if (const NamedDecl *ND = dyn_cast<NamedDecl>(D))
            // v.TraverseDecl(D);
            decls.push_back(D);
        }
        return true;
    }

    void HandleTranslationUnit(ASTContext &context) override {
        // Extractor v;
        // v.setASTContext(&context);
        // v.setSourceFilename(source_file);

        // v.TraverseDecl(context.getTranslationUnitDecl());

        // for (auto &&i : decls) {
        //     i->dump();
        // }
        // clang::Sema &sema = Instance.getSema();
        // for (const FunctionDecl *FD : v.LateParsedDecls) {
        //     clang::LateParsedTemplate *LPT = sema.LateParsedTemplateMap.lookup(FD);
        //     sema.LateTemplateParser(sema.OpaqueParser, *LPT);
        //     llvm::errs() << "late-parsed-decl: \"" << FD->getNameAsString() << "\"\n";
        // }

        // auto result = Json::mkObject();
        // result->objectUpdate("usr_prefix", Json::mkString(util::getUSRPrefix()));
        // result->objectUpdate("filename", Json::mkString(source_file));
        // // result->objectUpdate("target_info", cb_pack.target_info);
        // // result->objectUpdate("diagnostics", cb_pack.diagnostics);
        // // result->objectUpdate("comments", cb_pack.comments);
        // // result->objectUpdate("defines", cb_pack.defines);
        // result->objectUpdate("declarations", v.getResults());
        // result->objectUpdate("usr_map", v.getUsrMap());
        // result->dump(&std::cout);
        cb_pack->HandleTranslationUnit(context);

        auto result = Json::mkObject();
        result->objectUpdate("usr_prefix", Json::mkString(util::getUSRPrefix()));
        result->objectUpdate("filename", Json::mkString(source_file));
        result->objectUpdate("target_info", cb_pack->target_info);
        result->objectUpdate("diagnostics", cb_pack->diagnostics);
        result->objectUpdate("comments", cb_pack->comments);
        result->objectUpdate("defines", cb_pack->defines);
        result->objectUpdate("declarations", cb_pack->extractor.getResults());
        result->objectUpdate("usr_map", cb_pack->extractor.getUsrMap());
        result->dump(&std::cout);
    }
};

class PrintDeclsNamesAction : public PluginASTAction {
    std::set<std::string> ParsedTemplates;

 protected:
    std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI, llvm::StringRef InFile) override {
        return llvm::make_unique<PrintDeclsConsumer>(CI, ParsedTemplates, InFile.str());
    }

    bool ParseArgs(const CompilerInstance &CI, const std::vector<std::string> &args) override {
        for (unsigned i = 0, e = args.size(); i != e; ++i) {
            llvm::errs() << "PrintDeclNames arg = " << args[i] << "\n";

            // Example error handling.
            DiagnosticsEngine &D = CI.getDiagnostics();
            if (args[i] == "-an-error") {
                unsigned DiagID = D.getCustomDiagID(DiagnosticsEngine::Error, "invalid argument '%0'");
                D.Report(DiagID) << args[i];
                return false;
            } else if (args[i] == "-parse-template") {
                if (i + 1 >= e) {
                    D.Report(D.getCustomDiagID(DiagnosticsEngine::Error, "missing -parse-template argument"));
                    return false;
                }
                ++i;
                ParsedTemplates.insert(args[i]);
            }
        }
        if (!args.empty() && args[0] == "help")
            PrintHelp(llvm::errs());

        return true;
    }
    void PrintHelp(llvm::raw_ostream &ros) { ros << "Help for PrintFunctionNames plugin goes here\n"; }
};
}  // namespace

static FrontendPluginRegistry::Add<PrintDeclsNamesAction> X("print-decls", "print declarations with json");
// clang++ -cc1 -load libPrintDecls.so  -plugin print-fns ~/work/blueboss/test/samples/macro_expansion.hpp
// clang++  -cc1 -load libPrintDecls.so  -plugin print-decls ~/work/blueboss/test/samples/macro_expansion.hpp
// clang++  -cc1 -load libPrintDecls.so  -plugin print-decls -I/home/sawai/local64/include/c++/v1/ -I/home/sawai/local64/lib/clang/3.9.0/include/ ~/work/blueboss/test/samples/size.hpp 
// clang++  -cc1 -load libPrintDecls.so  -plugin print-decls -plugin-arg-print-decls -parse-template -plugin-arg-print-decls AAA -I/home/sawai/local64/include/c++/v1/ -I/home/sawai/local64/lib/clang/3.9.0/include/ ~/work/blueboss/test/samples/size.hpp 
