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

host = 'localhost'
port = 8280

debug_level = 'INFO'

with_callback = True

start_time = True

here = os.path.join(os.path.dirname(__file__))
# HISTORY_DIR = ''

####################
### CLIPS CONFIG ###
####################

import clips

clips.DebugConfig.ExternalTraceback = True
#clips.EngineConfig.ResetGlobals = True
#clips.EngineConfig.IncrementalReset = True
