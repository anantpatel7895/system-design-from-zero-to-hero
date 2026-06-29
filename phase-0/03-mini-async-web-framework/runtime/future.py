"""
runtime/future.py

A minimal Future implementation.

A Future represents a value that is not available yet.

It does NOT execute code.
It only stores state and wakes waiting tasks.

runtime/future.py

A minimal Future implementation.

A Future represents a value that
will become available later.
"""

from __future__ import annotations

from typing import Any, Callable


class Future:

    def __init__(self) -> None:

        self._done = False

        self._result: Any = None

        self._callbacks: list[Callable] = []

    # =====================================================
    # State
    # =====================================================

    def done(self) -> bool:

        return self._done

    # =====================================================
    # Result
    # =====================================================

    def result(self) -> Any:

        if not self._done:

            raise RuntimeError(
                "Future has not completed."
            )

        return self._result

    # =====================================================
    # Complete
    # =====================================================

    def set_result(
        self,
        value: Any,
    ) -> None:

        if self._done:

            raise RuntimeError(
                "Future already completed."
            )

        self._done = True

        self._result = value

        self._run_callbacks()

    # =====================================================
    # Callbacks
    # =====================================================

    def add_done_callback(
        self,
        callback: Callable,
    ) -> None:

        if self._done:

            callback(self)

        else:

            self._callbacks.append(
                callback
            )

    def _run_callbacks(self):

        while self._callbacks:

            callback = self._callbacks.pop(0)

            callback(self)

    # =====================================================
    # Await Support
    # =====================================================

    def __await__(self):
        """
        Makes this Future awaitable.

        If not finished:
            suspend coroutine.

        When resumed:
            return the result.
        """

        if not self.done():

            yield self

        return self.result()

    # =====================================================
    # Debug
    # =====================================================

    def __repr__(self):

        state = (
            "FINISHED"
            if self.done()
            else "PENDING"
        )

        return (
            f"<Future state={state}>"
        )