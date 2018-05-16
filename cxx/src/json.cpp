/**
 * Copyright 2015 Co. Ltd. sizebook
 * @file json.cpp
 * @brief
 * @author Shogo Sawai (sawai@sizebook.co.jp)
 * @date 2015-11-13 15:46:30
 */
#include "json.hpp"

std::shared_ptr<Json> Json::mkBool(bool b) {
    std::shared_ptr<Json> j(new Json(Type::BOOL));
    j->b = b;
    return j;
}

std::shared_ptr<Json> Json::mkInt(int i) {
    std::shared_ptr<Json> j(new Json(Type::INTEGER));
    j->i = i;
    return j;
}

std::shared_ptr<Json> Json::mkString(const std::string &s) {
    std::shared_ptr<Json> j(new Json(Type::STRING));
    j->s = s;
    return j;
}

std::shared_ptr<Json> Json::mkArray() {
    std::shared_ptr<Json> j(new Json(Type::ARRAY));
    return j;
}

std::shared_ptr<Json> Json::mkObject() {
    std::shared_ptr<Json> j(new Json(Type::OBJECT));
    return j;
}
std::shared_ptr<Json> Json::mkNull() {
    std::shared_ptr<Json> j(new Json(Type::NULL_));
    return j;
}


void Json::arrayAppend(const std::shared_ptr<Json> &value) {
    a.push_back(value);
}

void Json::objectUpdate(const std::string &key,
                        const std::shared_ptr<Json> &value) {
    o[key] = value;
}

picojson::value Json::convert() const {
    switch (type) {
      case Type::NULL_:
          return picojson::value();
      case Type::BOOL:
          return picojson::value(b);
      case Type::INTEGER:
          return picojson::value(static_cast<double>(i));
      case Type::STRING:
          return picojson::value(s);
      case Type::ARRAY: {
          picojson::array aa;
          for (auto iter = a.begin(), end = a.end(); iter != end; iter++) {
              aa.push_back((*iter)->convert());
          }
          return picojson::value(aa);
      }
      case Type::OBJECT: {
          picojson::object oo;
          for (auto iter = o.begin(), end = o.end(); iter != end; iter++) {
              oo.insert(std::make_pair(iter->first, iter->second->convert()));
          }
          return picojson::value(oo);
      }
    }
    return picojson::value();
}

void Json::dump(std::ostream *ss, int indent, bool force) {
    (*ss) << convert().serialize(true);
#if 0
    auto print_indent = [=](int ind, bool f) {
        if (f) {
            for (int i = 0; i < ind; i++) {
                (*ss) << ' ';
            }
        }
    };
    print_indent(indent, force);
    switch (type) {
      case Type::BOOL: {
          (*ss) << (b ? "true" : "false");
          break;
      }
      case Type::INTEGER: {
          (*ss) << i;
          break;
      }
      case Type::STRING: {
          (*ss) << '"' << s << '"';
          break;
      }
      case Type::ARRAY: {
          (*ss) << "[" << std::endl;
          for (auto iter = a.begin(), end = a.end(); iter != end; ) {
              (*iter)->dump(ss, indent + 2, true);
              iter++;
              if (iter != end) {
                  (*ss) << ",";
              }
              (*ss) << std::endl;
          }
          print_indent(indent, true);
          (*ss) << "]";
          break;
      }
      case Type::OBJECT: {
          (*ss) << "{" << std::endl;
          for (auto iter = o.begin(), end = o.end(); iter != end; ) {
              print_indent(indent + 2, true);
              (*ss) << '"' << (*iter).first << '"' << ": ";
              (*iter).second->dump(ss, indent + 2, false);
              iter++;
              if (iter != end) {
                  (*ss) << ",";
              }
              (*ss) << std::endl;
          }
          print_indent(indent, true);
          (*ss) << "}";
          break;
      }
    }
#endif
}
