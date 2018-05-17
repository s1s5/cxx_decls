/**
 * Copyright (c)
 * @file json.hpp
 * @brief
 * @author Shogo Sawai (sawai@sizebook.co.jp)
 * @date 2015-11-13 15:42:51
 */
#ifndef JSON_HPP_
#define JSON_HPP_

#include <map>
#include <memory>
#include <ostream>
#include <string>
#include <vector>

#include "picojson.h"

class Json {
 public:
    enum class Type {
        NULL_,
        BOOL,
        INTEGER,
        STRING,
        ARRAY,
        OBJECT,
    };

    Type type;

    bool b;
    int i;
    std::string s;
    std::vector<std::shared_ptr<Json>> a;
    std::map<std::string, std::shared_ptr<Json>> o;

    explicit Json(Type t) : type(t) {}

    void dump(std::ostream *ss, int indent = 0, bool force = false);

    static std::shared_ptr<Json> mkBool(bool b);
    static std::shared_ptr<Json> mkInt(int i);
    static std::shared_ptr<Json> mkString(const std::string &s);
    static std::shared_ptr<Json> mkArray();
    static std::shared_ptr<Json> mkObject();
    static std::shared_ptr<Json> mkNull();

    void arrayAppend(const std::shared_ptr<Json> &value);
    void objectUpdate(const std::string &key,
                      const std::shared_ptr<Json> &value);

    void add(bool _b) { arrayAppend(mkBool(_b)); }
    void add(int _i) { arrayAppend(mkInt(_i)); }
    void add(const char *_s) { arrayAppend(mkString(_s)); }
    void add(const std::string &_s) { arrayAppend(mkString(_s)); }
    void add(const std::shared_ptr<Json> &value) { arrayAppend(value); }
    void set(const std::string &key) { objectUpdate(key, mkNull()); }
    void set(const std::string &key, bool _b) { objectUpdate(key, mkBool(_b)); }
    void set(const std::string &key, int _i) { objectUpdate(key, mkInt(_i)); }
    void set(const std::string &key, const char *_s) {
        objectUpdate(key, mkString(_s));
    }
    void set(const std::string &key, const std::string &_s) {
        objectUpdate(key, mkString(_s));
    }
    void set(const std::string &key, const std::shared_ptr<Json> &value) {
        objectUpdate(key, value);
    }

    picojson::value convert() const;
};

#endif  // JSON_HPP_
