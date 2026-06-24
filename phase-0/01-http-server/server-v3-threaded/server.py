import socket
import threading

from request import parse_request
from router import dispatch
from response import build_response
from middleware import log_request


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

server.bind(
    (
        HOST,
        PORT
    )
)

server.listen(100) # Accept up to 100 connections in the queue

print(
    f"Threaded HTTP Server "
    f"Running On {HOST}:{PORT}"
)


def handle_client(
    client_socket,
    client_address
):

    print(
        f"THREAD STARTED: "
        f"{client_address}"
    )

    try:

        while True:

            data = client_socket.recv(
                BUFFER_SIZE
            )

            if not data:
                break

            request = parse_request(
                data
            )

            log_request(
                request
            )

            response = dispatch(
                request
            )

            raw_response = (
                build_response(
                    response
                )
            )

            client_socket.sendall(
                raw_response.encode()
            )

    except Exception as e:

        print(
            f"ERROR "
            f"{client_address}: "
            f"{e}"
        )

    finally:

        print(
            f"THREAD CLOSED: "
            f"{client_address}"
        )

        client_socket.close()


while True:

    client_socket, client_address = (
        server.accept()
    )

    thread = threading.Thread(
        target=handle_client,
        args=(
            client_socket,
            client_address
        )
    )

    thread.start()