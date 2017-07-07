#!/usr/bin python
# -*- coding: UTF8 -*-
# Copyright (C) 2011 Python Software Foundation
# Author: icewater.song
# Contact: icersong@gmail.com

""" UTF8文件编码  """

__version__ = '1.0.0'

import re
from abstract import tovalue


class Sets(object):
    def set(self, *args, **kwargs):
        """
        参数方式:
        1) 字符模式：set("key=value")
        2) 键值模式：set(key, value)
        3) 字典模式：set(key = value, ...)
        4) 数组模式：set((key, value), ...)
        """

        if not hasattr(self, '_sets'):
            self._sets = []

        assert(args or kwargs)

        # 字典模式; set(key=value, ...)
        for k, v in kwargs.items():
            self._sets.append(u"`{0}`={1}".format(k.strip(' \t`'), tovalue(v, self._auto_escape)))

        # 字符串模式; set('a=b')
        if len(args) == 1 and isinstance(args[0], basestring):
            self._sets.append(args[0])
            return self

        # KV模式; set(key, value)
        if len(args) == 2 and isinstance(args[0], basestring) and re.match('`?\w+`?', args[0]):
            self._sets.append(u"`{0}`={1}".format(args[0], tovalue(args[1], self._auto_escape)))
            return self

        # 数组模式: set((key, value), ...)
        for k, v in args:
            self._sets.append(u"`{0}`={1}".format(k.strip('` \t\r\n'), tovalue(v)))

        return self

    def get_sets(self):
        return self._sets_string()

    def has_sets(self):
        return not not getattr(self, '_sets', None)

    def _sets_string(self):
        return ', '.join(getattr(self, '_sets', []))


class SetsMixIn(Sets):
    pass


class UpdateMixIn:
    def update(self, *args, **kwargs):
        if not hasattr(self, '_update'):
            self._update = Sets()
        self._update._auto_escape = self._auto_escape
        self._update.set(*args, **kwargs)
        return self

    def duplicate(self, *args, **kwargs):
        if not hasattr(self, '_update'):
            self._update = Sets()
        self._update._auto_escape = self._auto_escape
        self._update.set(*args, **kwargs)
        return self

    def get_update(self):
        return hasattr(self, '_update') and self._update.get_sets()

    def has_update(self):
        return hasattr(self, '_update') and self._update.has_sets()

    def _update_string(self):
        return self._update._sets_string() if hasattr(self, '_update') else ''
