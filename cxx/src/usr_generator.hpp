/**
 * Copyright Shogo Sawai
 * @file usr_generator.hpp
 * @brief
 * @author shogo.sawai@gmail.com (Shogo Sawai)
 * @date 2016-05-26 09:56:57
 */
#ifndef USR_GENERATOR_HPP_
#define USR_GENERATOR_HPP_

#include "clang/AST/ASTContext.h"
#include "clang/AST/DeclTemplate.h"
#include "clang/AST/DeclVisitor.h"
#include "clang/Index/USRGeneration.h"
#include "clang/Lex/PreprocessingRecord.h"
#include "llvm/ADT/SmallString.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/raw_ostream.h"

bool generateUSRForDecl(const clang::Decl *D, llvm::SmallVectorImpl<char> &Buf);

#endif  // USR_GENERATOR_HPP_
