from socket import *

serverName = "hostname"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input("message:")
clientSocket.sendto(message.encode(), (serverName, serverPort))
modified_message, server_address = clientSocket.recvfrom(2048)

print(modified_message.decode())
clientSocket.close()
