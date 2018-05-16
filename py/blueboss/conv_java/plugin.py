# coding: utf-8
class Plugin(object):
    def __init__(self, creator, settings, target_info):
        self.creator = creator
        self.settings = settings
        self.target_info = target_info

    def includes(self):
        return []

    def includesSys(self):
        return []

    def depends(self):
        return []

    def linkStart(self):
        pass

    def resolveFilter(self, decl_or_type):
        return True

    def resolveInterfacePath(self, decl_or_type):
        return None

    def resolveClassPath(self, decl_or_type):
        return None

    def resolveFunctionClassPath(self, function_decl):
        return None

    def converterFilter(self, *args):
        return True

    def getFunctionConverter(self, func_decl, decl_class=None):
        return None

    def getArgConverter(self, arg_decl, func_conv):
        return None

    def getReturnConverter(self, ret_type, func_conv):
        return None

    def walkUsr(self, decl):
        pass

    def walkUsrEnd(self):
        pass

    def declare(self, decl):
        return False

    def hook(self, decl_or_type):
        pass

    def linkEnd(self):
        pass

    def jniHeader(self):
        pass

    def jniSource(self):
        pass
