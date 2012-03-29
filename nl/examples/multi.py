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

import nl


class Uno_verb(nl.Exists):
    subject = nl.Thing
    mods = {'to': nl.Thing}

r1 = nl.Rule([
        nl.Fact(nl.Thing('Thing1'), nl.Verb('Uno_verb1', Uno_verb)(to=nl.Thing('Thing2'))),
        ],[
        nl.Fact(nl.Thing('Thing2'), nl.Verb('Uno_verb1', Uno_verb)(to=nl.Thing('Thing1'))),
        ])

class Dos_verb(nl.Exists):
    subject = nl.Thing
    mods = {'to': nl.Thing}

uno = nl.Thing('uno')

r2 = nl.Rule([
        nl.Fact(nl.Thing('Thing1'), nl.Verb('Dos_verb1', Dos_verb)(to=nl.Thing('Thing2'))),
        ],[
        nl.Fact(nl.Thing('Thing1'), nl.Verb('Dos_verb1', Dos_verb)(to=uno)),
        ])

dos = nl.Thing('dos')
tre = nl.Thing('tre')

class Tre_verb(Uno_verb, Dos_verb): pass

f1 = nl.Fact(dos, Tre_verb(to=tre))

nl.kb.tell(r1, uno, r2, dos, tre, f1)
