# Authors: Jake Mair, Sydney Eriksson, Brian Tran, Bryce Molnar

from socket import *
import sys
import os

# Handle 'put' task, uploads a file from client to server
def putTask(conn):
    # Receive filename from client
    filename = conn.recv(1024).decode()
    conn.sendall(b"Filename received.")  # ACK

    file_size = int(conn.recv(1024).decode())
    conn.sendall(b"File size received.")

    # Rename file if it already exists by appending '_1' to filename
    parts = filename.rsplit('.', 1)  
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}" 

    bytes_received = 0 
    # Open new file in write-binary mode and start writing data received from client
    with open(new_filename, 'wb') as file:
        while bytes_received < file_size:
            data = conn.recv(1024)  # Receive data in chunks of 1024 bytes
            if not data:  # If no more data is received, stop loop
                break
            file.write(data)  # Write received data to new file
            bytes_received += len(data)

    # Inform client that file has been successfully uploaded
    conn.sendall(b"Server response: File uploaded.")
    
    return new_filename


# Handle 'get' task, sends a file from server to client
def getTask(conn):
    # Receive filename from client
    filename = conn.recv(1024).decode()

    if os.path.isfile(filename):
        file_size = os.path.getsize(filename)
        conn.sendall(f"{file_size}".encode())  # Send file size
        conn.recv(1024).decode()

    # Open requested file in read-binary mode and start sending data to client
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)  
            if not data: 
                break
            conn.sendall(data)  # Send file data to client
    
    conn.recv(1024).decode()


# Handle 'keyword' task, which anonymizes a file based on a given keyword
def keywordTask(conn):
    conn.sendall(b"Keyword command received.")  # ACK

   
    key_and_file = conn.recv(1024).decode().split() 
    keyword, filename = key_and_file[0], key_and_file[1]
    
    # Split filename into name and extension to create a new anonymized filename
    parts = filename.rsplit('.', 1)
    name = parts[0]
    ext = parts[1]
    anonymized_filename = f"{name}_anon.{ext}" 

    # Read content of original file
    with open(filename, 'r') as file:
        content = file.read()

    # Replace occurrences of keyword with X's in file content
    anonymized_content = content.replace(keyword, 'X' * len(keyword))

    # Write anonymized content to a new file
    with open(anonymized_filename, 'w') as anon_file:
        anon_file.write(anonymized_content)

    # Inform client that file has been anonymized and provide new filename
    conn.sendall(f"Server response: File {filename} anonymized. Output file is {anonymized_filename}".encode())

# Start server and listen for incoming client connections and commands
def startServer(port):
    serverSocket = socket(AF_INET, SOCK_STREAM) 
    serverSocket.bind(('', port)) 
    serverSocket.listen(1)
    print(f'The server is ready to receive on port {port}')

    connectionSocket, addr = serverSocket.accept()  # Accept a connection from a client
    print(f"Connection established with {addr}")  
   
    while True:

        # Receive command from client
        command = connectionSocket.recv(1024).decode()
        if command != "quit":
            connectionSocket.sendall(b"File received.")  # Acknowledge that command was received

        if command == "put":
            putTask(connectionSocket)  # Handle file upload
        elif command == "get":
            getTask(connectionSocket)  # Handle file download
        elif command == "keyword":
            keywordTask(connectionSocket)  # Handle file anonymization
        elif command == "quit":
            connectionSocket.sendall(b"Server response: Goodbye!")  # Send a goodbye message
            break 

    # Close connection after handling command
    connectionSocket.close()

if __name__ == "__main__":
    port = 12000  # Default port for program

    # If a port number is provided as a command-line argument, use that port
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    startServer(port)
