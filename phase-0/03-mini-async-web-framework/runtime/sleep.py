"""
runtime/sleep.py

SleepFuture implementation.

Represents a Future that becomes ready
after a specified delay.
"""

from __future__ import annotations

import time

from runtime.future import Future


class SleepFuture(Future):
    """
    Future that completes after a delay.
    """

    def __init__(
        self,
        delay: float,
    ) -> None:

        super().__init__()

        self.delay = delay

        self.wake_time = (
            time.monotonic() + delay
        )

    def ready(self) -> bool:
        """
        Returns True when it's time
        to wake this future.
        """

        return (
            time.monotonic()
            >= self.wake_time
        )

    def remaining(self) -> float:
        """
        Seconds remaining before wakeup.
        """

        remaining = (
            self.wake_time
            - time.monotonic()
        )

        return max(
            0.0,
            remaining,
        )

    def __repr__(self):

        state = (
            "FINISHED"
            if self.done()
            else "PENDING"
        )

        return (
            f"<SleepFuture "
            f"delay={self.delay}s "
            f"remaining={self.remaining():.2f}s "
            f"state={state}>"
        )


def sleep(
    seconds: float,
) -> SleepFuture:
    """
    Async sleep.

    Usage:

        await sleep(2)
    """

    return SleepFuture(
        seconds
    )