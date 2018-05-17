# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys
import os
import subprocess
import uuid
import shutil
import json

from blueboss import common as bc


def print_help():
    print("USAGE : [command] [opts]")


def main(args):
    if len(args) == 0 or args[0] == help:
        print_help()

    if args[0] == 'json':
        try:
            output = subprocess.check_output(
                ['clang', '-Xclang', '-load',
                 '-Xclang', '/usr/local/lib/CXXDeclsExtractor.so',
                 '-Xclang', '-plugin', '-Xclang', 'print-decls'] + args[1:]
            )

            js = bc.loadJson(bc.mergeJson(json.loads(output)))
            messages = []
            for i in js.diagnostics:
                if (i.level == 'fatal' or i.level == 'error'):
                    print("-" * 30)
                    i.show(sys.stderr)
                    messages.append(i)
            print(output)
            if messages:
                sys.exit(1)
        except subprocess.CalledProcessError as exc:
            print("Status : FAIL", exc.returncode, exc.output, file=sys.stderr)
    elif args[0] == 'java':
        tmp_dir = '/tmp/{}'.format(uuid.uuid4().hex)
        try:
            output = subprocess.check_output(
                ['python', '-m', 'blueboss.conv_java',
                 '--dst-dir', tmp_dir,
                 '--default-package', args[1],
                 '--libname', args[2],
                 '--jni-filename', os.path.join(tmp_dir, 'jniex.cpp')] + args[3:],
                stderr=subprocess.STDOUT,
            )
            output = output.strip()
            if output:
                sys.stderr.write(output)
                sys.stderr.write('\n')
                sys.stderr.flush()
                # with open(os.path.join(tmp_dir, 'log'), 'w') as fp:
                #     fp.write(output)

            subprocess.check_call(
                ['tar', '-C', tmp_dir,
                 '--create', '-f', '-', '.'])
        except subprocess.CalledProcessError as exc:
            print("Status : FAIL", exc.returncode, exc.output, file=sys.stderr)
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    elif args[0] == 'objc':
        tmp_dir = '/'
        while os.path.exists(tmp_dir):
            tmp_dir = '/tmp/{}'.format(uuid.uuid4().hex)

        try:
            os.mkdir(tmp_dir)

            output = subprocess.check_output(
                ['python', '-m', 'blueboss.conv_objc',
                 '--dst-header', os.path.join(tmp_dir, '{}.h'.format(args[1])),
                 '--dst-source', os.path.join(tmp_dir, '{}.mm'.format(args[1]))] + args[2:],
                stderr=subprocess.STDOUT,
            )
            output = output.strip()
            if output:
                sys.stderr.write(output)
                sys.stderr.write('\n')
                sys.stderr.flush()
                # with open(os.path.join(tmp_dir, 'log'), 'w') as fp:
                #     fp.write(output)
            subprocess.check_call(
                ['tar', '-C', tmp_dir,
                 '--create', '-f', '-', '.'])
        except subprocess.CalledProcessError as exc:
            print("Status : FAIL", exc.returncode, exc.output, file=sys.stderr)
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
    else:
        print_help()


def __entry_point():
    main(sys.argv[1:])


if __name__ == '__main__':
    __entry_point()
