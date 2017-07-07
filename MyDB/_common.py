# -*- coding:utf8 -*-

################################################################
# Copyright (c) 2008 by icewater.song.
# Created: 2017-07-8
# Author: icersong
################################################################
import os, sys, threading, traceback


class ExException(Exception):
    def __init__(self, *args, **kvargs):
        super(ExException, self).__init__(*args, **kvargs)
        self.extract_tb = traceback.extract_tb(sys.exc_info()[-1])
        self.extract_stack = traceback.extract_stack()

    def tostring(self):
        traceinfo = ["Trace exceptions:"]
        traceinfo.extend(['  - ' + str(x)[1:-1] for x in self.extract_stack[:-1]])
        traceinfo.append("%s: %s" % (self.__class__.__name__, str([x for x in self.args if not isinstance(x, Exception)])[1:-1]))

        exceptions = [self]
        while exceptions[-1]:
            exceptions.extend([x for x in exceptions[-1].args if isinstance(x, Exception)] or [None])
        exceptions = exceptions[1:-1]

        traceinfo.extend(['  - ' + str(x)[1:-1] for x in self.extract_tb])

        for exception in exceptions:
            traceinfo.append("%s: %s" % (exception.__class__.__name__,
                                         str([x for x in exception.args if not isinstance(x, Exception)])[1:-1]))
            traceinfo.extend(['  - ' + str(x)[1:-1]
                              for x in (isinstance(exception, self.__class__) and exception.extract_tb or [])])

        return '\n'.join(traceinfo)


def debug(*args, **kvargs):
    """日志输出, 打印当前函数名称及行号"""

    threadid = threading.currentThread().ident
    frame = sys._getframe()
    lineno = frame.f_lineno
    while frame.f_back and frame.f_code.co_name in ('debug', 'info', 'warning', 'error'):
        frame = frame.f_back
        lineno = frame.f_lineno
    # print '[{0}] [{1} {2}:{3}]'.format(threadid, frame.f_code.co_name, frame.f_back.f_code.co_name, frame.f_back.f_lineno),
    # print '[{0}] [{1} {2}:{3}]'.format(threadid, frame.f_code.co_name, frame.f_back.f_code.co_name, lineno),
    msg = [u'[{0}] [{1}:{2}] [{3}]'.format(threadid, os.path.split(frame.f_code.co_filename)[1], lineno, frame.f_code.co_name)]

    for l in args:
        if isinstance(l, unicode):
            msg.append(l)
            continue
        if isinstance(l, basestring):
            for charset in ('UTF8', 'GB18030'):
                try:
                    msg.append(l.decode(charset))
                except:
                    continue
                break
            else:
                raise ExException(l)
            continue
        msg.append(u'{0}'.format(l))

    msg = u' '.join(msg)

    print msg.encode('GB18030')


class SingletonType(type):

    """ Singleton Metaclass """

    def __init__(cls, name, bases, dic):

        super(SingletonType, cls).__init__(name, bases, dic)

        cls.instance = None

    def __call__(cls, *args, **kwargs):

        if cls.instance is None:
            cls.instance = super(SingletonType, cls).__call__(*args, **kwargs)

        return cls.instance


def strval(var):
    """
    Convert var to unicode string
    """
    if isinstance(var, unicode):
        return var

    if isinstance(var, str):
        ee = []
        for c in ('UTF8', 'GB2312'):
            try:
                return var.decode(c)
            except Exception, e:
                ee.append(e)
        raise ExException(ee)
    if isinstance(var, float):
        s = str(var).strip('0')
        if s == '':
            s = '0'
        if s[0] == '.':
            s = '0' + s
        if s[-1] == '.':
            s = s + '0'
        var = s.find('e') < 0 and s or s.find('e-') < 0 and str(var) or ('%0.20f' % (var)).rstrip('0')
        # s = "%0.20g"%(var)
    else:
        var = hasattr(var, '__str__') and var.__str__() or str(var)
        assert(isinstance(var, (unicode, str)))

    return var
