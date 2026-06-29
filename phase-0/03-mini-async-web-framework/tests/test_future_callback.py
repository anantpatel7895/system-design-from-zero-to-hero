from runtime.future import Future


def test_callback():

    future = Future()

    value = []

    def callback(f):

        value.append(
            f.result()
        )

    future.add_done_callback(
        callback
    )

    future.set_result(99)

    assert value == [99]