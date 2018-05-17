/**
 * Copyright 2015- Co. Ltd. sizebook
 * @file global_functions.hpp
 * @brief
 * @author Shogo Sawai
 * @date 2018-05-17 10:31:57
 */
#ifndef GLOBAL_FUNCTIONS_HPP_
#define GLOBAL_FUNCTIONS_HPP_

#include <cstdint>
#include <string>
#include <vector>

// ---------- default ----------
/**
 *  - java <package_name>.Global
 * public static void func()
 * 
 *  - objc @class bb_Global
 * + (void) bb_func;
 */
void func();

/**
 *  - java <package_name>.Global
 * public static int return_int();
 * 
 *  - objc @class bb_Global
 * + (int) bb_return_int;
 */
int return_int();

// ---------- overloaded ----------

int32_t add(int32_t, int32_t);
double add(double, double);

std::string say_hello();
std::vector<std::string> get_names();


#endif  // GLOBAL_FUNCTIONS_HPP_
