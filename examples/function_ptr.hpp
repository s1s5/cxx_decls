/**
 * Copyright 2015- Co. Ltd. sizebook
 * @file function_ptr.hpp
 * @brief
 * @author Shogo Sawai
 * @date 2018-06-12 14:06:33
 */
#ifndef FUNCTION_PTR_HPP_
#define FUNCTION_PTR_HPP_

#include <functional>
#include <string>

void invoke(std::function<std::string(std::string)> f);

#endif  // FUNCTION_PTR_HPP_
