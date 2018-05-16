# coding: utf-8
from blueboss import common as bc
import plugin
import function_converter
import objc_class


class FunctionPlugin(plugin.Plugin):
    def linkStart(self):
        self.functions = []

    def resolveFilter(self, decl_or_type):
        return isinstance(decl_or_type, bc.FunctionDecl)

    def resolveClass(self, function_decl):
        l = function_decl.path.split('::')
        if len(l) == 1:
            path = self.settings['global_class']
        else:
            l[0] = self.creator.settings['global_prefix'] + l[0]
            path = '_'.join(l[:-1])
        return objc_class.ObjCClass, path

    def getFunctionConverter(self, func_decl):
        return function_converter.FunctionConverter.check(self.creator,
                                                          func_decl)

    def declare(self, decl):
        if not isinstance(decl, bc.FunctionDecl):
            return False
        ins = self.creator.getClass(decl)
        ins.addFunction(self.creator.getFunctionConverter(decl))
        return True
