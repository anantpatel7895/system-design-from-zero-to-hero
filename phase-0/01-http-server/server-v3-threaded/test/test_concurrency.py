import threading
import requests
import time


def slow_client():

    start = time.time()

    print(
        "SLOW REQUEST START"
    )

    response = requests.get(
        "http://localhost:8080/slow"
    )

    print(
        response.text
    )

    print(
        f"SLOW TOOK "
        f"{time.time()-start:.2f}s"
    )


def fast_client():

    time.sleep(1)

    start = time.time()

    print(
        "FAST REQUEST START"
    )

    response = requests.get(
        "http://localhost:8080/hello"
    )

    print(
        response.text
    )

    print(
        f"FAST TOOK "
        f"{time.time()-start:.2f}s"
    )


t1 = threading.Thread(
    target=slow_client
)

t2 = threading.Thread(
    target=fast_client
)

t1.start()
t2.start()

t1.join()
t2.join()