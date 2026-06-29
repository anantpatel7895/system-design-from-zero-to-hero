import time


class Sleep:

    def __init__(self, seconds):
        self.seconds = seconds


def task1():

    print("Task1 Started")

    yield Sleep(3)

    print("Task1 Resumed")

    yield Sleep(2)

    print("Task1 Finished")


def task2():

    print("Task2 Started")

    yield Sleep(1)

    print("Task2 Resumed")

    yield Sleep(1)

    print("Task2 Finished")


ready_tasks = [
    task1(),
    task2()
]

sleeping_tasks = []


while ready_tasks or sleeping_tasks:
    print("\n-------------")
    print(
        f"READY={len(ready_tasks)} "
        f"SLEEPING={len(sleeping_tasks)}"
    )

    current_time = time.time()

    # Wake sleeping tasks

    for wake_time, task in sleeping_tasks[:]:

        if current_time >= wake_time:

            print(
                f"WAKING TASK "
                f"at {int(current_time)}"
            )

            ready_tasks.append(task)

            sleeping_tasks.remove(
                (wake_time, task)
            )

    # Run ready tasks

    for task in ready_tasks[:]:

        try:

            result = next(task)

            if isinstance(
                result,
                Sleep
            ):

                wake_time = (
                    time.time()
                    + result.seconds
                )

                print(
                    f"SLEEPING "
                    f"{result.seconds}s"
                )

                sleeping_tasks.append(
                    (
                        wake_time,
                        task
                    )
                )

                ready_tasks.remove(
                    task
                )

        except StopIteration:
            print("TASK FINISHED")
            ready_tasks.remove(
                task
            )

    time.sleep(0.1)