"""
Future Demo
"""

from runtime.future import Future


future = Future()


def callback(f):

    print(
        "Callback executed"
    )

    print(
        "Result:",
        f.result(),
    )


future.add_done_callback(
    callback
)

print(future)

future.set_result(
    "Hello Future"
)

print(future)