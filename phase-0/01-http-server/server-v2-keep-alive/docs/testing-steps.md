# HTTP Server V2 - Testing Guide

## Start Server

Run:

```bash
python3 server.py
```

Expected Output:

```text
HTTP Server Running On 0.0.0.0:8080
```

---

# Test 1 - Hello Endpoint

Request:

```bash
curl http://localhost:8080/hello
```

Expected Response:

```text
Hello User
```

Server Log:

```text
GET /hello
```

---

# Test 2 - Users Endpoint

Request:

```bash
curl http://localhost:8080/users
```

Expected Response:

```json
["anant", "john", "alice"]
```

Server Log:

```text
GET /users
```

---

# Test 3 - Health Endpoint

Request:

```bash
curl http://localhost:8080/health
```

Expected Response:

```json
{"status":"UP"}
```

Server Log:

```text
GET /health
```

---

# Test 4 - POST Request

Request:

```bash
curl -X POST \
http://localhost:8080/users \
-d '{"name":"Anant"}'
```

Expected Response:

```text
Received: {"name":"Anant"}
```

Server Log:

```text
POST /users
```

---

# Test 5 - Unknown Route

Request:

```bash
curl http://localhost:8080/unknown
```

Expected Response:

```text
Not Found
```

HTTP Status:

```text
404 Not Found
```

---

# Test 6 - View Response Headers

Request:

```bash
curl -i http://localhost:8080/hello
```

Expected:

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 10
Connection: keep-alive

Hello User
```

Observe:

```text
Content-Length
Connection: keep-alive
```

---

# Test 7 - Verbose Mode

Request:

```bash
curl -v http://localhost:8080/hello
```

Purpose:

Shows:

* TCP Connection
* Request Headers
* Response Headers

Useful for debugging.

---

# Test 8 - Keep-Alive Verification

Request:

```bash
curl -v \
-H "Connection: keep-alive" \
http://localhost:8080/hello
```

Observe:

```http
Connection: keep-alive
```

in response.

---

# Test 9 - Browser Testing

Open browser:

```text
http://localhost:8080/hello
```

Expected:

```text
Hello User
```

---

Open:

```text
http://localhost:8080/users
```

Expected:

```json
["anant","john","alice"]
```

---

# Test 10 - Raw TCP Test Using Telnet

Connect:

```bash
telnet localhost 8080
```

Send manually:

```http
GET /hello HTTP/1.1
Host: localhost

```

(Press Enter twice)

Expected:

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 10
Connection: keep-alive

Hello User
```

---

# Test 11 - Raw TCP Test Using Netcat

Create request:

```bash
printf "GET /hello HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc localhost 8080
```

Expected:

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 10
Connection: keep-alive

Hello User
```

---

# Test 12 - Observe Keep-Alive Limitation

Open Terminal 1:

```bash
telnet localhost 8080
```

Connection stays open.

Do not close it.

---

Open Terminal 2:

```bash
curl http://localhost:8080/users
```

Expected:

```text
Request hangs
```

Reason:

```text
Server is still busy with Client1.
```

This demonstrates the major limitation of V2.

---

# Test 13 - Demonstrate Blocking recv()

Client1:

```bash
telnet localhost 8080
```

Connect and do nothing.

---

Server State:

```python
data = client_socket.recv(...)
```

Server is blocked.

---

Client2:

```bash
curl http://localhost:8080/hello
```

Result:

```text
Waiting...
```

Reason:

```text
Server never returned to accept().
```

---

# Test 14 - Demonstrate Content-Length

Request:

```bash
curl -i http://localhost:8080/health
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 15

{"status":"UP"}
```

Count:

```text
{
"
s
t
a
t
u
s
"
:
"
U
P
"
}
```

Total:

```text
15 bytes
```

Content-Length matches body size.

---

# Test 15 - Multiple Requests On Same Connection

Using Telnet:

```bash
telnet localhost 8080
```

Request 1:

```http
GET /hello HTTP/1.1
Host: localhost

```

Receive response.

---

Request 2:

```http
GET /users HTTP/1.1
Host: localhost

```

Receive response.

---

Request 3:

```http
GET /health HTTP/1.1
Host: localhost

```

Receive response.

Observe:

```text
Same TCP connection.
Multiple HTTP requests.
```

This is Keep-Alive in action.

---

# Key Learning Outcomes

After completing these tests you should understand:

* TCP Connection Lifecycle
* HTTP Request Structure
* HTTP Response Structure
* Headers
* Content-Length
* Keep-Alive
* Request Parsing
* Routing
* Middleware
* Blocking I/O
* Why V2 does not scale
* Why Threads are needed
* Why Async Servers exist
* Foundation of FastAPI and Uvicorn
