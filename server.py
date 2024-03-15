from utils import *
import threading as th

class Server:
    def __init__(self):
        # Create server socket and room manager 
        self.serverSocket = UDPComm(True)
        self.rooms = Rooms()
        
        # Start server threads
        try:
            lock = th.Lock()
            sendThread  = th.Thread(target=self.sendMessage, args=[lock])
            rcvThread   = th.Thread(target=self.receiveMessage, args=[lock])

            sendThread.daemon   = True
            rcvThread.daemon    = True

            sendThread.start()
            rcvThread.start()

            sendThread.join()
            rcvThread.join()

        except KeyboardInterrupt:
            self.serverSocket.close()
            print("Server closed.")

    def sendMessage(self, lock):
        # Send messages to clients
        while True:
            lock.acquire() 
            self.serverSocket.checkPacketBuffer()
            [time, address, message] = self.serverSocket.checkACK('server')

            if message:
                self.serverTasks(time, address, message)
            self.serverSocket.checkSendBuffer()
            lock.release() 
    
    def receiveMessage(self, lock):
        # Receive messages from clients
        while True:
            try:
                packet, address, time = self.serverSocket.rdtReceive()

                if packet:
                    dict = eval(packet.decode())
                    message = dict['message']
                    
                    lock.acquire()
                    self.serverSocket.addACK(message, address, time)        # Add message to ACK buffer
                    lock.release()
            
            except KeyboardInterrupt:
                self.serverSocket.close()
                print("Server closed.")
        
    def broadcast(self, message, selfAddress):  
        # Send message to all connected clients except the sender
        print("Broadcasting: " + message)
        connected = self.serverSocket.connections                   # Get all connected clients
        for address in connected:
            if address == selfAddress:                              # Skip sender
                continue
            self.serverSocket.addSendBuffer(message, address)       # Add message to send buffer
    
    def addConnection(self, username, address):
        # Add new connection to server
        msg = ''

        if not self.serverSocket.findAddress(username):             # Check if username is already connected
            msg = username + " esta avaliando reservas!"            # Message to be broadcasted
            self.serverSocket.connect(username, address)            # Add connection to server
          
        return msg
    
    def endConnection(self, address):
        # End connection with client
        username = self.serverSocket.getUsername(address)                   # Get username
        print("Ending connection with " + username)               
        msg = ''
        if username:
            msg = '\n' + username + " saiu do sistema de reservas!"         # Message to be broadcasted     
            self.serverSocket.disconnect(address)                           # Remove connection from server
        
        return msg
    
    def __get_str(self, t): 
        # Get string from time
        if t < 10:
            return '0' + str(t)
        
        return str(t)
    
    def serverTasks(self, time, address, message):
        # Server tasks

        # Bye command 'bye'
        if message == "bye":
            msgToAll = self.endConnection(address)           # Return message to be broadcasted
            self.broadcast(msgToAll, address)                # Broadcast message

        # List command  'list'
        if message == "list":
            connected = self.serverSocket.getConnections()          # Get all connected clients
            msgToClient = "Usuarios conectados: " + ', '.join([connected[addressL]['username'] for addressL in connected]) # Message to be sent
            self.serverSocket.addSendBuffer(msgToClient, address)           # Add message to send buffer, to be sent to the client that requested the list

        # Connect command 'connect as <username>'
        if len(message) >= 12 and message[:11] == "connect as ":    
            username = message[11:]                                     # Get username
            
            if self.serverSocket.findAddress(username):                 # Check if username is already connected, to avoid duplicates
                msgToClient = "The username '" + username + "' is already logged in!"
                self.serverSocket.addSendBuffer(msgToClient, address)           # Add message to send buffer, to be sent to the client that requested the connection

            else:
                msgToAll = self.addConnection(username, address)             # Add connection to server and return message to be broadcasted
                msgToClient = "Hi " + username + " Welcome to the reservation system \n" + \
                        "You can use the following commands: \n" + \
                        "[list] - to list all connected users \n" + \
                        "[reservar] <room> <day> <hour> - to reserve a room \n" + \
                        "[cancelar] <room> <day> <hour> - to cancel a reservation \n" + \
                        "[check] <room> <day> - to check the availability of a room \n" + \
                        "[bye] - to disconnect from the server"
                
                self.serverSocket.addSendBuffer(msgToClient, address)           # Add message to send buffer, to be sent to the client that requested the connection
                self.broadcast(msgToAll, address)                               # Broadcast message

        # Reserve command 'reservar <sala> <dia> <hora>'
        if len(message) >= 10 and message[:8] == "reservar":
            room = message[9:13]                            # Get room
            day = message[14:21]                            # Get day
            hour = int(message[22:])                        # Get hour

            if self.rooms.reserveRoom(day, room, hour-8, self.serverSocket.getUsername(address)):       # If room is available
                msgToAll = self.serverSocket.getUsername(address) + " " + str(address) + " reserved the " + room + " room for " + day + " at " + str(hour) + "h!"
                msgToClient = "You " + str(address) + " have reserved the " + room + " room for " + day + " at " + str(hour) + "h!"
                
                self.serverSocket.addSendBuffer(msgToClient, address)       # Add message to send buffer, to be sent to the client that requested the reservation
                self.broadcast(msgToAll, address)                           # Broadcast message

            else:                                    # If room is not available
                msgToClient = "The " + room + " room is already reserved for " + day + " at " + str(hour) + "h!"    
                self.serverSocket.addSendBuffer(msgToClient, address)            # Add message to send buffer, to be sent to the client that requested the reservation

        # Cancelar
        if len(message) >= 10 and message[:8] == "cancelar":
            room = message[9:13]                            # Get room
            day = message[14:21]                            # Get day
            hour = int(message[22:])                        # Get hour
            
            if self.rooms.cancelReservation(day, room, hour-8, self.serverSocket.getUsername(address)):     # If room has been reserved by the user
                msgToAll = self.serverSocket.getUsername(address) + " canceled the " + room + " room reservation for " + day + " at " + str(hour) + "h!"
                self.broadcast(msgToAll, address)
           
            else:
                msgToClient = "Unable to cancel... The " + room + " room is free or has been reserved by another user for " + day + " at " + str(hour) + "h!"
                self.serverSocket.addSendBuffer(msgToClient, address)

        # Check
        if len(message) >= 7 and message[:5] == "check":
            room = message[6:10]                    # Get room
            day = message[11:]                      # Get day

            hours = self.rooms.checkRoom(day, room)     # Get room availability
            answer = []                                 
            
            for i in range(9):                          
                if hours[i] == 0:
                    answer.append(str(i+8) + "h")       # Add available hours
                else:
                    answer.append(hours[i])             # Add reserved hours
            
            msgToClient = "The " + room + " room - " + day + ": " + ', '.join(answer)
            self.serverSocket.addSendBuffer(msgToClient, address)

if __name__ == "__main__":
    Server()            # Start server