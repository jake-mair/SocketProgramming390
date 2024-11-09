from socket import *
from multiprocessing import Process
import os

serverName = "localhost"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

# source for timeout function: https://alexandra-zaharia.github.io/posts/function-timeout-in-python-multiprocessing/
# Waits for an ack
def wait_for_ack(message):
    clientSocket.sendto(message, (serverName, serverPort))
    print('Sent the message')
    ack, server_address = clientSocket.recvfrom(1048)
    if (ack.decode().upper() == "ACK"):
        print("ACK")

# Sends a message
def send_message(message):
    p = Process(target=wait_for_ack, args=(message,))
    p.start()
    p.join(1)
    if p.is_alive():
        p.terminate()
        p.join()
        return "terminate"
    return "success"

def send_file(filename):
    # Sends a message that we are starting the process now
    clientSocket.sendto("STARTING PROCESS NOW".encode(), (serverName, serverPort))

    # Sends a message with the length of the data in the format LEN:Bytes
    file_size = os.path.getsize(filename)
    #clientSocket.sendto(("LEN:" + str(file_size)).encode(), (serverName, serverPort))
    send_message(("LEN:" + str(file_size)).encode())

    with open(filename, 'rb') as file:
        while True:
            data = file.read(1000)  # Read the file in 1000-byte chunks
            if not data:  # If no data left, break the loop
                break
            if (send_message(data) == "terminate"): # Send the file data to the server
                print("Did not receive ACK. Terminating.")
                return

if __name__ == '__main__':
    # Opens a test file
    send_file('File1.txt')
    
    clientSocket.close()