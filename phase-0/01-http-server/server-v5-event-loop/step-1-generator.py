def task():

    print("Task Started")

    yield

    print("Task Resumed")

    yield

    print("Task Finished")


g = task()

next(g)

print("Scheduler Running...")

next(g)

print("Scheduler Running...")

next(g)