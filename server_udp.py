from socket import *
import multiprocessing

if __name__ == '__main__':
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

   # Open the new file for writing binary data
    with open("recieved_data", 'wb') as file:
        bytes_received = 0 
        server_socket.sendto("ACK".encode(), client_address)
        print('Sent the ACK')
        message, client_address = server_socket.recvfrom(1048)
        print("recieved " + str(len(message)) + " bytes")
        file.write(message)
        bytes_received += len(message)

        while bytes_received < file_size:
            server_socket.sendto("ACK".encode(), client_address)
            print('Sent the ACK')
            message, client_address = server_socket.recvfrom(1048)
            print("recieved " + str(len(message)) + " bytes")
            file.write(message)
            bytes_received += len(message)

    print("All bytes recieved")
    server_socket.sendto("FIN".encode(), client_address)
    #recieve_file()

    # while True:
    #     message, client_address = server_socket.recvfrom(1048)
    #     modified_message = message.decode().upper()
    #     print(f"{message} -> {modified_message}")
    #     server_socket.sendto("ACK".encode(), client_address)




    # ret = {"message": ""}

# # Sends an ACK and waits for data
# def ack_and_wait_for_data(queue):
#     server_socket.sendto("ACK".encode(), client_address)
#     print('Sent the ACK')
#     message, client_address = server_socket.recvfrom(1048)
#     print("recieved " + str(len(message)) + " bytes")
#     ret = queue.get()
#     ret['message'] = message
#     queue.put(ret)

# # recieves data
# def recieve_data():
#     queue = multiprocessing.Queue()
#     queue.put(ret)
#     p = multiprocessing.Process(target=ack_and_wait_for_data, args=(queue, ))
#     p.start()
#     p.join(1)
#     if p.is_alive():
#         p.terminate()
#         p.join()
#         return "terminate"
#     print(queue.get)
#     #return return_dict.values


# def recieve_file():
#     print("the server is ready to receive")

#     message, client_address = server_socket.recvfrom(1048)
#     print(message.decode().upper())
#     message, client_address = server_socket.recvfrom(1048)
#     print(message.decode().upper())
#     file_size = int(message.decode().upper()[4:])
#     server_socket.sendto("ACK".encode(), client_address)

#     # Open the new file for writing binary data
#     with open("recieved_data", 'wb') as file:
#         bytes_received = 0 
#         recieve_data()
        #message = recieve_data()
        # if (message == "terminate"):
        #     print("Did not receive data. Terminating.")
        #     return 
        #else:
            #file.write(message)
            #bytes_received += len(message)

        # while bytes_received < file_size:
        #     recieve_data()
            #message = recieve_data()
            # if (message == "terminate"):
            #     print("Data transmission terminated prematurely.")
            #     return 
            # else:
            #     file.write(message)
            #     bytes_received += len(message)