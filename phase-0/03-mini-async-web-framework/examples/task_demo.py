"""
Task Demo
"""

from runtime.future import Future
from runtime.task import Task


async def worker():

    print("Worker Started")

    future = Future()

    future.set_result(100)

    value = await future

    print(
        "Received:",
        value,
    )

    return value


task = Task(
    worker()
)

future = task.step()

print(future)

task.step(
    future.result()
)

print(task)