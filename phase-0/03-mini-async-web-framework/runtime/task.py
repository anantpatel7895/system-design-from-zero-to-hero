"""
runtime/task.py

A Task drives a coroutine.

Responsibilities
----------------
- Execute coroutine
- Pause on Future
- Resume when Future completes

runtime/task.py

A Task is a Future that executes a coroutine.

runtime/task.py
"""

from __future__ import annotations

from runtime.future import Future
import itertools

_counter = itertools.count(1)


class Task(Future):
    """
    A Task drives a coroutine.

    It does NOT know about the EventLoop.
    """

    def __init__(
        self,
        coroutine,
    ) -> None:

        super().__init__()

        self.coroutine = coroutine

        # Future currently being awaited
        self.waiting_on: Future | None = None

        self.id = next(_counter)

        self.name = f"Task-{self.id}"

    # =====================================================
    # Execute One Step
    # =====================================================

    def step(
        self,
        value=None,
    ) -> Future | None:

        if self.done():
            return None

        try:

            future = self.coroutine.send(
                value
            )

        except StopIteration as exc:

            self.set_result(
                exc.value
            )

            return None

        if not isinstance(
            future,
            Future,
        ):

            raise RuntimeError(
                "Coroutine must await a Future."
            )

        self.waiting_on = future

        return future

    # =====================================================
    # Debug
    # =====================================================

    def __repr__(self):

        if self.done():

            state = "FINISHED"

        elif self.waiting_on:

            state = "WAITING"

        else:

            state = "READY"

        return (
            f"{self.name}"
            f" [{state}]"
        )