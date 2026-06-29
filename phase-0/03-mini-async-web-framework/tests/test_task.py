from runtime.future import Future
from runtime.task import Task


async def worker():

    future = Future()

    future.set_result(42)

    value = await future

    return value


def test_task():

    coro = worker()

    task = Task(coro)

    future = task.step()

    assert future.done()

    task.step(
        future.result()
    )

    assert task.done()

    assert task.result() == 42