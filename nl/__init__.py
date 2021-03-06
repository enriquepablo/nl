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

import clips

import kb
from metanl import Number, Arith, Noun, Word, Verb, Subword, Namable, Not, And, Or, Distinct
from thing import Thing
from state import Exists
from prop import Fact
from nltime import (Time, Instant, Duration, Finish, During,
                    Coincide, Max_end, Min_end,
                    Intersection, now)
from rule import Rule
from utils import change_now

from log import logger
import utils
import nltime
import log
from nlc.compiler import yacc, CompileError
