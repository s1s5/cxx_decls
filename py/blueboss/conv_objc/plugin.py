# coding: utf-8


class Plugin(object):

    def __init__(self, creator, settings, target_info):
        self.creator = creator
        self.settings = settings
        self.target_info = target_info

    def depends(self):
        return []

    def linkStart(self):
        pass

    def resolveFilter(self, decl_or_type):
        return True

    def converterFilter(self, *args):
        return True

    def resolveClass(self, decl_or_type):
        pass

    def getFunctionConverter(self, func_decl):
        return None

    def getArgConverter(self, arg_decl, func_conv):
        return None

    def getReturnConverter(self, ret_type, func_conv):
        return None

    def declare(self, decl):
        return False

    def hook(self, decl_or_type):
        pass

    def linkEnd(self):
        pass

    def objcHeader(self):
        pass

    def objcSourceHeader(self):
        pass

    def objcSourcePrivate(self):
        pass

    def objcSourcePublic(self):
        pass
