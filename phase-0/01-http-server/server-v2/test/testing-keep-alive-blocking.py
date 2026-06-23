import socket 
import threading 
import time 


HOST = "13.234.225.164" # ip of host machine (or "localhost" if running locally)
PORT = 8080 

def client1(): 
    print("=" * 60) 
    print("CLIENT1 CONNECTING") 
    print("=" * 60) 
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
    sock.connect((HOST, PORT)) # 3-way handshake
    print("CLIENT1 CONNECTED") 
    request = ( "GET /hello HTTP/1.1\r\n" "Host: localhost\r\n" "\r\n" ) 
    print("\nCLIENT1 -> REQUEST 1") 
    sock.send(request.encode())  # send http request to server
    response = sock.recv(4096) 
    print( "\nCLIENT1 <- RESPONSE 1" ) 
    print( response.decode() ) 
    print( "\nCLIENT1 KEEPING CONNECTION OPEN..." ) 
    print( "Sleeping 30 seconds..." ) 
    time.sleep(30) 
    print( "\nCLIENT1 -> REQUEST 2" ) 
    sock.send(request.encode())  # send http request to server
    response = sock.recv(4096) 
    print( "\nCLIENT1 <- RESPONSE 2" ) 
    print( response.decode() ) 
    sock.close() 
    print( "\nCLIENT1 CLOSED" ) 


def client2(): 
    time.sleep(5) 
    print("\n" + "=" * 60) 
    print("CLIENT2 TRYING TO CONNECT") 
    print("=" * 60) 
    start = time.time() 
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
    sock.connect((HOST, PORT))    # 3-way handshake
    print( "CLIENT2 CONNECTED" ) 
    request = ( "GET /users HTTP/1.1\r\n" "Host: localhost\r\n" "\r\n" ) 
    print( "\nCLIENT2 -> REQUEST" ) 
    sock.send(request.encode())  # send http request to server
    response = sock.recv(4096) 
    end = time.time() 
    print( "\nCLIENT2 <- RESPONSE" ) 
    print( response.decode() ) 
    print( f"\nCLIENT2 WAITED " f"{end - start:.2f} seconds" ) 
    sock.close() 


thread1 = threading.Thread( target=client1 ) 
thread2 = threading.Thread( target=client2 ) 
thread1.start() 
thread2.start() 
thread1.join() 
thread2.join()