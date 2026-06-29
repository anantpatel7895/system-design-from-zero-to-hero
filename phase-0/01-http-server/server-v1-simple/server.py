import socket

from router import route_request
from response import build_response


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

    client_socket, client_address = server.accept() # Main Thread first blocks here until a client connects, then returns a new socket object (client_socket) that can be used to communicate with the client, and the address of the client (client_address).

    print(f"Client Connected: {client_address}")

    try:

        while True:

            request = client_socket.recv(BUFFER_SIZE) # Main Thread blocks here until data is received from the client. It returns the data received as bytes.

            if not request:
                break

            request_text = request.decode()

            print("\nREQUEST:")
            print(request_text)

            request_line = request_text.split("\r\n")[0]

            try:
                method, path, version = request_line.split()

            except ValueError:
                break

            status_code, body = route_request(
                method,
                path
            )

            response = build_response(
                status_code,
                body
            )

            client_socket.sendall(
                response.encode()
            )

    except Exception as e:

        print("ERROR:", e)

    finally:

        print(
            f"Connection Closed: {client_address}"
        )

        client_socket.close()