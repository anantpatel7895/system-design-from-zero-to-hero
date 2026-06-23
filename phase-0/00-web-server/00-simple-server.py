# simple_server.py

import socket

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind(("0.0.0.0", 8080))

server_socket.listen(5)

print("Waiting for one client...")

client_socket, address = server_socket.accept()

print(f"Connected: {address}")

client_socket.send(
    b"Hello From Simple Server\n"
)

client_socket.close()

server_socket.close()

print("Server Stopped")