from pyramid_socketio.io import SocketIOContext
from pyramid.view import view_config
from random import random
import gevent


def includeme(config):
    config.scan(__name__)
    config.add_route('socket_io', 'socket.io/*remaining')


class ConnectIOContext(SocketIOContext):
    # self.io is the Socket.IO socket
    # self.request is the request

    def sendcpu(self):
        while self.io.connected():
            ## vals = map(int, [x for x in open('/proc/stat').readlines()
            ##                  if x.startswith('cpu ')][0].split()[1:5])
            ## if prev:
            ##     percent = (100.0 * (sum(vals[:3]) - sum(prev[:3])) / 
            ##                (sum(vals) - sum(prev)))
            percent = random() * 10
            if percent > 5:
                self.msg("showdata", point=percent)
            gevent.sleep(0.5)
    
    def msg_connect(self, msg):
        print "Connect message received", msg
        self.msg("connected", hello="world")
        self.spawn(self.sendcpu)


# Socket.IO implementation
@view_config(route_name="socket_io")
def socketio_service(request):
    ##print "Socket.IO request running"
    resp = ConnectIOContext.socketio_response(request, debug=True)
    return resp
