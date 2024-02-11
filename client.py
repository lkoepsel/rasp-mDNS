import socket

HOST = '10.0.1.3'  # Server IP
PORT = 5001  # Server Port

# Create socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
client.connect((HOST, PORT))

# Send message
message = "Hello Server"
client.sendall(message.encode())

# Receive and print response
response = client.recv(1024)
print(response.decode())

# Close connection
client.close()
