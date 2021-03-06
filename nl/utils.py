# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 by Enrique Pérez Arnaud <enriquepablo@gmail.com>
#
# This file is part of nlproject.
#
# The nlproject is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The nlproject is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any part of the nlproject.
# If not, see <http://www.gnu.org/licenses/>.

import time
import re
import pkg_resources  # setuptools specific

from nl.log import logger, get_history

NAME = ''

# vars are always XNUM
t_VAR = r'([A-Z][a-z_]*)(Verb|Noun|Word)?\d+'
varpat = re.compile(t_VAR)

plugins = []


def load_plugins():
    '''setuptools based plugin loader'''
    entrypoint = 'nl.new_fact'
    for entrypoint in pkg_resources.iter_entry_points(entrypoint):
        plugin = entrypoint.load()
        plugins.append(plugin)

# XXX not thread safe
_vn = 0

def _newvar():
    global _vn
    _vn += 1
    return 'Y%d' % _vn


subclasses = {}
def register(clsname, cls):
    subclasses[clsname.lower()] = cls

def get_class(cls):
    if isinstance(cls, basestring):
        try:
            import nl
            return getattr(nl, cls.capitalize())
        except AttributeError:
            return subclasses[cls.lower()]
    return cls


def clips_instance(ancestor, mod_path, meths=None):
    send_str = '(send ?%s get-%s)'
    meth_str = '(%s ?%s)'
    for mod in mod_path:
        if ancestor.startswith('('):
            send_str = '(send %s get-%s)'
        ancestor = send_str % (ancestor, mod)
        send_str = '(send %s get-%s)'
        meth_str = '(%s %s)'
    if meths:
        for meth in meths:
            ancestor = meth_str % (meth, ancestor)
            meth_str = '(%s %s)'
    return possible_var(ancestor)

def possible_var(var):
    if varpat.match(var):
        return '?%s' % var
    return var

_now = 0.0
_time_granularity = 1.0
_time_start_delta = 0

def change_now(i=0):
    'deprecated'
    global _now
    delta = float(int(time.time())) - _now
    logger.debug('OOOOOOOOOOOOOO %f' %  delta)
    _now = i and float(i) or \
            float(_now) + 1000.0

def parens(expr):
    """
    >>> from nl.arith import parens
    >>> parens('uno')
    'uno'
    >>> parens('(uno (dos tres) cuatro)')
    ['uno', '(dos tres)', 'cuatro']
    >>> parens('(uno (dos tres) (ho ho (he (ha ha))) cuatro)')
    ['uno', '(dos tres)', '(ho ho (he (ha ha)))', 'cuatro']
    """
    if expr[0] != '(':
        return expr
    depth = 0
    term = ''
    terms = []
    for c in expr:
        if depth == 1 and c == ' ':
            terms.append(term)
            term = ''
        elif c == '(':
            depth += 1
            if depth > 1:
                term += c
        elif c == ')':
            depth -= 1
            if depth > 0:
                term += c
        else:
            term += c
    terms.append(term)
    if depth != 0:
        raise ValueError('wrong arithmetic expression')
    return terms

def get_subclasses(cls):
    return [subclass[0] for subclass in subclasses.items()
            if issubclass(subclass[1], cls)]

def var_tonl(var):
    #if isinstance(var.value, basestring) and varpat.match(var.value):
    #    classname = var.__class__.__name__
    #    return classname + var.value
    return var.value

def to_history(s):
    if NAME:
        history = get_history(NAME)
        history.info(s)

def now(new=0):
    global _now
    if new:
        if new < _now:
            raise ValueError('Time cannot go backwards')
        _now = float(new)
    else:
        t = float(int(time.time() * _time_granularity))
        delta = t - _now
        delta = delta < 1 and 1.0 or delta
        _now = _now + _time_start_delta + delta
    return _now

def time_granularity(gr):
    _time_granularity = gr

def start_of_time(start_delta):
    _time_start_delta = start_delta
    now()
