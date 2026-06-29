from runtime.event_loop import EventLoop


def test_call_soon():

    loop = EventLoop()

    output = []

    class DummyTask:

        def step(self, value=None):

            output.append(
                value
            )

    loop.call_soon(
        DummyTask(),
        10,
    )

    loop._run_ready_tasks()

    assert output == [10]