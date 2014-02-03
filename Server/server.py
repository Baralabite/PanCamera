import tornado.httpserver
import tornado.websocket
from tornado import ioloop, iostream
import tornado.ioloop
import tornado.web
import functools
import socket
import errno

camera = None
 
def connection_ready(sock, fd, events):
    while True:
        try:
            connection, address = sock.accept()
            print "New socket connection from", address
            camera.set_status(True)
        except socket.error, e:
            if e[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        else:
            connection.setblocking(0)
            CommunicationHandler(connection)
 
class CommunicationHandler():
    def __init__(self, connection):
        self.stream = iostream.IOStream(connection)
        self.stream.set_close_callback(self.on_close)
        camera.set_heading_change_callback(self.on_heading_change_request)
        self.stream.write("H"+str(camera.heading)+"\n")
        self._read()

    def _read(self):
        self.stream.read_until('\r\n', self.handle_data)
        
    def handle_data(self, data):
        print "Recieved: %s" % data
        if not self.stream.closed():
            self._read() 
    
    def on_heading_change_request(self, new_heading):
        if camera.online:
            self.stream.write("H"+str(new_heading)+"\n")

    def on_close(self):
        camera.set_status(False)
        print "Connection closed!"
 
class WSHandler(tornado.websocket.WebSocketHandler):
 #   def __init__(self):
 #       self.connected = False

    def open(self):
        camera.set_connection_callback(self.on_camera_connect)
        camera.set_disconnection_callback(self.on_camera_disconnect)
        print 'New WebSocket Connection!'
        self.connected = True
        self.write_message("H"+str(camera.heading))
        self.write_message("C"+str(int(camera.online)))
      
    def on_message(self, message):
        print 'Data Received: %s' % message
        if message.startswith("H"):
            camera.change_heading(int(message.strip()[1:]))
 
    def on_close(self):
      print 'Connection Closed!'
      self.connected = False

    def on_camera_connect(self):
        if self.connected:
            self.write_message("C1")

    def on_camera_disconnect(self):
        if self.connected:
            self.write_message("C0")
 
class Camera:
    def __init__(self):
        self.online = False
        self.heading = 90
        self.heading_callback = None
        self.connection_callback = None
        self.disconnection_callback = None

    def set_status(self, bool):
        if bool:
            self.online = True
            if not self.connection_callback == None:
                self.connection_callback()
        else:
            self.online = False
            if not self.disconnection_callback == None:
                self.disconnection_callback()

    def set_heading_change_callback(self, callback):
        self.heading_callback = callback

    def set_connection_callback(self, callback):
        self.connection_callback = callback

    def set_disconnection_callback(self, callback):
        self.disconnection_callback = callback

    def change_heading(self, heading):
        self.heading = heading
        if not self.heading_callback == None:
            self.heading_callback(self.heading)
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
]) 
 
if __name__ == "__main__":
    print "Camera Pan Controller Server"
    print "==================================="
    camera = Camera()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind(("", 8887))
    sock.listen(128)
    print "TCP Socket Server listening on port 8887"
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    io_loop = tornado.ioloop.IOLoop.instance()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    print "WebSocket Server listening on port 8888"

    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
        print "Exited Cleanly!"
