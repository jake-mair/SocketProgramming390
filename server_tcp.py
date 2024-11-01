from socket import *
import sys
import os

# Function to handle the 'put' task, which uploads a file from the client to the server
def putTask(conn):
    # Receive the filename from the client
    filename = conn.recv(1024).decode()
    conn.sendall(b"Filename received.")  # Acknowledge filename receipt

    file_size = int(conn.recv(1024).decode())
    conn.sendall(b"File size received.")

    # Part to rename the file if it already exists by appending '_1' to the filename
    parts = filename.rsplit('.', 1)  # Split the filename to separate name and extension
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"  # Add '_1' to the filename to avoid overwriting

    bytes_received = 0 
    # Open the new file in write-binary mode and start writing data received from the client
    with open(new_filename, 'wb') as file:
        while bytes_received < file_size:
            data = conn.recv(1024)  # Receive data in chunks of 1024 bytes
            if not data:  # If no more data is received, stop the loop
                break
            file.write(data)  # Write the received data to the new file
            bytes_received += len(data)
    # Inform the client that the file has been successfully uploaded
    conn.sendall(b"Server response: File uploaded.")
    
    return new_filename


# Function to handle the 'get' task, which sends a file from the server to the client
def getTask(conn):
    # Receive the filename from the client
    filename = conn.recv(1024).decode()
    conn.sendall(b"Filename received.")  # Acknowledge filename receipt

    file_size = os.path.getsize(filename)
    print(file_size)
    conn.sendall(str(file_size).encode())
    print("Before")
    response = conn.recv(1024).decode() # Wait for the client to acknowledge file size
    print(response)
    print("After")


    # Open the requested file in read-binary mode and start sending the data to the client
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)  # Read file data in chunks of 1024 bytes
            if not data:  # If the end of the file is reached, stop the loop
                break
            conn.sendall(data)  # Send the file data to the client


# Function to handle the 'keyword' task, which anonymizes a file based on a given keyword
def keywordTask(conn):
    conn.sendall(b"Keyword command received.")  # Acknowledge that the command was received

    # Receive the keyword and filename from the client
    key_and_file = conn.recv(1024).decode().split()  # Split the keyword and filename
    keyword, filename = key_and_file[0], key_and_file[1]
    
    # Split the filename into name and extension to create a new anonymized filename
    parts = filename.rsplit('.', 1)
    name = parts[0]
    ext = parts[1]
    anonymized_filename = f"{name}_anon.{ext}"  # Create a new filename for the anonymized file

    # Read the content of the original file
    with open(filename, 'r') as file:
        content = file.read()

    # Replace occurrences of the keyword with X's in the file content
    anonymized_content = content.replace(keyword, 'X' * len(keyword))

    # Write the anonymized content to a new file
    with open(anonymized_filename, 'w') as anon_file:
        anon_file.write(anonymized_content)

    # Inform the client that the file has been anonymized and provide the new filename
    conn.sendall(f"Server response: File {filename} anonymized. Output file is {anonymized_filename}".encode())

# Function to start the server and listen for incoming client connections and commands
def startServer(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)  # Create a TCP/IP socket
    serverSocket.bind(('', port))  # Bind the socket to the specified port
    serverSocket.listen(1)  # Listen for incoming connections (1 connection at a time)
    print(f'The server is ready to receive on port {port}')

    connectionSocket, addr = serverSocket.accept()  # Accept a connection from a client
    print(f"Connection established with {addr}")  # Log the client's address
    # Main server loop: Accept and process client connections
    while True:

        # Receive the command from the client
        command = connectionSocket.recv(1024).decode()
        if command != "quit":
            connectionSocket.sendall(b"File received.")  # Acknowledge that the command was received

        # Check the command and call the appropriate task function
        if command == "put":
            putTask(connectionSocket)  # Handle file upload
        elif command == "get":
            getTask(connectionSocket)  # Handle file download
        elif command == "keyword":
            keywordTask(connectionSocket)  # Handle file anonymization
        elif command == "quit":
            connectionSocket.sendall(b"Server response: Goodbye!")  # Send a goodbye message
            break  # Exit the server loop

    # Close the connection after handling the command
    connectionSocket.close()

# Main block to start the server with a specified port
if __name__ == "__main__":
    port = 12000  # Default port for the program

    # If a port number is provided as a command-line argument, use that port
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    startServer(port)
