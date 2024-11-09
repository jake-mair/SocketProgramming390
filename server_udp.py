from socket import *
import multiprocessing
from multiprocessing import Queue
import multiprocessing.queues as mpq

# Timeout source: https://flipdazed.github.io/blog/quant%20dev/parallel-functions-with-timeouts
# Sends an ACK and waits for data
def ack_and_wait_for_data(q: Queue, server_socket):
    message, client_address = server_socket.recvfrom(1048)
    print("recieved " + str(len(message)) + " bytes")
    server_socket.sendto("ACK".encode(), client_address)
    print('Sent the ACK')
    #sleep(message)
    q.put(message)
    #message = recieved_message

# recieves data
def recieve_data(server_socket):
    q_worker = Queue()
    #conn1, conn2 = Pipe()
    #message = multiprocessing.Value('i', "".encode())
    #data.value
    p = multiprocessing.Process(target=ack_and_wait_for_data, args=(q_worker, server_socket, ))
    p.start()
    try:
        res = q_worker.get(timeout=1)
        return res
    except mpq.Empty:
        p.terminate()
        print('Timeout!')
        return "terminate"


def recieve_file():
    SERVER_PORT = 12000
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(("", SERVER_PORT))
    print("the server is ready to receive")

    message, client_address = server_socket.recvfrom(1048)
    print(message.decode().upper())
    message, client_address = server_socket.recvfrom(1048)
    print(message.decode().upper())
    file_size = int(message.decode().upper()[4:])
    server_socket.sendto("ACK".encode(), client_address)
    print('Sent the ACK')

    # Open the new file for writing binary data
    with open("recieved_data", 'wb') as file:
        bytes_received = 0 
        message = recieve_data(server_socket)
        #message = recieve_data(server_socket, client_address)
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
            message = recieve_data(server_socket)
            if (message == "terminate"):
                print("Data transmission terminated prematurely.")
                return 
            else:
                file.write(message)
                bytes_received += len(message)


if __name__ == '__main__':
    recieve_file()