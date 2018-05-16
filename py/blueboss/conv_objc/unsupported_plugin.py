# coding: utf-8
import plugin
import objc_class
import arg_converter
import return_converter
import function_converter


class UnsupportedClass(objc_class.ObjCClass):
    def isValid(self):
        return False


class ArgConverter(arg_converter.ArgConverter):

    def isValid(self):
        return False


class ReturnConverter(return_converter.ReturnConverter):

    def isValid(self):
        return False


class FunctionConverter(function_converter.FunctionConverter):

    def isValid(self):
        return False

    def getReturnConverter(self):
        return None

    def getArgConverters(self):
        return []


class UnsupportedPlugin(plugin.Plugin):
    def resolveClass(self, decl_or_type):
        print decl_or_type, " resolveClass skipped..."
        return UnsupportedClass, ''

    def getFunctionConverter(self, func_decl, decl_class=None):
        print func_decl, decl_class, "getFunctionConverter skipped..."
        return FunctionConverter(self.creator, func_decl)

    def getArgConverter(self, arg_decl, func_conv):
        print arg_decl, "getArgConverter skipped...", func_conv.decl
        return ArgConverter(self.creator, arg_decl, func_conv)

    def getReturnConverter(self, ret_type, func_conv):
        print ret_type, "getReturnConverter skipped...", func_conv.decl
        return ReturnConverter(self.creator, ret_type, func_conv)

    def declare(self, decl):
        print decl, "declare skipped..."
        return True
