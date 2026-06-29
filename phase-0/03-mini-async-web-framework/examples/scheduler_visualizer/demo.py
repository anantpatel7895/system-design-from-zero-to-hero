from runtime.event_loop import EventLoop
from runtime.sleep import sleep

from .scheduler_renderer import SchedulerRenderer


async def task1():

    print("Task-1 Started")

    await sleep(3)

    print("Task-1 Resumed")

    await sleep(2)

    print("Task-1 Finished")


async def task2():

    print("Task-2 Started")

    await sleep(1)

    print("Task-2 Finished")


async def task3():

    print("Task-3 Started")

    await sleep(5)

    print("Task-3 Finished")


def main():

    loop = EventLoop()

    renderer = SchedulerRenderer()

    #
    # Observe scheduler
    #

    loop.on_iteration(
        renderer.render
    )

    #
    # Schedule tasks
    #

    loop.create_task(
        task1()
    )

    loop.create_task(
        task2()
    )

    loop.create_task(
        task3()
    )

    #
    # Run scheduler
    #

    loop.run_forever()

    print()

    print("=" * 60)

    print("Scheduler Finished")

    print("=" * 60)


if __name__ == "__main__":

    main()