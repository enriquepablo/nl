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

import os
import clips

from nl.metanl import Namable
from nl.thing import Thing
from nl.prop import Fact
from nl.rule import Rule
from nl.nltime import now
from nl.log import logger, history_dir
from nl import utils
from nl.nlc.compiler import yacc


def tell(*args):
    '''
    Take any number of sentences and rules and
    add them to clips.
    '''
    for sentence in args:
        s = sentence.put_action()
        logger.info(s)
        if isinstance(sentence, Rule):
            try:
                clips.Build(s)
            except:
                logger.error(clips.ErrorStream.Read())
                raise
        else:
            try:
                clips.Eval(s)
            except:
                logger.error(clips.ErrorStream.Read())
                raise
        sen = sentence.sen_tonl()
        if sen:
            utils.to_history(sen + '.')


def get_instancesn(*sentences):
    templs = []
    queries = []
    vrs = {}
    for n, sentence in enumerate(sentences):
        sentence.get_ism(templs, queries, vrs, newvar='q%d' % n)
    if len(queries) > 1:
        q = '(and %s)' % ' '.join(queries)
    else:
        q = queries and queries[0] or 'TRUE'
    clps = '(find-all-instances (%s) %s)' % \
            (' '.join(['(?%s %s)' % templ for templ in templs]), q)
    return clps, templs

def get_instances(*sentences):
    q, templs = get_instancesn(*sentences)
    logger.info(q)
    try:
        return clips.Eval(q), templs
    except:
        logger.error(clips.ErrorStream.Read())
        raise

def retract(sentence):
    for ins in get_instances(sentence):
        clips.FindInstance(ins).Remove()

def ask(*sentences):
    '''
    Retrieve objects from clips.
    sentences is a list of facts or things,
    and they can contain variables,
    whose scope is the set of sentences asked.
    return a list of dicts with the names of the variables
    used in the sentences asked as keys
    and the matched objects as values.
    If there are no variables in the
    question, but the asked sentences match,
    return True.
    if there is no match, return False
    '''
    clps, templs = get_instances(*sentences)
    resp = []
    if clps:
        names = [Namable.from_clips(ins) for ins in clps]
        while names:
            first = names[:len(templs)]
            names = names[len(templs):]
            rsp = {}
            for templ in templs:
                if utils.varpat.match(templ[0]) and not templ[0].startswith('Y'):
                    rsp[templ[0]] = str(first[templs.index(templ)])
            if rsp:
                resp.append(rsp)
        if not resp:
            resp = True
    else:
        resp = False
    return resp

def ask_obj(sentence):
    '''
    retrieve sentences in clips
    matching the given sentence.
    Can use variables.
    '''
    clps, templs = get_instances(sentence)
    sens = []
    if clps:
        if isinstance(sentence, Thing):
            for ins in clps:
                sens.append(Namable.from_clips(ins))
        elif isinstance(sentence, Fact):
            for ins in clps:
                i = clips.FindInstance(ins)
                if issubclass(utils.get_class(str(i.Class.Name)), Fact):
                    sens.append(Fact.from_clips(ins))
    return sens

def get_symbol(sym):
    '''
    '''
    try:
        return utils.get_class(sym)
    except KeyError:
        try:
            return ask_obj(Thing(sym))[0]
        except IndexError:
            return sym

def extend():
    '''
    Run the CLIPS machine;
    build or extend the rete network.
    To be used whenever new sentences
    or rules are added to clips,
    and we want to query the system.
    '''
    acts = clips.Run()
    return acts

def open_kb(name):
    utils.NAME = name
    # XXX wrong: this import writes into the history file,
    # that is read below, and thus is imported twice.
    now()
    try:
        __import__('nlp.ont.' + name, globals(), locals())
    except ImportError:
        pass
    history_file = os.path.join(history_dir, name + '.nl')
    if os.path.isfile(history_file):
        f = open(history_file, 'r')
        name, utils.NAME = utils.NAME, ''
        buff = ''
        for sen in f.readlines():
            sen = sen.strip()
            if sen and not sen.startswith('#'):
                buff += ' ' + sen
                if buff.endswith('.'):
                    yacc.parse(buff)
                    buff = ''
        utils.NAME = name
        f.close()
    extend()
    now()
