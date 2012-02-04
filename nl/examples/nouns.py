# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 by Enrique Pérez Arnaud <enriquepablo@gmail.com>
#
# This file is part of ln.
#
# ln is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ln is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ln.  If not, see <http://www.gnu.org/licenses/>.

from nl import (kb, Noun, Verb, Thing, Exists, Fact, Rule)


class Person(Thing):
    '''
    '''

class Food(Thing):
    '''
    '''

b1 = Food('banana1')
b2 = Food('banana2')
b3 = Food('banana3')
b4 = Food('banana4')
b5 = Food('banana5')
b6 = Food('banana6')

kb.tell(b1, b2, b3, b4, b5, b6)

class Tries(Exists):
    subject = Person
    mods = {'what': Verb}

class Feels(Exists):
    subject = Person
    mods = {'what': Exists}

class Wants(Exists):
    subject = Person
    mods = {'what': Verb}

class Wanting(Exists):
    subject = Person
    mods = {'what': Exists}

class IsCool(Exists):
    subject = Person

class Eats(Exists):
    subject = Person
    mods = {'what': Noun}

class Eating(Exists):
    subject = Person
    mods = {'what': Food}

class Drinking(Exists):
    subject = Person
    mods = {'what': Food}

class Smelling(Exists):
    subject = Person
    mods = {'what': Food}

kb.tell(Rule([
    Fact(Person('Person1'), Wants(what=Verb('EatsVerb1', Eats)))
],[
    Fact(Person('Person1'), Eats(what=Food))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Wants(what=Verb('EatsVerb1', Eats)))
],[
    Fact(Person('Person1'), Tries(what=Verb('EatsVerb1', Eats)))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Wanting(what=Eating(what=b1))),
    Fact(Person('Person1'), Wants(what=Verb('EatsVerb1', Eats)))
],[
    Fact(Person('Person1'), Eating(what=b1))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Wanting(what=Eating(what=b2))),
    Fact(Person('Person1'), Wants(what=Eats))
],[
    Fact(Person('Person1'), Eating(what=b2))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Wanting(what=Verb('EatingVerb1', Eating)(what=Food('Food1')))),
    Fact(Person('Person1'), Verb('EatingVerb1', Eating)('Eating1'))
],[
    Fact(Person('Person1'), Feels(what=Verb('EatingVerb1', Eating)(what=Food('Food1')))),
]))

kb.tell(Rule([
    Fact(Person('Person1'), Eating(what=b2)),
    Fact(Person('Person1'), Wants(what=Verb('EatsVerb1', Eats)))
],[
    Fact(Person('Person1'), Eating(what=b3))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Wants(what=Verb('EatsVerb1', Eats))),
    Fact(Person('Person1'), Eating(what=b3)),
],[
    Fact(Person('Person1'), Drinking(what=b4))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Drinking(what=Noun('FoodNoun1', Food)('Food1'))),
    Fact(Person('Person1'), Eats(what=Noun('FoodNoun1', Food)))
],[
    Fact(Person('Person1'), Eating(what=Noun('FoodNoun1', Food)('Food1')))
]))

kb.tell(Rule([
    Fact(Person('Person1'), Eats(what=Noun('FoodNoun1', Food))),
    Fact(Person('Person1'), Eating(what=Noun('FoodNoun1', Food)('Food1'))),
],[
    Fact(Person('Person1'), Smelling(what=Noun('FoodNoun1', Food)('Food1')))
]))
