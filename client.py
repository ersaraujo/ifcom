from utils import *
import threading as th

class Client:
    def __init__(self):
        # Create client socket
        self.clientSocket = UDPComm(False)

        # Start client threads
        try:
            lock = th.Lock()
            sendThread  = th.Thread(target=self.sendMessage, args=[lock])
            rcvThread   = th.Thread(target=self.receiveMessage, args=[lock])
            inputThread = th.Thread(target=self.readMessage, args=[lock])

            sendThread.daemon   = True
            rcvThread.daemon    = True
            inputThread.daemon  = True

            sendThread.start()
            rcvThread.start()
            inputThread.start()

            sendThread.join()
            rcvThread.join()
            inputThread.join()

        
        except KeyboardInterrupt:
            self.clientSocket.close()
            print("Client closed.")
    
    def sendMessage(self, lock):
        # Send messages to server
        leave = False
        while not leave:
            lock.acquire()

            _, _, message = self.clientSocket.checkACK('client')
            leave = message == 'bye'
            
            self.clientSocket.checkSendBuffer()

            lock.release()
        self.clientSocket.close()
    
    def receiveMessage(self, lock):
        # Receive messages from server
        while True:
            try:
                packet, address, time = self.clientSocket.rdtReceive()

                if packet:
                    message = eval(packet.decode())

                    messageReceived = message['message']

                    lock.acquire()
                    self.clientSocket.addACK(messageReceived, address, time)
                    lock.release()

                    print(messageReceived)
            
            except KeyboardInterrupt:
                self.clientSocket.close()
                print("Client closed.")

    def readMessage(self, lock):
        # Read messages from user
        while True:
            try:
                message = input()           # Read message from user
                print("\033[A                             \033[A")      # Clear input line
            
            except EOFError:
                break

            lock.acquire()
            self.clientSocket.addSendBuffer(message, self.clientSocket.serverAddress)
            lock.release()

            if message == 'bye':    
                print("Client closed.")
                return
                

if __name__ == "__main__":
    Client()