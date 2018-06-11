/**
 * Copyright 2015- Co. Ltd. sizebook
 * @file global_variables.hpp
 * @brief
 * @author Shogo Sawai
 * @date 2018-06-11 10:18:13
 */
#ifndef GLOBAL_VARIABLES_HPP_
#define GLOBAL_VARIABLES_HPP_

#include <cstdint>

namespace A {
class X {
 public:
    static uint32_t reg() { return 0; }
    static const std::uint32_t version;
};

const X global_x;
const std::uint32_t X::version = X::reg();

template<class T>
class V {
};

template<>
class V<int> {
 public:
    static uint32_t reg() { return 1; }
    static const std::uint32_t version;

    V(): t(0) {
    }

    void sayHello();
    int returnInt();
    int t;
};

const V<int> global_v_int;
const std::uint32_t V<int>::version = V<int>::reg();

}  // namespace A


#endif  // GLOBAL_VARIABLES_HPP_
