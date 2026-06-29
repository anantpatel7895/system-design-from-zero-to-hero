import selectors
import socket


class WaitForRead:

    def __init__(self, sock):
        self.sock = sock

    def __repr__(self):
        return f"WaitForRead({self.sock})"


# coroutine that handles a client connection
def client_handler(client_sock):

    print("CLIENT TASK STARTED")

    yield WaitForRead(client_sock) # Wait for the network event to read data from the client socket

    data = client_sock.recv(1024)

    print(
        "RECEIVED:",
        data.decode()
    )

    print("CLIENT TASK FINISHED")


selector = selectors.DefaultSelector()

ready_tasks = []

waiting_tasks = {}


def schedule(task):
    print("SCHEDULING TASK, ", task)
    ready_tasks.append(task)


def event_loop():

    while ready_tasks or waiting_tasks:

        while ready_tasks:

            task = ready_tasks.pop(0)

            try:

                result = next(task)

                if isinstance(result, WaitForRead):

                    waiting_tasks[
                        result.sock
                    ] = task

                    # Register the client socket with the selector to wait for it to be ready for reading. When the socket is ready, the selector will notify us, and we can resume the task.
                    selector.register(
                        result.sock,
                        selectors.EVENT_READ
                    )

            except StopIteration:
                print("TASK FINISHED")
                pass

        events = selector.select() # Blocking call that waits for I/O events on registered sockets. It returns a list of (key, events) tuples for sockets that are ready for I/O operations.
        print(
            f"EVENT LOOP: "
            f"Selector returned {len(events)} ready sockets"
        )
        for key, mask in events:
            print(
                f"EVENT LOOP: "
                f"Socket {key.fileobj} is ready for reading"
            )
            sock = key.fileobj

            selector.unregister(
                sock
            )

            task = waiting_tasks.pop(
                sock
            )

            schedule(task)


server_sock = socket.socket()

server_sock.bind(
    ("localhost", 9999)
)

server_sock.listen(1) # accept queue size only 1 connection

print(
    "Waiting for client..."
)

client_sock, addr = (
    server_sock.accept()           # Main thread first blocks here until a client connects,
)

print(
    f"Connected: {addr}"
)

schedule(
    client_handler(
        client_sock
    )
)

event_loop()

