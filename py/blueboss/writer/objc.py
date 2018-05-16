# coding: utf-8
import StringIO
import base
import cxx

Statement = base.Statement
StatementList = base.StatementList
BraceBlock = cxx.BraceBlock
If = cxx.If
ElseIf = cxx.ElseIf
Else = cxx.Else
Switch = cxx.Switch
Case = cxx.Case
For = cxx.For


def func_dec(retval, name, args, is_static=False):
    fp = StringIO.StringIO()
    if is_static:
        fp.write("+ ")
    else:
        fp.write("- ")
    if retval:
        fp.write("(%s) " % retval)
    fp.write(name)
    for i, arg in enumerate(args):
        if i:
            fp.write(' %s:(%s)%s' % arg)
        else:
            fp.write(':(%s)%s' % arg[1:])
    return fp.getvalue()


class FuncDec(base.Statement):

    def __init__(self, retval, name, args, is_static=False):
        super(FuncDec, self).__init__(
            func_dec(retval, name, args, is_static) + ';')


class Func(BraceBlock):

    def __init__(self, retval, name, args, is_static=False):
        self.name = name
        self.decl = func_dec(retval, name, args, is_static)
        super(Func, self).__init__(self.decl, after=True)


class ForEach(BraceBlock):
    def __init__(self, it, iterable):
        super(ForEach, self).__init__('for (%s : %s)' % (it, iterable))


class Property(Statement):

    def __init__(self, type_, var_name, getter=None,
                 setter=None, other_attribs=None):
        props = ''
        if getter or setter:
            if getter:
                props += 'getter = %s' % getter
            if setter:
                if props:
                    props += ', '
                props += 'setter = %s:' % setter
            elif getter:
                props += ', readonly'
        if other_attribs:
            if props:
                props += ', '
            props += other_attribs
        if props:
            props = '(%s)' % props
        super(Property, self).__init__("@property %s%s %s;" %
                                       (props, type_, var_name))


class Synthesize(Statement):

    def __init__(self, a):
        super(Synthesize, self).__init__("@synthesize %s = %s;" % (a, a))


class ClassDecl(base.Statement):

    def __init__(self, name, is_protocol):
        p = 'class'
        if is_protocol:
            p = 'protocol'
        super(ClassDecl, self).__init__("@%s %s;" % (p, name))


class Interface(base.IndentedBlock):

    def __init__(self, name, bases, brace=None, protocols=None):
        bases_str = ''
        if bases:
            bases_str = ':' + ', '.join(bases)
        pstr = ''
        if protocols:
            pstr = '<%s>' % (', '.join(protocols))
        p = '@interface %s%s%s' % (name, bases_str, pstr, )
        if brace:
            p = BraceBlock(prev=p)
            if brace is True:
                pass
            else:
                p << brace
        else:
            p += '()\n'
        a = '\n@end'
        super(Interface, self).__init__('', '', p, a, 0)
        self.prev_space = ''


class Protocol(base.IndentedBlock):
    def __init__(self, name):
        p = '@protocol %s' % (name, )
        a = '\n@end'
        super(Protocol, self).__init__('\n', '', p, a, 0)


class Implementation(base.IndentedBlock):

    def __init__(self, name):
        super(Implementation, self).__init__(
            '', '', '@implementation %s\n' % name, '\n@end', 0)
        self.prev_space = ''


class Enum(BraceBlock):
    def __init__(self, name):
        super(Enum, self).__init__("typedef enum : NSInteger", "%s;" % name)
