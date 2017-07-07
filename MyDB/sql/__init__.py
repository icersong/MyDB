#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011-2011 Python Software Foundation
# Author: icewater.song
# Contact: icersong@gmail.com


from abstract import Abstract, SqlBase as Base


def set_auto_escape(flag=True):
    Abstract._auto_escape = flag

__all__ = [
    'Abstract',
    'fields',
    'condition',
    'joins',
    'select',
    'update',
    'insert',
    'delete',
    'table',
    'Base',
    'and_',
    'or_',
]
