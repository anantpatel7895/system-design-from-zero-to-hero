from runtime.future import Future


def callback(future):

    print("Callback Fired")

    print(
        future.result()
    )


future = Future()

future.add_done_callback(
    callback
)

print(future)

future.set_result(
    "Hello World"
)

print(future)