from socket import *
import sys



def putTask(conn):
    filename = conn.recv(1024).decode()
    conn.sendall(b"Filename received.")

    # Part to rename the file if it already exists
    parts = filename.rsplit('.', 1)
    name = parts[0]
    ext = parts[1]
    new_filename = f"{name}_1.{ext}"

    with open(new_filename, 'wb') as file:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            file.write(data)
    
    conn.sendall(b"Server response: File uploaded.")

def getTask(conn):
    filename = conn.recv(1024).decode()
    conn.sendall(b"Filename received.")
    with open(filename, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            conn.sendall(data)

def keywordTask(conn):
    conn.sendall(b"Keyword command received.")
    key_and_file = conn.recv(1024).decode().split()
    keyword, filename = key_and_file[0], key_and_file[1]
    print(f"{keyword}, {filename}")

    parts = filename.rsplit('.', 1)
    name = parts[0]
    ext = parts[1]
    anonymized_filename = f"{name}_anon.{ext}"
    with open(filename, 'r') as file:
        content = file.read()
    
    anonymized_content = content.replace(keyword, 'X' * len(keyword))

    with open(anonymized_filename, 'w') as anon_file:
        anon_file.write(anonymized_content)
    
    conn.sendall(f"Server response: File {filename} anonymized. Output file is {anonymized_filename}".encode())

def startServer(port):
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',port))
    serverSocket.listen(1)
    print(f'The server is ready to receive on port {port}')

    while True:
        connectionSocket, addr = serverSocket.accept()
        print(f"Connection established with {addr}")
        command = connectionSocket.recv(1024).decode()
        connectionSocket.sendall(b"File received.")
        if command == "put":
            putTask(connectionSocket)
        elif command == "get":
            getTask(connectionSocket)
        elif command == "keyword":
            keywordTask(connectionSocket)
        
        connectionSocket.close()
    

    



if __name__ == "__main__":
    
    port = 12000 # Default port for program

    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    startServer(port)