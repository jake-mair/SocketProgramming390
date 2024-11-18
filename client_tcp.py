# Authors: Jake Mair, Sydney Eriksson, Brian Tran, Bryce Molnar


from socket import *
import sys
import os

# Send a file from client to server
def sendFile(filename, clientSocket):
    file_size = os.path.getsize(filename)
    clientSocket.sendall(f"{file_size}".encode())
    clientSocket.recv(1024)


    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)  # Read file in 1024-byte chunks
            if not data:  # If no data left, break loop
                break
            clientSocket.sendall(data)  # Send file data to server


# Receive a file from server and save it
def recFile(filename, clientSocket):

    clientSocket.sendall(filename.encode())
    response = clientSocket.recv(1024).decode() 
    file_size = int(response)
    clientSocket.sendall(b"File size received")

    # Rename file if it already exists by appending '_1'
    parts = filename.rsplit('.', 1) 
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}" 

    bytes_received = 0 
    # Open new file for writing binary data
    with open(new_filename, 'wb') as file:
        while bytes_received < file_size:
            data = clientSocket.recv(1024) 
            if not data: 
                break
            file.write(data)  
            bytes_received += len(data)
            
    # Inform server that file has been successfully downloaded
    clientSocket.sendall(b"Client response: File downloaded.")
    return new_filename

# Handle user commands and communicate with server
def startClient(name, port):
    clientSocket = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
    clientSocket.connect((serverName, serverPort))  # Connect to server

    while True:
        command = input("Enter command: ").split()  # Get user's command as a list

        if command[0] == "put":

            filename = command[1]

            clientSocket.sendall(b"put")  # Send 'put' command to server
            clientSocket.recv(1024)

            clientSocket.sendall(filename.encode())  # Send filename to server
            clientSocket.recv(1024)  

            sendFile(filename, clientSocket)  # Call sendFile function to upload file
            print("Awaiting server response.")
            clientSocket.recv(1024)  # Wait for server's confirmation
            print("Server response: File uploaded.")

        elif command[0] == "get":

            filename = command[1]  

            clientSocket.sendall(b"get")  # Send 'get' command to server
            clientSocket.recv(1024)  # Wait for ACK

            recFile(filename, clientSocket)  # Call recFile function to download file
            print(f"File {filename} downloaded.")

        elif command[0] == "keyword":
            keyword = command[1]  
            filename = command[2] 

            clientSocket.sendall(b"keyword")  # Send 'keyword' command to server
            clientSocket.recv(1024)  # Wait for ACK

            clientSocket.sendall(f"{keyword} {filename}".encode())  # Send keyword and filename
            response = clientSocket.recv(1024) 
            print(response.decode()) 

        elif command[0] == "quit":
            clientSocket.sendall(b"quit")  # Send 'quit' command to server
            print("Exiting program!")
            break 

    clientSocket.close()  # Close socket after quitting


if __name__ == "__main__":
    serverName = 'localhost'  # Default IP address (localhost)
    serverPort = 12000  # Default port number

    if len(sys.argv) == 3:
        serverName = str(sys.argv[1])
        serverPort = int(sys.argv[2])

    startClient(serverName, serverPort) 
