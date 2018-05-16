# coding: utf-8
import StringIO
import base

Statement = base.Statement
StatementList = base.StatementList


class BraceBlock(base.IndentedBlock):
    def __init__(self, *args, **kw):
        super(BraceBlock, self).__init__('{\n', '}', *args, **kw)


class If(BraceBlock):
    def __init__(self, cond):
        super(If, self).__init__('if (%s)' % cond)

    def connect(self, after):
        if (isinstance(after, ElseIf) or isinstance(after, Else)):
            return True
        return False


class ElseIf(BraceBlock):
    def __init__(self, cond):
        super(ElseIf, self).__init__('else if (%s)' % cond)

    def connect(self, after):
        if (isinstance(after, ElseIf) or isinstance(after, Else)):
            return True
        return False


class Else(BraceBlock):
    def __init__(self):
        super(Else, self).__init__('else')


class Switch(BraceBlock):
    def __init__(self, cond):
        super(Switch, self).__init__('switch (%s)' % cond)


class Case(BraceBlock):
    def __init__(self, cond):
        super(Case, self).__init__('case %s:' % cond)


class For(BraceBlock):
    def __init__(self, st, cond, it):
        super(For, self).__init__('for (%s; %s; %s)' % (st, cond, it))


class ForEach(BraceBlock):
    def __init__(self, it, iterable):
        super(ForEach, self).__init__('for (%s : %s)' % (it, iterable))


def func_dec(retval, name, args, is_const=False):
    fp = StringIO.StringIO()
    fp.write(retval)
    if retval:
        fp.write(' ')
    fp.write(name)
    fp.write('(')
    for i, arg in enumerate(args):
        if i:
            fp.write(', ')
        if (isinstance(arg, str) or isinstance(arg, unicode)):
            fp.write(arg)
        else:
            fp.write(arg[0])
            fp.write(" ")
            fp.write(arg[1])
            if len(arg) > 2:
                fp.write("=")
                fp.write(arg[2])
    fp.write(')')
    if is_const:
        fp.write(' const')
    return fp.getvalue()


class FuncDec(base.Statement):
    def __init__(self, retval, name, args, is_const=False):
        super(FuncDec, self).__init__(
            func_dec(retval, name, args, is_const) + ';')


class Func(BraceBlock):
    def __init__(self, retval, name, args, is_const=False):
        self.name = name
        self.decl = func_dec(retval, name, args, is_const)
        super(Func, self).__init__(self.decl, after=True)


class Struct(BraceBlock):
    def __init__(self, class_name):
        super(Struct, self).__init__('struct %s' % class_name, after=";")


class Class(BraceBlock):
    def __init__(self, class_name):
        super(Class, self).__init__('class %s' % class_name, after=";")

    def public(self):
        self << base.Statement('public', -3)
        return self

    def protected(self):
        self << base.Statement('protected', -3)
        return self

    def private(self):
        self << base.Statement('private', -3)
        return self


class Namespace(BraceBlock):
    def __init__(self, name=""):
        self.name = name
        if self.name:
            ns = 'namespace %s' % self.name
        else:
            ns = 'namespace'
        afns = '  // %s' % ns
        super(Namespace, self).__init__(prev=ns, after=afns, indent=0)


class Try(BraceBlock):
    def __init__(self):
        super(Try, self).__init__('try')

    def connect(self, after):
        if isinstance(after, Catch):
            return True
        return False


class Catch(BraceBlock):
    def __init__(self, throwable, var):
        super(Catch, self).__init__('catch (%s %s)' % (throwable, var))

    def connect(self, after):
        if isinstance(after, Catch):
            return True
        return False


class Lambda(BraceBlock):
    def __init__(self, varname, args, retval='', capture=''):
        fp = StringIO.StringIO()
        for i, arg in enumerate(args):
            if i:
                fp.write(', ')
            if (isinstance(arg, str) or isinstance(arg, unicode)):
                fp.write(arg)
            else:
                fp.write(arg[0])
                fp.write(" ")
                fp.write(arg[1])
                if len(arg) > 2:
                    fp.write("=")
                    fp.write(arg[2])
        if retval:
            retval = '-> %s ' % retval
        else:
            retval = ''
        pr = 'auto %s = [%s](%s) %s' % (
            varname, capture, fp.getvalue(), retval)
        af = ';'
        super(Lambda, self).__init__(pr, af)


def main(args):
    pass


def __entry_point():
    import argparse
    parser = argparse.ArgumentParser(
        description=u'',  # プログラムの説明
    )
    parser.add_argument("args", nargs="*")
    # parser.add_argument(
    #     '-f', '--foo',
    #     # append, append_const, store_const, store_false, store_true
    #     action='store',
    #     # nargs=<digit>, "?", "*", "+",
    #     nargs=None,
    #     # 引数なし、固定の値を入れるとき
    #     const=None,
    #     default=None,
    #     # int, type=argparse.FileType('r')
    #     type=str,
    #     # choices=[iterable]
    #     choices=None,
    #     help='help text here',
    #     metavar="<metavar>",
    #     dest="dest_field",
    # )

    # parser.add_argument('--verbose', action='store_true',
    #                     help='make noise', dest="verbose")
    # subparsers = parser.add_subparsers(help='sub-command help')

    # parser_a = subparsers.add_parser('a', help='a help')
    # parser_a.add_argument('aaa', type=int, help='aaa help')
    # parser_a.set_defaults(which="a")

    main(parser.parse_args().args)

if __name__ == '__main__':
    __entry_point()
