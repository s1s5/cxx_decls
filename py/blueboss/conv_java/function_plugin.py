# coding: utf-8
from blueboss import common as bc
import plugin
import jpath
import jclass
import function_converter


class FunctionPlugin(plugin.Plugin):
    def resolveFunctionClassPath(self, function_decl):
        l = function_decl.path.split('::')[:-1]
        return jclass.Class, jpath.JPath(
            tuple(l) + ('Global', ))

    def getFunctionConverter(self, func_decl, decl_class=None):
        return function_converter.FunctionConverter.check(self.creator,
                                                          func_decl)

    def declare(self, decl):
        if not isinstance(decl, bc.FunctionDecl):
            return False
        klass = self.creator.getFunctionClass(decl)
        if klass is None:
            return False
        klass.addFunction(self.creator.getFunctionConverter(decl))
        return True
