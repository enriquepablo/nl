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

import daemon
import SocketServer
import nl
from nl.nlc.preprocessor import Preprocessor


def main():
    server = SocketServer.TCPServer((nl.conf.host, nl.conf.port),
                                    NlTCPHandler)
    context = daemon.DaemonContext()
    context.files_preserve = [server.fileno()]
    with context:
        server.serve_forever()


class NlTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        prep = Preprocessor().parse(self.rfile.read())
        preprocessed = prep.strip('\n')
        resp = nl.yacc.parse(preprocessed.strip('\n'))
        if preprocessed.endswith('.'):
            nl.extend()
            nl.now()
        self.wfile.write(resp)
