from future import Future
from scheduler import Scheduler


future = Future()


def worker():

    print(
        "Worker Started"
    )

    message = yield future

    print(
        f"Worker Received: {message}"
    )

    print(
        "Worker Finished"
    )


scheduler = Scheduler()

scheduler.create_task(
    worker()
)

print(
    "==============="
)

print(
    "FIRST RUN"
)

print(
    "==============="
)

scheduler.run()

print()

print(
    "Future completed..."
)

future.set_result(
    "Hello From Future"
)

print()

print(
    "==============="
)

print(
    "RESUMING"
)

print(
    "==============="
)

future.waiting_task.run(
    future.result
)