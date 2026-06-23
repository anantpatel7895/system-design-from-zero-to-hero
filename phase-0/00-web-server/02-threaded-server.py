# threaded_server.py

import socket
import threading
import time


def handle_client(client_socket, address):

    print(f"[THREAD] Started {address}")

    data = client_socket.recv(1024)

    print(
        f"[{address}] Received: "
        f"{data.decode(errors='ignore')}"
    )

    # Simulate long work
    time.sleep(10)

    client_socket.send(
        b"Request Processed\n"
    )

    client_socket.close()

    print(f"[THREAD] Closed {address}")


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

print("Threaded Server Started")


while True:

    print("Waiting for connection...")

    client_socket, address = server_socket.accept()

    print(
        f"Accepted connection from "
        f"{address}"
    )

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, address)
    )

    thread.start()