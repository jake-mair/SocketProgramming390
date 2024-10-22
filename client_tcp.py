from socket import *
import sys

def sendFile(filename, clientSocket):
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            clientSocket.sendall(data)



def recFile(filename, clientSocket):

    # Part to rename the file if it already exists
    parts = filename.rsplit('.', 1)
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"



    with open(new_filename, 'wb') as file:
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            file.write(data)

def startClient(name, port):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))

    while True:
        command = input("Enter command: ").split()
        filename = command[1]

        if command[0] == "put":

            clientSocket.sendall(b"put")
            clientSocket.recv(1024)
            clientSocket.sendall(filename.encode())
            clientSocket.recv(1024)

            print("Sending file.")
            sendFile(filename, clientSocket)
            print("Awaiting server response.")
            clientSocket.recv(1024)
            print("Server response: File uploaded.")

        elif command[0] == "get":
            clientSocket.sendall(b"get")
            clientSocket.recv(1024)
            clientSocket.sendall(filename.encode())
            clientSocket.recv(1024)
            recFile(filename, clientSocket)
            clientSocket.recv(1024)
            print(f"File {filename} downloaded.")
        
        elif command[0] == "keyword":
            keyword = command[1]
            filename = command[2]

            clientSocket.sendall(b"keyword")
            clientSocket.recv(1024)

            clientSocket.sendall(f"{keyword} {filename}".encode())
            response = clientSocket.recv(1024)
            print(response.decode())
        
    clientSocket.close()

if __name__ == "__main__":
    serverName = 'localhost' # Default ip
    serverPort = 12000 # Default port

    if len(sys.argv) == 3:
        serverName = str(sys.argv[1])
        serverPort = int(sys.argv[2])
        
    startClient(serverName, serverPort)