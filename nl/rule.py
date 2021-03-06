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

import uuid
from nl.metanl import Namable, Subword
from nl.nltime import Finish

class Rule(Namable):
    """
    A rule is instantiated with a list of premises or antecedents, or tail,
    and a list of consecuences, or consequents, or head.
    Both lists can contain objects of type Thing or of type Fact.
    Additionally, in the list of premises there can be objects of type
    During, Coincide, Arith and Subword.
    In the list of consecuences there can be objects of type
    Finish.
    """
    def __init__(self, prems, cons):
        self.name = uuid.uuid4().get_hex()
        self.prems = prems
        self.cons = sorted(cons, key=lambda x: isinstance(x, Finish) and 2 or 1)
        sane = False
        for x in xrange(len(self.prems)):
            if sane:
                break
            if isinstance(self.prems[0], Subword):
                self.prems = self.prems[1:] + [self.prems[0]]
            else:
                sane = True
        if not sane:
            raise SyntaxError('cannot have only subwords as prems')

    def put_action(self, vrs=None):
        """
        put rule in clips
        """
        if vrs is None:
            vrs = {}
        cprems = filter(None, map(lambda x:x.get_ce(vrs), self.prems))
        ccons = [con.put_action(vrs) for con in self.cons]
        return '(defrule %s %s => %s)' % (self.name,
                                          ' '.join(cprems),
                                          ' '.join(ccons))

    def sen_tonl(self):
        prems = ';\n    '.join([sen.sen_tonl() for sen in self.prems]).strip()
        cons = ';\n    '.join([sen.sen_tonl() for sen in self.cons]).strip()
        return 'if:\n    %s;\n  then:\n    %s' % (prems, cons)

