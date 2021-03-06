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

from nl import kb, Exists, Thing, Number, Arith, Fact, Rule


time = '100'

# names

class Body(Thing): pass


# verbs

class Has_mass(Exists):
    subject = Thing
    mods = {'kgs': Number}



class Has_position(Exists):
    subject = Thing
    mods = {'x': Number,
            'y': Number}


class Has_speed(Exists):
    subject = Thing
    mods = {'x': Number,
            'y': Number}



class Has_acceleration(Exists):
    subject = Thing
    mods = {'x': Number,
            'y': Number}



class Is_forced(Exists):
    subject = Thing
    mods = {'x': Number,
            'y': Number}



# rules


r1 = Rule([
           Fact(Body('Body1'), Has_position(x='Number1', y='Number2'), 'Time1'),
           Fact(Body('Body1'), Has_speed(x='Number3', y='Number4'), 'Time1'),
           Arith('(< Time1 %s)' % time)
           ], [
           Fact(Body('Body1'), Has_position(x=Number('+', arg1='Number1',
                                                      arg2='Number3'),
                                        y='(+ Number2 Number4)'), '(+ Time1 1)')
           ])


r2 = Rule([
           Fact(Body('Body1'), Has_speed(x='Number1', y='Number2'), 'Time1'),
           Fact(Body('Body1'), Has_acceleration(x='Number3', y='Number4'), 'Time1'),
           Arith('(< Time1 %s)' % time)
           ], [
           Fact(Body('Body1'), Has_speed(x='(+ Number1 Number3)', y='(+ Number2 Number4)'), '(+ Time1 1)')
           ])


r3 = Rule([
           Fact(Body('Body1'), Is_forced(x='Number1', y='Number2'), 'Time1'),
           Fact(Body('Body1'), Has_mass(kgs='Number3'), 'Time1'),
           Arith('(< Time1 %s)' % time)
           ], [
           Fact(Body('Body1'), Has_acceleration(x='(/ Number1 Number3)', y='(/ Number2 Number3)'), '(+ Time1 1)')
           ])

r4 = Rule([
           Fact(Body('Body1'), Has_position(x='Number1', y='Number2'), 'Time1'),
           Fact(Body('Body1'), Has_mass(kgs='Number3'), 'Time1'),
           Fact(Body('Body2'), Has_position(x='Number4', y='Number5'), 'Time1'),
           Fact(Body('Body2'), Has_mass(kgs='Number6'), 'Time1'),
           Arith('(< Time1 %s)' % time),
           Arith('(neq Body1 Body2)')
           ], [
           Fact(Body('Body1'), Is_forced(
              x='(- 0 (/ (* (* Number3 Number6) (- Number1 Number4)) (** (+ (** (- Number1 Number4) 2) (** (- Number2 Number5) 2)) (/ 3 2))))',
              y='(- 0 (/ (* (* Number3 Number6) (- Number2 Number5)) (** (+ (** (- Number1 Number4) 2) (** (- Number2 Number5) 2)) (/ 3 2))))'),
              '(+ Time1 1)')])

r5 = Rule([
           Fact(Body('Body1'), Has_mass(kgs='Number1'), 'Time3'),
           Arith('(< Time3 %s)' % time)
           ],
           [
           Fact(Body('Body1'), Has_mass(kgs='Number1'), '(+ Time3 1)')
           ])



# things

c1 = Body('c1')

c2 = Body('c2')

# propositions

p1 = Fact(c1, Has_mass(kgs=750), 1)

p2 = Fact(c2, Has_mass(kgs=750), 1)

p3 = Fact(c1, Has_position(x=0, y=0), 1)

p4 = Fact(c2, Has_position(x=0, y=100), 1)

p5 = Fact(c1, Has_speed(x=-2, y=0), 1)

p6 = Fact(c2, Has_speed(x=2, y=0), 1)

p7 = Fact(c1, Has_acceleration(x=0, y=0), 1)

p8 = Fact(c2, Has_acceleration(x=0, y=0), 1)

p9 = Fact(c1, Is_forced(x=0, y=0), 1)

p10 = Fact(c2, Is_forced(x=0, y=0), 1)

for p in (c1, c2, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, r1, r2, r3, r4, r5):
    kb.tell(p)

kb.extend()


def plotPh22():
    import Gnuplot
    resp1 = kb.ask_obj(Fact(c1, Has_position(x='X1', y='X2'), 'X3'))
    resp2 = kb.ask_obj(Fact(c2, Has_position(x='X1', y='X2'), 'X3'))

    #resp1 = kb.ask_obj(Fact(c1, Is_forced(newton='X1'), 'X2'))
    #resp2 = kb.ask_obj(Fact(c2, Is_forced(newton='X1'), 'X2'))


    line1 = [(float(p.predicate.x.value), float(p.predicate.y.value)) for p in resp1]
    line2 = [(float(p.predicate.x.value), float(p.predicate.y.value)) for p in resp2]


    gp = Gnuplot.Gnuplot(persist = 1)

    gp('set data style lines')

    plot1 = Gnuplot.PlotItems.Data(line1, with="dots lw 2 lc rgb 'red'",
          title='c1 con %s kgs, desde (%s, %s) a (%s, %s)' % (p1.predicate.kgs.value,
                                                         p3.predicate.x.value,
                                                         p3.predicate.y.value,
                                                         p5.predicate.x.value,
                                                         p5.predicate.y.value))
    plot2 = Gnuplot.PlotItems.Data(line2, with="points pt 6 lw 1 lc rgb 'blue'",
          title='c2 con %s kgs, desde (%s, %s) a (%s, %s)' % (p2.predicate.kgs.value,
                                                         p4.predicate.x.value,
                                                         p4.predicate.y.value,
                                                         p6.predicate.x.value,
                                                         p6.predicate.y.value))

    gp.plot(plot1, plot2)


if __name__ == '__main__':
    plotPh22()
