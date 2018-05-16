# coding: utf-8
import StringIO


class Statement(object):
    def __init__(self, s, ri=0):
        self.s = s
        self.ri = ri

    def dump(self, fp, p=None, n=None, indent=0):
        if indent + self.ri > 0:
            fp.write(' ' * (indent + self.ri))
        fp.write(self.s)
        fp.write('\n')


class StatementList(Statement):
    def __init__(self):
        super(StatementList, self).__init__("")
        self.l = []

    def __lshift__(self, a):
        if a is None:
            return self
        if isinstance(a, str) or isinstance(a, unicode):
            a = Statement(a)
        if not isinstance(a, Statement):
            raise TypeError()
        self.l.append(a)
        return self

    # def write(self, *a):
    #     for i in a:
    #         if i == '\n':
    #             continue
    #         self << i
    #     return self

    def dump(self, fp, p=None, n=None, indent=0):
        if len(self.l) == 1:
            self.l[0].dump(fp, None, None, indent)
            return
        p = None
        for idx, i in enumerate(self.l):
            if idx < len(self.l) - 1:
                n = self.l[idx + 1]
            else:
                n = None
            i.dump(fp, p, n, indent)
            p = i

    # def __str__(self):
    #     return self

    def __unicode__(self):
        sio = StringIO.StringIO()
        self.dump(sio)
        return sio.getvalue()


class IndentedBlock(StatementList):
    def __init__(self,
                 prev_block="",
                 after_block="",
                 prev="",
                 after="",
                 indent=4):
        super(IndentedBlock, self).__init__()
        self.prev_block = prev_block
        self.after_block = after_block
        self.prev = prev
        self.after = after
        self.indent = indent
        self.prev_space = ' '

    def connect(self, after):
        return False

    def dump(self, fp, p=None, n=None, indent=0):
        if isinstance(p, IndentedBlock) and p.connect(self):
            fp.write(' ')
        else:
            fp.write(' ' * indent)
        if self.prev:
            if isinstance(self.prev, Statement):
                self.prev.dump(fp, indent=indent)
            else:
                fp.write(self.prev)
                fp.write(self.prev_space)
        fp.write(self.prev_block)
        super(IndentedBlock, self).dump(fp,
                                        p=None,
                                        n=None,
                                        indent=indent + self.indent)
        fp.write(' ' * indent)
        fp.write(self.after_block)
        if self.after is not True:
            if isinstance(self.after, Statement):
                self.after.dump(fp, indent=indent)
            else:
                fp.write(self.after)

        if isinstance(n, IndentedBlock) and self.connect(n):
            pass
        else:
            fp.write('\n')


def main(args):
    # c = Class("Hoge")
    # (c.public() << FuncDec("void", "foo", [])
    #  << FuncDec("void", "bar", [("int", "xx")]))
    # (c.private() << FuncDec("", "Hoge", []))
    # print >> c, "hoge", "hoge"
    # # c.dump(sys.stdout)
    # print c
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
