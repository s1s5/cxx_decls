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
void func();
int return_int();

// ---------- overloaded ----------

int32_t add(int32_t, int32_t);
double add(double d0, double d1);

std::string say_hello();
std::vector<std::string> get_names();

/**
 *  - java <package_name>.Global
 *
 *  public static void func() { ... }
 *  public static int return_int() { ... }
 *  public static int add(int arg0, int arg1) { ... }
 *  public static double add(double arg0, double arg1) { ... }
 *  public static String say_hello() { ... }
 *  public static String [] get_names() { ... }
 */

/**
 *  - objc @class bb_Global
 * 
 * @class bb_Global;
 * @interface bb_Global:NSObject {
 * }
 * + (void) bb_func;
 * + (int) bb_return_int;
 * + (int) bb_add:(int)arg0 arg1:(int)arg1;
 * + (double) bb_add:(double)d0 d1:(double)d1;
 * + (NSString *) bb_say_hello;
 * + (NSArray<NSString*> *) bb_get_names;
 * 
 * @end
 */

template<class X> void echo_hoge(const X &x);

#endif  // GLOBAL_FUNCTIONS_HPP_
