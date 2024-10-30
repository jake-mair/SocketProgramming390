from socket import *
import sys

# Function to send a file from the client to the server
def sendFile(filename, clientSocket):
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)  # Read the file in 1024-byte chunks
            print([data])
            clientSocket.sendall(data)  # Send the file data to the server
            if not data:  # If no data left, break the loop
                print("entered")
                break
        file.close()

'''I need to send something signifiying the end of the file rn it gets stuck and just waits to receive
also I don't understand how to do that with the chunks of bytes because if I were to signify that it was
the end of file then the entire chunk isn't equal to that'''

'''It's just not finding the end signifier on the server side'''



# Function to receive a file from the server and save it
def recFile(filename, clientSocket):
    # Rename the file if it already exists by appending '_1'
    parts = filename.rsplit('.', 1)  # Split the filename and extension
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"  # Create a new filename to avoid overwriting

    # Open the new file for writing binary data
    with open(new_filename, 'wb') as file:
        while True:
            data = clientSocket.recv(1024)  # Receive data in 1024-byte chunks
            if not data:  # If no more data, break the loop
                break
            file.write(data)  # Write the data to the new file

# Main client function to handle user commands and communicate with the server
def startClient(name, port):
    clientSocket = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
    clientSocket.connect((serverName, serverPort))  # Connect to the server

    while True:
        command = input("Enter command: ").split()  # Get the user's command as a list
        # If the command is 'put', handle file upload
        if command[0] == "put":
            print(command)
            filename = command[1]  # Get the filename from the command
            clientSocket.sendall(b"put")  # Send the 'put' command to the server
            clientSocket.recv(1024)  # Wait for the server to acknowledge

            clientSocket.sendall(filename.encode())  # Send the filename to the server
            clientSocket.recv(1024)  # Wait for the server to acknowledge

            print("Sending file.")
            sendFile(filename, clientSocket)  # Call the sendFile function to upload the file
            print("Awaiting server response.")
            clientSocket.recv(1024)  # Wait for server's confirmation
            print("Server response: File uploaded.")

        # If the command is 'get', handle file download
        # elif command[0] == "get":
        #     filename = command[1]  # Get the filename from the command
        #     clientSocket.sendall(b"get")  # Send the 'get' command to the server
        #     clientSocket.recv(1024)  # Wait for the server to acknowledge

        #     clientSocket.sendall(filename.encode())  # Send the filename to the server
        #     clientSocket.recv(1024)  # Wait for the server to acknowledge

        #     recFile(filename, clientSocket)  # Call the recFile function to download the file
        #     clientSocket.recv(1024)  # Wait for server's confirmation
        #     print(f"File {filename} downloaded.")

        # # If the command is 'keyword', handle file anonymization
        # elif command[0] == "keyword":
        #     keyword = command[1]  # Get the keyword from the command
        #     filename = command[2]  # Get the filename from the command

        #     clientSocket.sendall(b"keyword")  # Send the 'keyword' command to the server
        #     clientSocket.recv(1024)  # Wait for the server to acknowledge

        #     clientSocket.sendall(f"{keyword} {filename}".encode())  # Send the keyword and filename
        #     response = clientSocket.recv(1024)  # Receive the server's response
        #     print(response.decode())  # Print the server's response

        # # If the command is 'quit', handle client exit
        # elif command[0] == "quit":
        #     clientSocket.sendall(b"quit")  # Send the 'quit' command to the server
        #     response = clientSocket.recv(1024).decode()  # Receive and decode the server's response
        #     break  # Exit the loop and close the client

    clientSocket.close()  # Close the socket after quitting

# Entry point for the client program
if __name__ == "__main__":
    serverName = 'localhost'  # Default IP address (localhost)
    serverPort = 12000  # Default port number

    if len(sys.argv) == 3:
        serverName = str(sys.argv[1])
        serverPort = int(sys.argv[2])

    startClient(serverName, serverPort) 
