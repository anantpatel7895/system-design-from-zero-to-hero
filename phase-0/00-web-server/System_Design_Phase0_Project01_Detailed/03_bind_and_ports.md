
# bind()

bind(('0.0.0.0', 8080))

Registers the socket with port 8080.

Kernel Table:

8080 -> Python Process

Without bind(), Linux does not know where packets should go.
