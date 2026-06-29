import socket

from request import parse_request
from router import dispatch
from response import build_response

from middleware import (
    log_request,
    log_headers
)


HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 4096


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))

server.listen(5)

print(f"HTTP Server Running On {HOST}:{PORT}")


while True:
    print("\nWaiting for client at the accept() call...")
    client_socket, client_address = server.accept() # blocking call
    """
    Accepts a connection from a client. This is a **blocking call**, meaning the server will wait here until a client connects.
    Once a client connects, it returns a new socket object (client_socket) that can be used to communicate with the client, and the address of the client (client_address).
    """

    print(
        f"\nClient Connected: "
        f"{client_address}"
    )


    try:

        while True:

            print(
                f"\nWaiting for data from "
                f"{client_address} at the recv() call..."
            )

            data = client_socket.recv(
                BUFFER_SIZE
            )
            """
            Receives data from the client. This is a **blocking call**, meaning the server will wait here until data is received.
            """

            print(data)

            if not data:
                print("CLIENT DISCONNECTED")
                break

            request = parse_request(data)

            log_request(request)

            log_headers(request)

            response = dispatch(request)

            raw_response = build_response(
                response
            )

            client_socket.sendall(
                raw_response.encode()
            )

    except Exception as e:

        print("ERROR:", e)

    finally:

        print(
            f"Connection Closed: "
            f"{client_address}"
        )

        client_socket.close()