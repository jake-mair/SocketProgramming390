from socket import *


def sendFile(filename, clientSocket):
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            clientSocket.sendall(data)


def recFile(filename, clientSocket):
    with open(filename, 'wb') as file:
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            file.write(data)

def startClient(name, port):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))

    # Step 1: Send the file name
    filename = input("Enter the file to anonymize: ")
    clientSocket.sendall(filename.encode()) # Ensures data is sent

    # Step 2: Send the file data
    sendFile(filename, clientSocket)
    print("File sent to server.")

    # Step 3: Send the keyworkd to anonymize
    keyword = input("Enter the keyworkd to anonymize: ")
    clientSocket.sendall(keyword.encode())

    # Step 4: Receive the anonymized file
    anonymized_filename = filename.split('.')[0] + '_anon.txt'
    recFile(anonymized_filename, clientSocket)
    print(f"Anonymized file received: {anonymized_filename}")

    clientSocket.close()

if __name__ == "__main__":
    serverName = 'localhost'
    serverPort = 12000
    startClient(serverName, serverPort)