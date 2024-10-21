from socket import *

def startClient(name, port):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    sentence = input("Input lowercase sentence:")
    clientSocket.send(sentence.encode())
    modifiedSentence = clientSocket.recv(1024)
    print('From Server: ', modifiedSentence.decode()) 
    clientSocket.close()

if __name__ == "__main__":
    serverName = 'localhost'
    serverPort = 12000
    startClient(serverName, serverPort)