```text
1. Client connects
2. client_handler scheduled

ready_tasks:
    [client_handler]

3. next(task)

CLIENT TASK STARTED

yield WaitForRead(client_sock)

waiting_tasks:
    {client_sock : task}

4. selector.select()
   thread sleeps

5. Client sends "hello"

6. OS wakes selector

7. task moved back to ready_tasks

ready_tasks:
    [client_handler]

8. next(task)

data = recv()

RECEIVED: hello

CLIENT TASK FINISHED

9. StopIteration

TASK FINISHED
```
