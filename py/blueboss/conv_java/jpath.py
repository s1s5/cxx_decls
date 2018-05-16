# coding: utf-8
class JPath(object):

    def __init__(self, path, is_sys=False, package_path=None, class_path=None):
        self.path = path
        self.is_sys = is_sys
        if package_path is not None:
            self.package_path = tuple(package_path)
            self.class_path = tuple(class_path)
        else:
            self.package_path = None
            self.class_path = None

    def set(self, package_path, class_path):
        self.package_path = tuple(package_path)
        self.class_path = tuple(class_path)

    def isSys(self):
        return self.is_sys

    def getJniFuncName(self, name):
        pp = map(lambda x: x.replace('_', '_1'), self.package_path)
        cp = map(lambda x: x.replace('_', '_1'), self.class_path)
        jni_prefix = 'Java_' + '_'.join(pp) + '_'
        jni_prefix += '_00024'.join(cp)
        jni_method_name = jni_prefix + '_' + name
        return jni_method_name

    def getPackagePath(self):
        if self.class_path is None:
            return '.'.join(self.path)
        return '.'.join(self.package_path)

    def getClassPath(self):
        if self.class_path is None:
            return '.'.join(self.path)
        # return '.'.join(self.class_path)
        return '.'.join(self.package_path + self.class_path)

    def getImportPath(self):
        return '.'.join(self.package_path + (self.class_path[0], ))

    def __str__(self):
        # return '/'.join(['.'.join(self.package_path)
        # , '.'.join(self.class_path)
        #                  ])
        return '/'.join(['.'.join(self.path)])

    def __nonzero__(self):
        # return self.package_path + self.class_path != ()
        return self.path != ()

    def __eq__(self, o):
        return self.path == o.path
        # a = self.package_path + self.class_path
        # b = o.package_path + o.class_path
        # c = (self.package_path == o.package_path and
        #      self.class_path == o.class_path)
        # if a == b and not c:
        #     raise Exception()
        # return c

    def __hash__(self):
        return hash(self.path)
        # return hash(self.package_path + self.class_path)


ByteBuffer = JPath(('java', 'nio', 'ByteBuffer', ), True,
                   ('java', 'nio'), ('ByteBuffer', ))
ByteOrder = JPath(('java', 'nio', 'ByteOrder', ), True,
                  ('java', 'nio'), ('ByteOrder', ))
String = JPath(('String', ), True, (), ('String', ))
