from socket import *
from multiprocessing import Process
import os
import multiprocessing
from multiprocessing import Queue
import multiprocessing.queues as mpq
from multiprocessing import Process
import sys


#### CODE FOR RECEIVING FILE


# Timeout source: https://flipdazed.github.io/blog/quant%20dev/parallel-functions-with-timeouts
# Sends an ACK and waits for data
def ack_and_wait_for_data(q: Queue, client_socket):
    message, server_address = client_socket.recvfrom(1048)
    # print("received " + str(len(message)) + " bytes")
    client_socket.sendto("ACK".encode(), server_address)
    # print('Sent the ACK')
    # sleep(message)
    q.put(message)
    # message = received_message


# receives data
def receive_data(client_socket):
    q_worker = Queue()
    # conn1, conn2 = Pipe()
    # message = multiprocessing.Value('i', "".encode())
    # data.value
    p = multiprocessing.Process(
        target=ack_and_wait_for_data,
        args=(
            q_worker,
            client_socket,
        ),
    )
    p.start()
    try:
        res = q_worker.get(timeout=1)
        return res
    except mpq.Empty:
        p.terminate()
        # print('Timeout!')
        return "terminate"


def receive_file(file_name, client_socket):
    # Part to rename the file if it already exists by appending '_1' to the filename
    parts = file_name.rsplit(
        ".", 1
    )  # Split the filename to separate name and extension
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"  # Add '_1' to the filename to avoid overwriting
    # SERVER_PORT = 12000
    # server_socket = socket(AF_INET, SOCK_DGRAM)
    # server_socket.bind(("", SERVER_PORT))
    # print("the server is ready to receive")

    message, server_address = client_socket.recvfrom(1048)
    # print(message.decode().upper())
    message, server_address = client_socket.recvfrom(1048)
    # print(message.decode().upper())
    file_size = int(message.decode().upper()[4:])
    client_socket.sendto("ACK".encode(), server_address)
    # print('Sent the ACK')

    # Open the new file for writing binary data
    with open(new_filename, "wb") as file:
        bytes_received = 0
        message = receive_data(client_socket)
        # message = receive_data(server_socket, client_address)
        # message, client_address = server_socket.recvfrom(1048)
        if message == "terminate":
            print("Did not receive data. Terminating.")
            return
        else:
            file.write(message)
            bytes_received += len(message)
            # server_socket.sendto("ACK".encode(), client_address)
            # print('Sent the ACK')

        while bytes_received < file_size:
            message = receive_data(client_socket)
            if message == "terminate":
                print("Data transmission terminated prematurely.")
                return
            else:
                file.write(message)
                bytes_received += len(message)
        client_socket.sendto("FIN".encode(), server_address)
        # print("FIN")
    return new_filename


#### CODE FOR SENDING FILE
# source for timeout function: https://alexandra-zaharia.github.io/posts/function-timeout-in-python-multiprocessing/
# Waits for an ack
def wait_for_ack(message, serverName, serverPort, clientSocket):
    clientSocket.sendto(message, (serverName, serverPort))
    # print('Sent the message')
    ack, server_address = clientSocket.recvfrom(1048)
    # if (ack.decode().upper() == "ACK"):
    # print("ACK")


# Sends a message
def send_message(message, serverName, serverPort, clientSocket):
    p = Process(
        target=wait_for_ack,
        args=(
            message,
            serverName,
            serverPort,
            clientSocket,
        ),
    )
    p.start()
    p.join(1)
    if p.is_alive():
        p.terminate()
        p.join()
        return "terminate"
    return "success"


def send_file(filename, serverName, serverPort, clientSocket):
    # Sends a message with the length of the data in the format LEN:Bytes
    file_size = os.path.getsize(filename)
    # clientSocket.sendto(("LEN:" + str(file_size)).encode(), (serverName, serverPort))
    send_message(
        ("LEN:" + str(file_size)).encode(), serverName, serverPort, clientSocket
    )

    with open(filename, "rb") as file:
        while True:
            data = file.read(1000)  # Read the file in 1000-byte chunks
            if not data:  # If no data left, break the loop
                break
            if (
                send_message(data, serverName, serverPort, clientSocket) == "terminate"
            ):  # Send the file data to the server in a small chunk
                print("Did not receive ACK. Terminating.")
                return


# Main client function to handle user commands and communicate with the server
def startClient(serverName, serverPort):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    # clientSocket = socket(AF_INET, SOCK_STREAM)  # Create a TCP socket
    # clientSocket.connect((serverName, serverPort))  # Connect to the server

    while True:
        command = input("Enter command: ")  # Get the user's command as a list
        # Tell the server what the command was
        send_message(command.encode(), serverName, serverPort, clientSocket)

        # If the command is 'put', handle file upload
        if command.split()[0] == "put":
            print("Awaiting server response.")
            filename = command.split()[1]  # Get the filename from the command
            send_file(filename, serverName, serverPort, clientSocket)
            fin, server_address = clientSocket.recvfrom(1048)
            server_response, server_address = clientSocket.recvfrom(1048)
            if fin.decode().upper() == "FIN":
                print(f"Server response: {server_response.decode()}")
        # If the command is 'get', handle file download
        elif command.split()[0] == "get":
            print("Awaiting server response.")
            new_filename = receive_file(
                command.split()[1], clientSocket
            )  # Call the recFile function to download the file
            clientSocket.sendto(
                f"File {command.split()[1]} downloaded. Output file is {new_filename}".encode(),
                (serverName, serverPort),
            )
            print(
                f"File {command.split()[1]} downloaded. Output file is {new_filename}"
            )
        # If the command is 'keyword', handle file anonymization
        elif command.split()[0] == "keyword":
            print("Awaiting server response.")
            server_response, server_address = clientSocket.recvfrom(1048)
            print(f"Server response: {server_response.decode()}")
        # If the command is 'quit', handle client exit
        elif command.split()[0] == "quit":
            print("Exiting program!")
            break  # Exit the loop and close the client

    clientSocket.close()  # Close the socket after quitting


if __name__ == "__main__":
    # Source for how to pass arguments to a file: https://www.pythonforbeginners.com/system/python-sys-argv
    serverName = str(sys.argv[1])
    serverPort = int(sys.argv[2])
    startClient(serverName, serverPort)

    # Opens a test file
    # send_file('File1.txt')

    # clientSocket.close()
