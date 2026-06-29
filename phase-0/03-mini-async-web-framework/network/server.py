"""
network/server.py

TCP Server

Responsibilities
----------------
- Create listening socket
- Accept new clients
- Create Connection objects
- Register sockets with EventLoop

The server NEVER calls recv().

The EventLoop handles all client I/O.

> this event-driven architecture is what allows the server to handle thousands of clients concurrently.
"""

"""
network/server.py
"""

from __future__ import annotations

import selectors
import socket

from config import (
    HOST,
    PORT,
    BACKLOG,
)

from runtime.event_loop import EventLoop

from network.connection import Connection

from http.request_processor import RequestProcessor


class Server:

    def __init__(
        self,
        router,
    ):

        self.router = router

        self.loop = EventLoop()

        self.processor = RequestProcessor(
            router
        )

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        self.server_socket.setblocking(False)

    # =====================================================
    # Start
    # =====================================================

    def start(
        self,
    ):

        self.server_socket.bind(
            (
                HOST,
                PORT,
            )
        )

        self.server_socket.listen(
            BACKLOG
        )

        print(
            f"Listening on "
            f"http://{HOST}:{PORT}"
        )

        self.loop.register(
            sock=self.server_socket,
            events=selectors.EVENT_READ,
            callback=self.accept_connection,
        )

        self.loop.run_forever()

    # =====================================================
    # Accept
    # =====================================================

    def accept_connection(
        self,
        server_socket,
        mask,
    ):

        try:

            client_socket, client_address = (
                server_socket.accept()
            )

        except BlockingIOError:

            return

        print(
            f"Accepted {client_address}"
        )

        client_socket.setblocking(False)

        connection = Connection(
            client_socket=client_socket,
            client_address=client_address,
            processor=self.processor,
            event_loop=self.loop,
        )

        self.loop.register(
            sock=client_socket,
            events=selectors.EVENT_READ,
            callback=connection.read,
        )