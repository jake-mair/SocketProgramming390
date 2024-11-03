from socket import *

serverName = "localhost"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

file = open('test_files/File1.txt', "r")
long_message = file.read()
clientSocket.sendto(("LEN:" + str(len(long_message.encode()))).encode(), (serverName, serverPort))
message = "Hello, UDP!"
clientSocket.sendto(message.encode(), (serverName, serverPort))
modified_message, server_address = clientSocket.recvfrom(2048)

print(modified_message.decode())
clientSocket.close()