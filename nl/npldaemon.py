
import daemon
import SocketServer
import nl


def main():
    server = SocketServer.TCPServer((nl.conf.host, nl.conf.port),
                                    NlTCPHandler)
    context = daemon.DaemonContext()
    context.files_preserve = [server.fileno()]
    with context:
        server.serve_forever()


class NlTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        data = self.rfile.readline().strip('\n ')
        resp = nl.yacc.parse(data)
        self.wfile.write(resp)
