import socket
from datetime import datetime

SERVER_ADDRESS = ('0.0.0.0', 19900)
BUFFER_SIZE = 1024

class UDPComm:
    def __init__(self, server):
        self.UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.server = server
        self.serverAddress = SERVER_ADDRESS

        self.ackBuffer = []
        self.sendBuffer = []
        self.connections = {}
        self.packetBuffer = {}
        self.deleteBuffer = []
        self.bye = False

        if server:
            self.UDPSocket.bind(SERVER_ADDRESS)
            print("UDP server up and listing...")

    def __receive(self):
        package, address = self.UDPSocket.recvfrom(BUFFER_SIZE)

        if not self.server and address not in self.connections:
            self.serverAddress = address
            self.connect("server", address)

        return package, address
    
    def __send(self, package, address):
        self.UDPSocket.sendto(package, address)
        
    def makePackage(self, data, time):
        #
        return str({
            'message': data,
            'time': time}).encode()

    def __rdtSend(self, data, time, address):
        #
        if data == "ACK":
            package = self.makePackage(data, time)
            self.__send(package, address)

        else:
            now = str(datetime.now())
            package = self.makePackage(data, now)
            self.packetBuffer[now] = {
                'package': package,
                'address': address
            }

            self.__send(package, address)
            
            if data == "bye":
                self.bye = True
    
    def rdtReceive(self):
        #
        package, address = self.__receive()
        message = eval(package.decode())
        time = message['time']

        if not self.__isACK(message):
            return package, address, time
        
        if self.__isACK(message):
            self.deleteBuffer.append(time)
        
        return '', address, time
    
    def __isACK(self, message):
        #
        return (message['message'] == 'ACK')
    
    def addACK(self, message, address, time):
        #
        self.ackBuffer.append(("ACK", time, address, message))

    def addSendBuffer(self, message, address):
        #
        self.sendBuffer.append((message, address))

    def checkACK(self, type):
        #
        if len(self.ackBuffer):
            [msg, time, address, msgReceived] = self.ackBuffer[0]
            self.ackBuffer.pop(0)
            
            if address:
                self.__rdtSend(msg, time, address)

            if type == "client" and self.bye == True:
                return time, address, 'bye'
            
            if type == "server" and msgReceived:
                return time, address, msgReceived
            
        return '', ('', 0), ''
        
    def checkSendBuffer(self):
        #
        if len(self.sendBuffer):
            msg, addressTo = self.sendBuffer[0]
            self.sendBuffer.pop(0)
            self.__rdtSend(msg, 0, addressTo)

    def checkPacketBuffer(self):
        #
        for time in self.deleteBuffer:
            if time in self.packetBuffer:
                del self.packetBuffer[time]
        
        self.deleteBuffer = []
        toResend = []
        
        for time in self.packetBuffer:
            now = datetime.now()
            t   = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
            t   = (now - t).seconds

            if t > 0:
                toResend.append(time)

        for time in toResend:
            package = self.packetBuffer[time]['package']
            address = self.packetBuffer[time]['address']

            del self.packetBuffer[time]

            message = eval(package.decode())
            self.__rdtSend(message['message'], 0, address)
    
    def connect(self, username, address):
        #
        self.connections[address] = {
            'username': username
        }

    def disconnect(self, address):
        #
        if address in self.connections.keys():
            
            del self.connections[address]
    
    def getUsername(self, address):
        #
        if address in self.connections.keys():
            return self.connections[address]['username']
        
        return ''
    
    def getConnections(self):
        #
        print(self.connections)
        return self.connections
    
    def findAddress(self, username):
        #
        for address in self.connections.keys():
            if self.connections[address]['username'] == username:
                return address
        
        return ''
    
    def close(self):
        self.UDPSocket.close() 

class Rooms:
    def __init__(self):
        
        self.rooms = {
            'segunda': {
                'E101': [0] * 9,
                'E102': [0] * 9,
                'E103': [0] * 9,
                'E104': [0] * 9,
                'E105': [0] * 9
            },
            'terça': {
                'E101': [0] * 9,
                'E102': [0] * 9,
                'E103': [0] * 9,
                'E104': [0] * 9,
                'E105': [0] * 9
            },
            'quarta': {
                'E101': [0] * 9,
                'E102': [0] * 9,
                'E103': [0] * 9,
                'E104': [0] * 9,
                'E105': [0] * 9
            },
            'quinta': {
                'E101': [0] * 9,
                'E102': [0] * 9,
                'E103': [0] * 9,
                'E104': [0] * 9,
                'E105': [0] * 9
            },
            'sexta': {
                'E101': [0] * 9,
                'E102': [0] * 9,
                'E103': [0] * 9,
                'E104': [0] * 9,
                'E105': [0] * 9
            }
        }


    def getRooms(self):
        #
        return self.rooms
    
    def getRoomsList(self):
        #
        return self.roomsList
    
    def reservarSala(self, dia, sala, horario, username):
        #
        if self.rooms[dia][sala][horario] == 0:
            self.rooms[dia][sala][horario] = username
            return True
        
    def cancelarReserva(self, dia, sala, horario, username):
        #
        if self.rooms[dia][sala][horario] == username:
            self.rooms[dia][sala][horario] = 0
            return True
        return False
    
    def checkRoom(self, dia, sala):
        #
        return self.rooms[dia][sala]
    