from socket import *

SERVER_PORT = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(("", SERVER_PORT))
print("the server is ready to receive")

while True:
    message, client_address = server_socket.recvfrom(2048)
    modified_message = message.decode().upper()
    print(f"{message} -> {modified_message}")
    server_socket.sendto(modified_message.encode(), client_address)
