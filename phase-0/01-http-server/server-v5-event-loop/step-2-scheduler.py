def task1():

    print("A")

    yield

    print("B")

    yield

    print("C")


def task2():

    print("X")

    yield

    print("Y")

    yield

    print("Z")


tasks = [
    task1(),
    task2()
]


while tasks:

    for task in tasks[:]:

        try:

            next(task)

        except StopIteration:

            tasks.remove(task)