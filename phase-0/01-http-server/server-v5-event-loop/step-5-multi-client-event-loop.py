import socket
import selectors


selector = selectors.DefaultSelector()


class WaitForRead:

    def __init__(self, sock):
        self.sock = sock


ready_tasks = []

waiting_tasks = {} # waiting tasks is socket.recv always
"""
Is waiting_tasks always waiting for data (client_socket.recv)?

In this implementation, yes.
"""


def schedule(task):
    ready_tasks.append(task)


def client_handler(sock):
    """
    Coroutine that handles a client connection.
    It waits for the client to send data, reads the data, sends a response, and closes the connection.
    """
    print("CLIENT TASK STARTED")

    yield WaitForRead(sock)

    data = sock.recv(1024)

    print(
        f"RECEIVED: "
        f"{data.decode().strip()}"
    )

    sock.send(
        b"Hello From Event Loop\n"
    )

    sock.close()

    print(
        "CLIENT TASK FINISHED"
    )


def accept_connections(server_sock):

    """
    Accept connections from clients and schedule a new task to handle each client.
    """

    while True:

        try:
            print("ACCEPTING CONNECTIONS")

            client_sock, addr = (
                server_sock.accept()
            )

            print(
                f"CONNECTED: {addr}"
            )

            client_sock.setblocking(
                False
            )

            schedule(
                client_handler(
                    client_sock
                )
            )

        except BlockingIOError:
            print("NO MORE CONNECTIONS")
            break


def event_loop():

    while True:

        while ready_tasks:

            task = ready_tasks.pop(0)

            try:

                result = next(task)

                if isinstance(
                    result,
                    WaitForRead
                ):

                    waiting_tasks[
                        result.sock
                    ] = task

                    selector.register(         # Register client socket 
                        result.sock,
                        selectors.EVENT_READ
                    )

            except StopIteration:
                print("TASK FINISHED : STOP ITERATION")
                pass

        events = selector.select() # event loop blocks here until at least one socket is ready for reading. It returns a list of (key, events) tuples, where key is a SelectorKey object that contains the socket and associated data, and events is a bitmask of events that are ready (in this case, EVENT_READ).
        print(
            f"EVENT LOOP: {events}"
        )

        for key, mask in events:

            sock = key.fileobj

            if sock is server_sock:

                accept_connections(
                    server_sock
                )

            else: # Client socket is ready for reading

                selector.unregister(
                    sock
                )

                task = (
                    waiting_tasks.pop(
                        sock
                    )
                )

                schedule(task)


server_sock = socket.socket()

server_sock.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_sock.bind(
    ("0.0.0.0", 9999)
)

server_sock.listen()

server_sock.setblocking(False)


selector.register( # Register the server socket with the selector to wait for it to be ready for reading. When a client connects, the selector will notify us, and we can accept the connection.
    server_sock,
    selectors.EVENT_READ
)

print("Event Loop Server Running On Port 9999")

event_loop()