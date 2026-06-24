import socket
import selectors

from request import parse_request
from router import dispatch
from response import build_response
from middleware import log_request


HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 4096


selector = selectors.DefaultSelector()


def accept_connection(server_socket):

    client_socket, addr = (
        server_socket.accept()
    )

    print(
        f"CONNECTED: {addr}"
    )

    client_socket.setblocking(False)

    selector.register(
        client_socket,
        selectors.EVENT_READ,
        handle_client
    )


def handle_client(client_socket):

    try:

        data = client_socket.recv(
            BUFFER_SIZE
        )

        if not data:

            selector.unregister(
                client_socket
            )

            client_socket.close()

            return

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

        client_socket.send(
            raw_response.encode()
        )

    except Exception as e:

        print(
            f"ERROR: {e}"
        )

        selector.unregister(
            client_socket
        )

        client_socket.close()


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind(
    (
        HOST,
        PORT
    )
)

server_socket.listen(100)

server_socket.setblocking(False)

selector.register(
    server_socket,
    selectors.EVENT_READ,
    accept_connection
)

print(
    f"Async HTTP Server Running "
    f"On {HOST}:{PORT}"
)

# event loop
while True:

    events = selector.select()
    """
    > is the line that blocks the event loop until there are ready sockets to read from or write to.
    > The selector.select() method is a blocking call that waits for events on the registered sockets
    > When a socket is ready, the selector returns a list of events that can be processed
    > The event loop then iterates over the list of events and calls the appropriate callback function
    > for each ready socket. The callback function is responsible for handling the event and performing any necessary I/O operations on the socket.
    > The event loop then goes back to waiting for more events to occur.
    > This allows the server to handle multiple connections concurrently without blocking on any one connection, which is a key feature of asynchronous programming.
    > The event loop is the core of the asynchronous server, and it is responsible for managing the flow of data between the server and its clients
    > The event loop is a fundamental concept in asynchronous programming, and it is used in many programming languages and frameworks to build scalable and efficient applications.
    > The event loop is a mechanism that allows a program to handle multiple tasks concurrently without blocking on any one task. In the context of an asynchronous server, the event loop is responsible for managing incoming connections and requests from clients. When a client connects to the server, the event loop registers the connection and waits for incoming data. When data is received, the event loop processes the request and sends a response back to the client. The event loop allows the server to handle multiple connections simultaneously without blocking on any one connection, which is a key feature of asynchronous programming. The event loop is typically implemented using a combination of non-blocking I/O and callbacks, which allows the server to efficiently manage multiple connections and requests without blocking on any one connection.

    Sleeps
    ↓
    Gets awakened by the Kernel
    ↓
    Receives ready sockets
    """


    for key, mask in events:
        print(
            f"EVENT: {key.fileobj} "
            f"MASK: {mask}"
        )

        callback = key.data

        callback(
            key.fileobj
        )