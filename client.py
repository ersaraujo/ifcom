import socket
import random

def main():

    serverAddress = ("localhost", 20001)
    bufferSize = 1024
    fileRecvName = "fileRecvFromServer."

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    fileToSendName = input("Digite o nome do arquivo a ser enviado: ")

    extension = fileToSendName.split('.')[1]
    UDPClientSocket.sendto(extension.encode(), serverAddress)
    print("Extensão enviada!")

    fileRecvName += extension
    fileToSend = open(fileToSendName, "rb")
    fileRecv = open(fileRecvName, 'wb')

    bytesToSend = fileToSend.read(bufferSize)

    print("Enviando...")
    while bytesToSend:
        # Simulando perda de pacotes aleatórios
        if random.random() < 0.006:
            print("Pacote perdido!")
        else:
            UDPClientSocket.sendto(bytesToSend, serverAddress)

        UDPClientSocket.settimeout(1)
        
        try:
            data, address = UDPClientSocket.recvfrom(bufferSize)
            
            if data == b'ACK':
                bytesToSend = fileToSend.read(bufferSize)
            else:
                print("Recebido reconhecimento inválido, reenviando o pacote...")
                continue

        except socket.timeout:
            print("Timeout! Reenviando o pacote...")
            UDPClientSocket.sendto(bytesToSend, serverAddress)

    UDPClientSocket.sendto('\x18'.encode(), serverAddress)
    print("Arquivo recebido:", fileRecvName)

    fileToSend.close()
    fileRecv.close()
    UDPClientSocket.close()

if __name__ == "__main__":
    main()