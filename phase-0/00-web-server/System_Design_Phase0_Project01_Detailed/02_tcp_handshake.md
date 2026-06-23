
# TCP Three Way Handshake

Client -> SYN
Server -> SYN ACK
Client -> ACK

Only after the handshake completes does Linux place the connection into the **accept queue**.

## IMPORTANT: TCP Handshake
Python does not perform the handshake.
Linux Kernel performs the handshake.
