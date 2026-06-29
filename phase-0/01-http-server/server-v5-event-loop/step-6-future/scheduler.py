from future import Future
from task import Task


class Scheduler:

    def __init__(self):

        self.ready = []

    def create_task(self, coroutine):

        task = Task(coroutine)

        self.ready.append(task)

        return task

    def run(self):

        while self.ready:

            task = self.ready.pop(0)

            future = task.run()

            if future is None:

                continue

            future.waiting_task = task