# coding: utf-8
from blueboss import common as bc
from blueboss import writer as bw


class Property(object):
    def __init__(self, type_, name, getter=None,
                 setter=None, other_attribs=None):
        self.type = type_
        self.name = name
        self.getter = getter
        self.setter = setter
        self.other_attribs = other_attribs

    def bw(self):
        return bw.objc.Property(self.type, self.name, self.getter,
                                self.setter, self.other_attribs)


class ObjCClass(object):
    def __init__(self, creator, name):
        self.creator = creator
        self.name = name
        self.bases = []
        self.funcs = []
        self.props = []
        self.protocols = []
        self.impl = None
        self.priority = 0
        self.is_valid = True
        self.has_delete = True

    def isValid(self):
        return self.is_valid

    def setValid(self, v):
        self.is_valid = v

    def isProtocol(self):
        return False

    def hasDelete(self, d):
        self.has_delete = d

    def addFunction(self, func):
        if func in self.funcs:
            return
        self.funcs.append(func)

    def addProperty(self, prop):
        if not isinstance(prop, Property):
            raise TypeError()
        self.props.append(prop)

    def addProtocol(self, p):
        if p in self.protocols:
            return
        self.protocols.append(p)

    def setImpl(self, decl):
        if not isinstance(decl, bc.RecordDecl):
            raise TypeError()
        self.impl = decl

    def addBase(self, base):
        if base in self.bases:
            return
        self.bases.append(base)

    def link(self):
        pass

    def objcHeader(self):
        bases = ['NSObject']
        if self.bases:
            bases = map(lambda x: x.name, self.bases)

        k = bw.objc.Interface(self.name, bases, True,
                              protocols=map(lambda x: x.name, self.protocols))
        for i in self.props:
            k << i.bw()
        for i in sorted(self.funcs, key=lambda x: x.getUid()):
            if not i.isValid():
                continue
            if i.isPrivate():
                continue
            k << bw.objc.FuncDec(*i.getFuncTuple())
        return k

    def objcSourceHeader(self):
        k = bw.objc.Interface(self.name, [], False)
        return k

    def objcSourcePrivate(self):
        pass

    def objcSourcePublic(self):
        k = bw.objc.Implementation(self.name)
        # if self.impl:
        #     k << bw.objc.Synthesize('impl')
        #     k << bw.objc.Synthesize('is_ref')
        if self.impl:
            f = bw.objc.Func("void", "dealloc", [])
            if self.has_delete:
                f << (bw.objc.If("self->is_ref == NO") << "delete self.i;")
            f << "self->impl = nullptr;"
            f << bw.objc.Statement("#if !__has_feature(objc_arc)", -9999)
            f << "[super dealloc];"
            f << bw.objc.Statement("#endif  // !__has_featur", -9999)
            k << f
        for i in sorted(self.funcs, key=lambda x: x.getUid()):
            if not i.isValid():
                continue
            f = bw.objc.Func(*i.getFuncTuple())
            i.dumpCCall(f)
            k << f
        return k


class BaseObjCClass(ObjCClass):
    def __init__(self, *args, **kw):
        super(BaseObjCClass, self).__init__(*args, **kw)
        self.priority = -1

    def objcHeader(self):
        bases = ['NSObject']
        if self.bases:
            bases = map(lambda x: x.name, self.bases)
        s = bw.objc.StatementList()
        k = bw.objc.Interface(self.name, bases, s)
        s << '@public'
        s << 'int tag;'
        s << 'void *impl;'
        s << 'NSObject *ref;'
        s << 'BOOL is_ref;'
        return k


class ObjCProtocol(ObjCClass):
    def isProtocol(self):
        return True

    def objcHeader(self):
        # bases = ['NSObject']
        # if self.bases:
        #     bases = map(lambda x: x.name, self.bases)
        k = bw.objc.Protocol(self.name)
        # for i in self.props:
        #     k << i.bw()
        for i in sorted(self.funcs, key=lambda x: x.getUid()):
            if not i.isValid():
                continue
            if i.isPrivate():
                continue
            if i.isStatic():
                continue
            k << bw.objc.FuncDec(*i.getFuncTuple())
        return k

    def objcSourceHeader(self):
        pass

    def objcSourcePrivate(self):
        pass

    def objcSourcePublic(self):
        pass
