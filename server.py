import socket

localAddress    = ("localhost", 20001)
bufferSize      = 1024
fileRec         = "fileRecvFromClient."

# Criando socket UDP
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
print("Server is creating a UDP socket.")

# Vinculando porta do socket ao endereço
UDPServerSocket.bind(localAddress)
print("UDP server up and listening!")

nFile = 1
while(True):

    # Recebendo extensão do arquivo (pdf ou txt)
    data, addressClient = UDPServerSocket.recvfrom(bufferSize)
    extension = str(data.decode())
    print("Extensão recebida do cliente = ", extension)
    
    fileRecvName = str(nFile) + fileRec + extension
    fileRecv = open(fileRecvName, "wb")
    
    print("Enviando a resposta...")
    
    while(data != '\x18'.encode()):
        data, addressClient = UDPServerSocket.recvfrom(bufferSize) # recebendo pacote do cliente
        if(data != '\x18'.encode()):
            fileRecv.write(data) # escrevendo no arquivo
            UDPServerSocket.sendto(data, addressClient) # retornando pacote ao cliente
    
    print("##################################################")
    print("Arquivo recebido e devolvido: " + fileRecvName)
    print("Client IP Address:{}".format(addressClient))
    fileRecv.close()

    nFile += 1
    
    
        

    
    
    

    
