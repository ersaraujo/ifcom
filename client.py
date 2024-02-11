import socket

serverAddress   = ("localhost", 20001)
bufferSize      = 1024
fileRecvName    = "fileRecvFromServer."

# Criando um socket UDP para o cliente
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
fileToSendName = input("Digite o nome do arquivo a ser enviado: ")


# Enviando a extensão do arquivo (pdf ou txt)
extension = fileToSendName.split('.')[1]
UDPClientSocket.sendto(extension.encode(), serverAddress)
print("Extensão enviada!")

# Abrindo arquivos a ser enviado e o recebido do servidor
fileRecvName += extension
fileToSend = open(fileToSendName, "rb")
fileRecv = open(fileRecvName,'wb')

# Lendo um pacote do arquivo a ser enviado
bytesToSend = fileToSend.read(bufferSize)

print("Enviando...")
while(bytesToSend):
    UDPClientSocket.sendto(bytesToSend, serverAddress) # enviando pacote para o servidor
    bytesToSend = fileToSend.read(bufferSize) # lendo novo pacote
    data, address = UDPClientSocket.recvfrom(bufferSize) # recebendo pacote do servidor
    fileRecv.write(data) # salvando no arquivo

UDPClientSocket.sendto('\x18'.encode(), serverAddress)

print("Arquivo recebido:", fileRecvName)

fileToSend.close()
fileRecv.close()
UDPClientSocket.close()
