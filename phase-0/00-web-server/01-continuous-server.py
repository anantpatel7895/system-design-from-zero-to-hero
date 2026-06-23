# continuous_server.py

import socket

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind(("0.0.0.0", 8080))

server_socket.listen(5)

print("Continuous Server Started")

while True:

    print("Waiting for client...")

    client_socket, address = server_socket.accept()

    print(f"Connected: {address}")

    client_socket.send(
        b"Hello From Continuous Server\n"
    )

    client_socket.close()

    print("Client Disconnected")