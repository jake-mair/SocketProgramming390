import sys
from socket import *
import multiprocessing.queues as mpq
from multiprocessing import Process, Queue
import os

#### CODE FOR RECEIVING FILE

# Timeout source: https://flipdazed.github.io/blog/quant%20dev/parallel-functions-with-timeouts
# Function that receives data and sends an ACK
def ack_and_wait_for_data(q: Queue, server_socket):
    message, client_address = server_socket.recvfrom(1048)
    server_socket.sendto("ACK".encode(), client_address)
    q.put(message)

# Function that receives data by calling ack_and_wait_for_data() with a one second timeout.
#   Calls ack_and_wait_for_data which receives data and sends an ACK.
#   If ack_and_wait_for_data returns data, this function returns the data as well, 
#   otherwise if the ack_and_wait_for_data times out, it returns "terminate".
def receive_data(server_socket):
    q_worker = Queue()
    p = Process(target=ack_and_wait_for_data, args=(q_worker, server_socket, ))
    p.start()

    try:
        res = q_worker.get(timeout=1)
        return res
    except mpq.Empty:
        p.terminate()
        return "terminate"

# Function to receive a file using stop and wait protocol.
def receive_file(SERVER_PORT, server_socket, client_address, file_name):
    # Part to rename the file if it already exists by appending '_1' to the filename
    parts = file_name.rsplit('.', 1)  # Split the filename to separate name and extension
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"  # Add '_1' to the filename to avoid overwriting

    # Receive and acknowledge a message containing the file size of of the file to be 
    #   received in the format "LEN:Bytes". If no message is received, prints 
    #   "Did not receive file size. Terminating", and terminates.
    message = receive_data(server_socket)
    if (message == "terminate"):
        print("Did not receive file size. Terminating")
        return "terminate"
    else:
        file_size = int(message.decode().upper()[4:])

    # Open the new file for writing binary data
    with open(new_filename, 'wb') as file:

        # receives the first chunk of data. If no data is received, 
        #   prints "Did not receive data. Terminating." and terminates.
        bytes_received = 0 
        message = receive_data(server_socket)
        if (message == "terminate"):
            print("Did not receive data. Terminating.")
            return "terminate"
        else:
            file.write(message)
            bytes_received += len(message)
            # server_socket.sendto("ACK".encode(), client_address)
            # print('Sent the ACK')

        # Receives the remaining data in chunks until it has received 
        #   as many bytes as the file_size. If no data is received, 
        #   prints "Data transmission terminated prematurely." and terminates.
        while bytes_received < file_size:
            message = receive_data(server_socket)
            if (message == "terminate"):
                print("Data transmission terminated prematurely.")
                return "terminate"
            else:
                file.write(message)
                bytes_received += len(message)
        
        # Sends "FIN" to the server to tell the client that the process is complete.
        send_message("FIN".encode(), server_socket, client_address)
        return new_filename
    

#### CODE FOR SENDING FILE

# Source for timeout function: https://alexandra-zaharia.github.io/posts/function-timeout-in-python-multiprocessing/
# Sends a message and waits for a message containing the string "ACK"
def send_message_and_wait_for_ack(message, server_socket, client_address):
    
    # Sends the message to the client
    server_socket.sendto(message, client_address)

    # Waits for a message containing the string "ACK"
    while True: 
        ack, client_address = server_socket.recvfrom(1048)
        if ("ACK" in ack.decode().upper()):
            break

# Sends a message to a server and waits for an ack with a one second timeout.
#   Calls the function send_message_and_wait_for_ack and if it receives an ACK 
#   before the timeout, returns "success", otherwise returns "terminate".
def send_message(message, server_socket, client_address):
    p = Process(target=send_message_and_wait_for_ack, args=(message, server_socket, client_address,))
    p.start()
    p.join(1)

    if p.is_alive():
        p.terminate()
        p.join()
        return "terminate"
    return "success"

# Sends a file to the server using stop and wait protocol.
def send_file(filename, client_address, server_socket):

    # Sends a message with the length of the data in the format LEN:Bytes, 
    #   if it doesn't receive an ACK, terminates
    file_size = os.path.getsize(filename)
    if (send_message(("LEN:" + str(file_size)).encode(), server_socket, client_address) == "terminate"):
        print("Did not acknowledge file size. Terminating")
        return "terminate"
    
    # Opens the file and sends it in 1000-byte chunks. 
    #   If it doesn't receive an ACK after sending a chunk, terminates.
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1000)  # Read the file in 1000-byte chunks
            if not data:  # If no data left, break the loop
                break
            if (send_message(data, server_socket, client_address) == "terminate"): # Send the file data to the client in a small chunk
                print("Did not receive ACK. Terminating.")
                return "terminate"


#### KEYWORD

# Function to handle the 'keyword' task, which anonymizes a file based on a given keyword
def keywordTask(filename, client_address, server_socket, keyword):
    
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
    send_message(f"File {filename} anonymized. Output file is {anonymized_filename}".encode(), server_socket, client_address)
    #server_socket.sendto(f"File {filename} anonymized. Output file is {anonymized_filename}".encode(), client_address)

# Main server function to handle user commands and communicate with the client
if __name__ == '__main__':
    # Source for how to pass arguments to a file: https://www.pythonforbeginners.com/system/python-sys-argv
    SERVER_PORT=int(sys.argv[1])

    # Creates the server socket
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(("", SERVER_PORT))

    while True:
        print("The server is ready to receive")

        # Receive a command from the client
        message, client_address = server_socket.recvfrom(1048)
        server_socket.sendto("ACK".encode(), client_address)
        print(f"Command: {message.decode()}")
        command = message.decode().split()[0]

        # If the command is 'put', handle file download
        if command == "put":

            # Gets the file name to be downloaded
            file_name = message.decode().split()[1]
            # Call the receive_file function to download the file and get the new file name
            new_file_name = receive_file(SERVER_PORT, server_socket, client_address, file_name)
            
            # Tell the server that the file is downloaded and what the new file name is.
            if (new_file_name != "terminate"):
                send_message(f"File {file_name} downloaded. Output file is {new_file_name}".encode(), server_socket, client_address)
        
        # If the command is 'get', handle file upload
        elif command == "get":
            file_name = message.decode().split()[1]  # Get the file_name from the message
            if (send_file(file_name, client_address, server_socket) != "terminate"): # Send the file to the client
                # Receive a message containing "FIN" to signal that the process is complete
                #   Then receive and print the client response.
                fin = receive_data(server_socket)
                response = receive_data(server_socket)
                if (fin, response != "terminate"):
                    if ("FIN" in fin.decode().upper()):
                        print(f"Client response: {response.decode()}")
                    else:
                        print("Did not receive FIN message. Terminating.")
                else:
                    print("Did not receive client response. Terminating.")

        # If the command is 'keyword', handle file anonymization    
        elif command == "keyword":
            # Gets the keyword and filename from the message
            keyword = message.decode().split()[1]
            file_name = message.decode().split()[2]

            # Completes the file anonymization with the keyword
            keywordTask(file_name, client_address, server_socket, keyword)

        # If the command is 'quit', handle server exit
        elif command == "quit":
            print("Exiting program!")
            break  # Exit the server loop

    server_socket.close()