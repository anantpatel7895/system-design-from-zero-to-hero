from runtime.future import Future


def test_future():

    future = Future()

    assert future.done() is False

    future.set_result(123)

    assert future.done() is True

    assert future.result() == 123