import socket
from datetime import datetime

SERVER_ADDRESS = ('0.0.0.0', 19900)
BUFFER_SIZE = 1024

class UDPComm:
    # Class to handle UDP communication
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

        if server:              # If server, bind to server address
            self.UDPSocket.bind(SERVER_ADDRESS)
            print("UDP server up and listing...")

    def __receive(self):        
        # Method to receive data from socket
        package, address = self.UDPSocket.recvfrom(BUFFER_SIZE)

        if not self.server and address not in self.connections:     # If client and not yet connected, connect to server
            self.serverAddress = address
            self.connect("server", address)

        return package, address    # Return package and address received
    
    def __send(self, package, address): 
        # Method to send data to socket
        self.UDPSocket.sendto(package, address)
        
    def makePackage(self, data, time):
        # Method to make package to send
        return str({
            'message': data,
            'time': time}).encode()

    def __rdtSend(self, data, time, address):   
        # Method to send data using RDT
        if data == "ACK":
            package = self.makePackage(data, time)
            self.__send(package, address)

        else:
            now = str(datetime.now())               # Get current time
            package = self.makePackage(data, now)   # Make package with data and time
            self.packetBuffer[now] = {              # Add package to packet buffer with time as key
                'package': package,
                'address': address
            }

            self.__send(package, address) 
            
            if data == "bye":
                self.bye = True
    
    def rdtReceive(self):
        # Method to receive data using RDT
        package, address = self.__receive()         
        message = eval(package.decode())
        time = message['time']

        if not self.__isACK(message):               # If not ACK, return package, address and time
            return package, address, time
        
        if self.__isACK(message):                   # If ACK, add package to delete buffer
            self.deleteBuffer.append(time)
        
        return '', address, time
    
    def __isACK(self, message):
        # Method to check if message is ACK
        return (message['message'] == 'ACK')
    
    def addACK(self, message, address, time):
        # Method to add message to ACK buffer
        self.ackBuffer.append(("ACK", time, address, message))

    def addSendBuffer(self, message, address):
        # Method to add message to send buffer
        self.sendBuffer.append((message, address))

    def checkACK(self, type):
        # Method to check ACK buffer
        if len(self.ackBuffer):                     # If ACK buffer is not empty
            [msg, time, address, msgReceived] = self.ackBuffer[0]    # Get first message in buffer
            self.ackBuffer.pop(0)                                    # Remove message from buffer
            
            if address:
                self.__rdtSend(msg, time, address)                  # Send ACK to address received

            if type == "client" and self.bye == True:               # If client and bye message received
                return time, address, 'bye'
            
            if type == "server" and msgReceived:                    # If server and message received
                return time, address, msgReceived
            
        return '', ('', 0), ''
        
    def checkSendBuffer(self):
        # Method to check send buffer
        if len(self.sendBuffer):                    # If send buffer is not empty
            msg, addressTo = self.sendBuffer[0]     # Get first message in buffer
            self.sendBuffer.pop(0)                  # Remove message from buffer
            self.__rdtSend(msg, 0, addressTo)       # Send message to address received

    def checkPacketBuffer(self):
        # Method to check packet buffer
        for time in self.deleteBuffer:          # For each time in delete buffer
            if time in self.packetBuffer:       # If time is in packet buffer can be deleted
                del self.packetBuffer[time]     
        
        self.deleteBuffer = []                  # Clear delete buffer
        toResend = []                           # List to store times to resend
        
        for time in self.packetBuffer:          # For each time in packet buffer
            now = datetime.now()                # Get current time
            t   = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
            t   = (now - t).seconds

            if t > 0:                           # If time is greater than 0, resend package
                toResend.append(time)           # Add time to resend list

        for time in toResend:                   # For each time to resend
            package = self.packetBuffer[time]['package']
            address = self.packetBuffer[time]['address']

            del self.packetBuffer[time]         # Delete package from packet buffer

            message = eval(package.decode())
            self.__rdtSend(message['message'], 0, address)      # Resend package
    
    def connect(self, username, address):
        # Method to connect to server
        self.connections[address] = {
            'username': username
        }

    def disconnect(self, address):
        # Method to disconnect from server
        if address in self.connections.keys():
            del self.connections[address]
    
    def getUsername(self, address):
        # Method to get username from address
        if address in self.connections.keys():
            return self.connections[address]['username']
        
        return ''
    
    def getConnections(self):
        # Method to get all connections
        print(self.connections)
        return self.connections
    
    def findAddress(self, username):
        # Method to find address from username
        for address in self.connections.keys():
            if self.connections[address]['username'] == username:
                return address
        
        return ''
    
    def close(self):
        # Method to close socket
        self.UDPSocket.close() 

class Rooms:
    # Class to handle rooms
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
    
    def reserveRoom(self, day, room, hour, username):
        # reserve room if available
        if self.rooms[day][room][hour] == 0:
            self.rooms[day][room][hour] = username
            return True
        return False
        
    def cancelReservation(self, day, room, hour, username):
        # cancel reservation if user is the owner
        if self.rooms[day][room][hour] == username:
            self.rooms[day][room][hour] = 0
            return True
        return False
    
    def checkRoom(self, day, room):
        # check room availability
        return self.rooms[day][room]
    