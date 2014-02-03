import serial, list_ports, socket

port = ""
HOST = 'jboard.tk'
PORT = 8887

class Application():    
    def __init__(self, port):
        self.serial = None        
        self.running = False
        self.socket = None

    def start(self):
        self.serial = serial.Serial(int(port[3:])-1, baudrate=115200)
        print self.serial.name, "was opened."
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        self.running = True
        self.run()

    def stop(self):
        self.serial.close()
        self.socket.close()
        print "Exited gracefully!"

    def run(self):
        while self.running:
            try:
                data = self.socket.recv(8)
                if data.startswith("H"):
                    self.serial.write(data.strip()[1:]+"\r\n")
            except KeyboardInterrupt:
                self.running = False
        self.stop()

if __name__ == "__main__":
    print ("="*20)+"[ Serial Ports ]"+("="*20)
    list_ports.main()
    print "="*56+"\n"
    port = raw_input("Select a port: ")
    app = Application(port)
    app.start()
    
    
