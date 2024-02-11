import socket

HOST = '127.0.0.1'
PORT = 5001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}: {PORT}")

    client_socket, address = s.accept()

    while True:
        data = socket.recv(1024)
        if not data:
            break
        print(data.decode())
