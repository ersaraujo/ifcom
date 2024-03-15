from utils import *
import threading as th

class Server:
    def __init__(self):
        self.serverSocket = UDPComm(True)
        self.rooms = Rooms()
        
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
        #
        while True:
            lock.acquire()
            self.serverSocket.checkPacketBuffer()
            [time, address, message] = self.serverSocket.checkACK('server')

            if message:
                self.serverTasks(time, address, message)
            self.serverSocket.checkSendBuffer()
            lock.release() 
    
    def receiveMessage(self, lock):
        #
        while True:
            try:
                packet, address, time = self.serverSocket.rdtReceive()

                if packet:
                    dict = eval(packet.decode())
                    message = dict['message']
                    
                    lock.acquire()
                    self.serverSocket.addACK(message, address, time)
                    lock.release()
            
            except KeyboardInterrupt:
                self.serverSocket.close()
                print("Server closed.")
        
    def broadcast(self, message, selfAddress):
        #
        print("Broadcasting: " + message)
        connected = self.serverSocket.connections
        for address in connected:
            if address == selfAddress:
                continue
            print("Sending to: " + connected[address]['username'] + " at " + str(address))
            self.serverSocket.addSendBuffer(message, address)
    
    def addConnection(self, username, address):
        #
        msg = ''

        if not self.serverSocket.findAddress(username):
            msg = username + " esta avaliando reservas!"
            self.serverSocket.connect(username, address)
          
        return msg
    
    def endConnection(self, address):
        #
        username = self.serverSocket.getUsername(address)
        print("Ending connection with " + username)
        msg = ''
        if username:
            msg = '\n' + username + " saiu do sistema de reservas!"
            self.serverSocket.disconnect(address)
        
        return msg
    
    def __get_str(self, t):
        #
        if t < 10:
            return '0' + str(t)
        
        return str(t)
    
    def serverTasks(self, time, address, message):
        # connect, bye, list, reservar, cancelar, check

        _, _, _, h, m, s, _, _, _ = datetime.now().timetuple()
        time = self.__get_str(h) + ':' + self.__get_str(m) + ':' + self.__get_str(s)
        msg = str(time) + " " + self.serverSocket.getUsername(address) + ' - ' + str(message)

        # Connect
        if len(message) >= 12 and message[:11] == "connect as ":
            username = message[11:]
            if self.serverSocket.findAddress(username):
                msg = "Usuario " + username + " ja conectado!"
                self.serverSocket.addSendBuffer(msg, address)
            else:
                msg = self.addConnection(username, address)
                msg1 = "Bem vindo ao sistema de reservas " + username + "!"
                self.serverSocket.addSendBuffer(msg1, address)
                self.broadcast(msg, address)

        # Bye
        if message == "bye":
            msg = self.endConnection(address)
            self.broadcast(msg, address)

        # List
        if message == "list":
            connected = self.serverSocket.getConnections()
            msg = "Usuarios conectados: " + ', '.join([connected[addressL]['username'] for addressL in connected])
            self.serverSocket.addSendBuffer(msg, address)

        # Reservar
        if len(message) >= 10 and message[:8] == "reservar":
            print("Reservando...")
            sala = message[9:13]
            dia = message[14:21]
            hora = int(message[22:])
            if self.rooms.reservarSala(dia, sala, hora-8, self.serverSocket.getUsername(address)):
                msg = self.serverSocket.getUsername(address) + " " + str(address) + " reservou a sala " + sala + " para " + dia + " as " + str(hora) + "h!"
                msg2 = "Voce " + str(address) + " reservou a sala " + sala + " para " + dia + " as " + str(hora) + "h!"
                self.broadcast(msg, address)
                self.serverSocket.addSendBuffer(msg2, address)
            else:
                msg = "A Sala " + sala + " ja reservada para " + dia + " as " + str(hora) + "h!"
                self.serverSocket.addSendBuffer(msg, address)

        # Cancelar
        if len(message) >= 10 and message[:8] == "cancelar":
            sala = message[9:13]
            dia = message[14:21]
            hora = int(message[22:])
            if self.rooms.cancelarReserva(dia, sala, hora-8, self.serverSocket.getUsername(address)):
                msg = self.serverSocket.getUsername(address) + " cancelou a reserva da sala " + sala + " para " + dia + " as " + str(hora) + "h!"
                self.broadcast(msg, address)
            else:
                msg = "Nao foi possivel cancelar... A sala " + sala + " está livre ou foi reservada por outro usuario para " + dia + " as " + str(hora) + "h!"
                self.serverSocket.addSendBuffer(msg, address)

        # Check
        if len(message) >= 7 and message[:5] == "check":
            sala = message[6:10]
            dia = message[11:]
            horarios = self.rooms.checkRoom(dia, sala)
            horariosL = []
            for i in range(9):
                if horarios[i] == 0:
                    horariosL.append(str(i+8) + "h")
                else:
                    horariosL.append(horarios[i])
            msg = "Sala " + sala + " - " + dia + "-feira: " + ', '.join(horariosL)
            self.serverSocket.addSendBuffer(msg, address)

if __name__ == "__main__":
    Server()