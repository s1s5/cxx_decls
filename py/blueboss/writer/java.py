# coding: utf-8
import base
import cxx

Statement = base.Statement
StatementList = base.StatementList
If = cxx.If
ElseIf = cxx.ElseIf
Else = cxx.Else
For = cxx.For
Switch = cxx.Switch
Case = cxx.Case
Try = cxx.Try
Catch = cxx.Catch


class FuncDecl(base.Statement):
    def __init__(self, retval, name, args, access=""):
        if access:
            access += " "
        super(FuncDecl,
              self).__init__(cxx.func_dec(access + retval, name, args) + ';')


class Func(cxx.BraceBlock):
    def __init__(self, retval, name, args,
                 access="public", is_static="", annotations=""):
        if is_static:
            is_static = "static"
        self.name = name
        self.decl = cxx.func_dec(
            ' '.join(filter(lambda x: x, [access, is_static, retval])), name,
            args)
        super(Func, self).__init__(self.decl, after=True)


class Interface(cxx.BraceBlock):
    def __init__(self, class_name, interfaces=[], access=""):
        prefix = ""
        if access:
            prefix = access + " "
        ex = ""
        if interfaces:
            ex = " extends " + (', '.join(interfaces))
        super(Interface, self).__init__('%sinterface %s%s' %
                                        (prefix, class_name, ex),
                                        after=True)


class Class(cxx.BraceBlock):
    def __init__(self, class_name, base=None, interfaces=[], access=""):
        prefix = ""
        if access:
            prefix = access + " "
        ex = ""
        if base:
            ex = " extends %s" % base
        im = ""
        if interfaces:
            im = " implements " + (', '.join(interfaces))
        super(Class, self).__init__('%sclass %s%s%s' %
                                    (prefix, class_name, ex, im),
                                    after=True)


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
