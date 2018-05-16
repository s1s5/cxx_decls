/**
 * Copyright (c) 
 * @file util.hpp
 * @brief
 * @author 
 * @date 
 */
#ifndef UTIL
#define UTIL

#include <clang/AST/Decl.h>
#include <clang/Basic/TargetInfo.h>

#include "json.hpp"

namespace util {
std::string getUSRPrefix();
std::vector<std::string> getDeclContext(const clang::Decl *decl);
std::string getAbsPath(const clang::NamedDecl *decl);
std::shared_ptr<Json> getTargetInfo(clang::TargetInfo *targetInfo);
// unified symbol resolutions
void setDeclUSR(std::shared_ptr<Json> o, const clang::Decl *decl);
std::string getDeclUSR(const clang::Decl *decl);
bool startswith(const char *p0, const char *p1);
}  // namespace util


#endif  // UTIL
