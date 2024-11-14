import sys
from socket import *
import multiprocessing
from multiprocessing import Queue
import multiprocessing.queues as mpq
from multiprocessing import Process
import os

#### CODE FOR RECEIVING FILE

# Timeout source: https://flipdazed.github.io/blog/quant%20dev/parallel-functions-with-timeouts
# Sends an ACK and waits for data
def ack_and_wait_for_data(q: Queue, server_socket):
    message, client_address = server_socket.recvfrom(1048)
    #print("received " + str(len(message)) + " bytes")
    server_socket.sendto("ACK".encode(), client_address)
    #print('Sent the ACK')
    #sleep(message)
    q.put(message)
    #message = received_message

# receives data
def receive_data(server_socket):
    q_worker = Queue()
    p = multiprocessing.Process(target=ack_and_wait_for_data, args=(q_worker, server_socket, ))
    p.start()
    try:
        res = q_worker.get(timeout=1)
        return res
    except mpq.Empty:
        p.terminate()
        #print('Timeout!')
        return "terminate"


def receive_file(SERVER_PORT, server_socket, client_address, file_name):
    # Part to rename the file if it already exists by appending '_1' to the filename
    parts = file_name.rsplit('.', 1)  # Split the filename to separate name and extension
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"  # Add '_1' to the filename to avoid overwriting
    # SERVER_PORT = 12000
    # server_socket = socket(AF_INET, SOCK_DGRAM)
    # server_socket.bind(("", SERVER_PORT))
    # print("the server is ready to receive")
    # receive message about file length
    message, client_address = server_socket.recvfrom(1048)
    #print(message.decode().upper())
    file_size = int(message.decode().upper()[4:])
    server_socket.sendto("ACK".encode(), client_address)
    #print('Sent the ACK')

    # Open the new file for writing binary data
    with open(new_filename, 'wb') as file:
        bytes_received = 0 
        message = receive_data(server_socket)
        #message = receive_data(server_socket, client_address)
       # message, client_address = server_socket.recvfrom(1048)
        if (message == "terminate"):
            print("Did not receive data. Terminating.")
            return 
        else:
            file.write(message)
            bytes_received += len(message)
            # server_socket.sendto("ACK".encode(), client_address)
            # print('Sent the ACK')

        while bytes_received < file_size:
            message = receive_data(server_socket)
            if (message == "terminate"):
                print("Data transmission terminated prematurely.")
                return 
            else:
                file.write(message)
                bytes_received += len(message)
        server_socket.sendto("FIN".encode(), client_address)
        return new_filename
        #print("FIN")

#### CODE FOR SENDING FILE

# source for timeout function: https://alexandra-zaharia.github.io/posts/function-timeout-in-python-multiprocessing/
# Waits for an ack
def wait_for_ack(message, server_socket, client_address):
    server_socket.sendto(message, client_address)
    #print('Sent the message')
    ack, client_address = server_socket.recvfrom(1048)
    # if (ack.decode().upper() == "ACK"):
    #     print("ACK")

# Sends a message
def send_message(message, server_socket, client_address):
    p = Process(target=wait_for_ack, args=(message, server_socket, client_address,))
    p.start()
    p.join(1)
    if p.is_alive():
        p.terminate()
        p.join()
        return "terminate"
    return "success"

def send_file(filename, client_address, server_socket):
    # Sends a message that we are starting the process now
    server_socket.sendto("STARTING PROCESS NOW".encode(), client_address)
    
    # Sends a message with the length of the data in the format LEN:Bytes
    file_size = os.path.getsize(filename)
    send_message(("LEN:" + str(file_size)).encode(), server_socket, client_address)

    with open(filename, 'rb') as file:
        while True:
            data = file.read(1000)  # Read the file in 1000-byte chunks
            if not data:  # If no data left, break the loop
                break
            if (send_message(data, server_socket, client_address) == "terminate"): # Send the file data to the server in a small chunk
                print("Did not receive ACK. Terminating.")
                return


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
    server_socket.sendto(f"Server response: File {filename} anonymized. Output file is {anonymized_filename}".encode(), client_address)


if __name__ == '__main__':
    # Source for how to pass arguments to a file: https://www.pythonforbeginners.com/system/python-sys-argv
    SERVER_PORT=int(sys.argv[1])

    #SERVER_PORT = 12000
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(("", SERVER_PORT))

    while True:
        print("The server is ready to receive")
        message, client_address = server_socket.recvfrom(1048)
        server_socket.sendto("ACK".encode(), client_address)
        print(f"Command: {message.decode()}")
        command = message.decode().split()[0]
        if command == "put":
            file_name = message.decode().split()[1]
            new_filename = receive_file(SERVER_PORT, server_socket, client_address, file_name)
            server_socket.sendto(f"File {file_name} downloaded. Output file is {new_filename}".encode(), client_address)

        elif command == "get":
            file_name = message.decode().split()[1]
            send_file(file_name, client_address, server_socket)
            print("Awaiting client response.")
            fin, client_address = server_socket.recvfrom(1048)
            client_response, client_address = server_socket.recvfrom(1048)
            if (fin.decode().upper() == "FIN"):
                print(f"Client response: {client_response.decode()}")
        elif command == "keyword":
            keyword = message.decode().split()[1]
            file_name = message.decode().split()[2]
            keywordTask(file_name, client_address, server_socket, keyword)
        elif command == "quit":
            print("Exiting program!")
            break  # Exit the server loop

    server_socket.close()