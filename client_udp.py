from socket import *
import os
import multiprocessing.queues as mpq
from multiprocessing import Process, Queue
import sys


#### CODE FOR RECEIVING FILE

# Timeout source: https://flipdazed.github.io/blog/quant%20dev/parallel-functions-with-timeouts
# Function that receives data and sends an ACK
def ack_and_wait_for_data(q: Queue, client_socket):
    message, server_address = client_socket.recvfrom(1048)
    client_socket.sendto("ACK".encode(), server_address)
    q.put(message)

# Function that receives data by calling ack_and_wait_for_data() with a one second timeout.
#   Calls ack_and_wait_for_data which receives data and sends an ACK.
#   If ack_and_wait_for_data returns data, this function returns the data as well, 
#   otherwise if the ack_and_wait_for_data times out, it returns "terminate".
def receive_data(client_socket):
    q_worker = Queue()
    p = Process(target=ack_and_wait_for_data, args=(q_worker, client_socket, ))
    p.start()

    try:
        res = q_worker.get(timeout = 1)
        return res
    except mpq.Empty:
        p.terminate()
        return "terminate"

# Function to receive a file using stop and wait protocol.
def receive_file(file_name, client_socket, server_address):
    # Rename the file if it already exists by appending '_1' to the file_name
    parts = file_name.rsplit('.', 1)  # Split the file_name to separate name and extension
    name = parts[0]
    ext = parts[1]
    new_file_name = f"{name}_1.{ext}"  # Add '_1' to the file_name to avoid overwriting

    # Receive and acknowledge a message containing the file size of of the file to be 
    #   received in the format "LEN:Bytes". If no message is received, prints 
    #   "Did not receive file size. Terminating", and terminates.
    message = receive_data(client_socket)
    if (message == "terminate"):
        print("Did not receive file size. Terminating")
        return "terminate"
    else:
        file_size = int(message.decode().upper()[4:])

    # Opens the new file for writing binary data
    with open(new_file_name, 'wb') as file:

        # receives the first chunk of data. If no data is received, 
        #   prints "Did not receive data. Terminating." and terminates.
        bytes_received = 0 
        message = receive_data(client_socket)
        if (message == "terminate"):
            print("Did not receive data. Terminating.")
            return "terminate"
        else:
            file.write(message)
            bytes_received += len(message)

        # Receives the remaining data in chunks until it has received 
        #   as many bytes as the file_size. If no data is received, 
        #   prints "Data transmission terminated prematurely." and terminates.
        while bytes_received < file_size:
            message = receive_data(client_socket)
            if (message == "terminate"):
                print("Data transmission terminated prematurely.")
                return "terminate"
            else:
                file.write(message)
                bytes_received += len(message)
        
        # Sends "FIN" to the server to tell the server that the process is complete.
        send_message("FIN".encode(), server_address, client_socket)
    return new_file_name


#### CODE FOR SENDING FILE
# Source for timeout function: https://alexandra-zaharia.github.io/posts/function-timeout-in-python-multiprocessing/
# Sends a message and waits for a message containing the string "ACK"
def send_message_and_wait_for_ack(message, server_address, client_socket):

    # Sends the message to the server
    client_socket.sendto(message, server_address)

    # Waits for a message containing the string "ACK"
    while True: 
        ack, server_address = client_socket.recvfrom(1048)
        if ("ACK" in ack.decode().upper()):
            break

# Sends a message to a server and waits for an ack with a one second timeout.
#   Calls the function send_message_and_wait_for_ack and if it receives an ACK 
#   before the timeout, returns "success", otherwise returns "terminate".
def send_message(message, server_address, client_socket):
    p = Process(target=send_message_and_wait_for_ack, args=(message, server_address, client_socket,))
    p.start()
    p.join(1)

    if p.is_alive():
        p.terminate()
        p.join()
        return "terminate"
    return "success"

# Sends a file to the server using stop and wait protocol.
def send_file(file_name, server_address, client_socket):

    # Sends a message with the length of the data in the format LEN:Bytes, 
    #   if it doesn't receive an ACK, terminates
    file_size = os.path.getsize(file_name)
    if (send_message(("LEN:" + str(file_size)).encode(), server_address, client_socket) == "terminate"):
        print("Did not acknowledge file size. Terminating")
        return "terminate"

    # Opens the file and sends it in 1000-byte chunks. 
    #   If it doesn't receive an ACK after sending a chunk, terminates.
    with open(file_name, 'rb') as file:
        while True:
            data = file.read(1000)  # Read the file in 1000-byte chunks
            if not data:  # If no data left, break the loop
                break
            if (send_message(data, server_address, client_socket) == "terminate"): # Send the file data to the server in a small chunk
                print("Did not receive ACK. Terminating.")
                return "terminate"


# Main client function to handle user commands and communicate with the server
def startClient(server_address):

    client_socket = socket(AF_INET, SOCK_DGRAM) # Creates the client socket

    while True:
        command = input("Enter command: ")  # Get the user's command as a list

        # If the command is 'quit', handle client exit
        if command.split()[0] == "quit":
            send_message(command.encode(), server_address, client_socket)
            print("Exiting program!")
            break  # Exit the loop and close the client

        # Tell the server what the command was
        if (send_message(command.encode(), server_address, client_socket) == "terminate"):
            print("Did not receive ACK. Terminating.")
        else:
            print("Awaiting server response.")

            # If the command is 'put', handle file upload
            if command.split()[0] == "put":
                file_name = command.split()[1]  # Get the file_name from the command
                if (send_file(file_name, server_address, client_socket) != "terminate"): # Send the file to the server

                    # Receive a message containing "FIN" to signal that the process is complete
                    #   Then receive and print the server response.
                    fin = receive_data(client_socket)
                    response = receive_data(client_socket)
                    if (fin, response != "terminate"):
                        if ("FIN" in fin.decode().upper()):
                            print(f"Server response: {response.decode()}")
                        else:
                            print("Did not receive FIN message. Terminating.")
                    else:
                        print("Did not receive server response. Terminating.")

            # If the command is 'get', handle file download
            elif command.split()[0] == "get":
                # Call the receive_file function to download the file and get the new file name
                new_file_name = receive_file(command.split()[1], client_socket, (server_address))

                # Tell the server that the file is downloaded and what the new file name is.
                if (new_file_name != "terminate"):
                    send_message(f"File {command.split()[1]} downloaded. Output file is {new_file_name}".encode(), server_address, client_socket)
                    print(f"File {command.split()[1]} downloaded. Output file is {new_file_name}")

            # If the command is 'keyword', handle file anonymization
            elif command.split()[0] == "keyword":
                # Receives and prints the response from the server containing the new file name
                print(f"Server response: {receive_data(client_socket).decode()}")

    client_socket.close()  # Close the socket after quitting


if __name__ == '__main__':
    # Source for how to pass arguments to a file: https://www.pythonforbeginners.com/system/python-sys-argv
    server_name=str(sys.argv[1])
    server_port=int(sys.argv[2])
    startClient((server_name, server_port))