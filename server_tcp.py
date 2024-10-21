from socket import *


def anonymizeFile(filename, keyword):
    try:
        with open(filename, 'r') as file:
            content = file.read()
        
        anonymized_content = content.replace(keyword, 'X' * len(keyword))

        anonymized_filename = filename.split('.')[0] + '_anon.txt'
        with open(anonymized_filename, 'w') as anon_file:
           anon_file.write(anonymized_content)
        
        return anonymized_filename
    except FileNotFoundError:
       return None
      

def doTask(conn):
    filename = conn.recv(1024).decode()

    with open(filename, 'wb') as file:
       while True:
          data = conn.recv(1024)
          if not data:
             break
          file.write(data)
    
    keyword = conn.recv(1024).decode()
    print(f"Anonymizing keyword '{keyword}' in file '{filename}'")

    anonymized_filename = anonymizeFile(filename, keyword)

    if anonymized_filename:
       with open(anonymized_filename, 'rb') as file:
          conn.sendfile(file)
    else:
       conn.sendall(b"File not found or could not be anonymized.")

    conn.close()


def startServer(port):
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',port))
    serverSocket.listen(1)
    print('The server is ready to receive')

    while True:
       connectionSocket, addr = serverSocket.accept()
       print(f"Connection established with {addr}")
       doTask(connectionSocket)


if __name__ == "__main__":
    port = 12000
    startServer(port)