"""
runtime/event_loop.py

A minimal event loop built on Python's selectors module.

Responsibilities
----------------
- Register sockets
- Unregister sockets
- Wait for socket readiness
- Invoke callbacks

This version only schedules socket events.

Future/Task support will be added later.

runtime/event_loop.py

Unified Event Loop

Responsibilities
----------------
- Socket events
- Task scheduling
- Future wakeups

runtime/event_loop.py

Mini Async Runtime Scheduler

runtime/event_loop.py

Mini Async Runtime

Responsibilities
----------------
- Schedule ready tasks
- Manage sleeping tasks
- Process socket events
"""

from __future__ import annotations

import heapq
import itertools
import selectors
import socket
import time
from collections import deque

from runtime.sleep import SleepFuture
from runtime.task import Task


class EventLoop:
    def __init__(self):

        # =====================================================
        # Socket Selector
        # =====================================================

        self.selector = selectors.DefaultSelector()

        # =====================================================
        # Scheduler
        # =====================================================

        # Tasks ready to execute
        self.ready_queue = deque()

        # Sleeping tasks
        #
        # Heap Entry:
        # (
        #     wake_time,
        #     sequence,
        #     task,
        #     future,
        # )
        #
        self.sleeping_heap = []

        # Sequence counter used when wake_time is equal
        self._sequence = itertools.count()

        # Currently executing task
        self.running_task = None

        # Debug
        self.iteration = 0

        self.running = False

        self.iteration_callbacks = []

    # =====================================================
    # Socket Registration
    # =====================================================

    def register(
        self,
        sock: socket.socket,
        events: int,
        callback,
    ):

        self.selector.register(
            sock,
            events,
            callback,
        )

    def unregister(
        self,
        sock,
    ):

        try:

            self.selector.unregister(
                sock
            )

        except Exception:
            pass

    # =====================================================
    # Task API
    # =====================================================

    def create_task(
        self,
        coroutine,
    ) -> Task:

        task = Task(
            coroutine
        )

        self.call_soon(task)

        return task

    def call_soon(
        self,
        task: Task,
        value=None,
    ):

        self.ready_queue.append(
            (
                task,
                value,
            )
        )

    # =====================================================
    # Sleeping Tasks
    # =====================================================

    def _sleep_task(
        self,
        task: Task,
        future: SleepFuture,
    ):

        heapq.heappush(

            self.sleeping_heap,

            (
                future.wake_time,
                next(self._sequence),
                task,
                future,
            ),

        )

    def _wake_sleeping_tasks(self):

        now = time.monotonic()

        while self.sleeping_heap:

            (
                wake_time,
                _,
                task,
                future,
            ) = self.sleeping_heap[0]

            #
            # Earliest timer hasn't expired yet.
            #

            if wake_time > now:

                break

            #
            # Remove from heap
            #

            heapq.heappop(
                self.sleeping_heap
            )

            #
            # Complete Future
            #

            future.set_result(None)

            #
            # Schedule task again
            #

            self.call_soon(
                task,
                future.result(),
            )

    # =====================================================
    # Execute Ready Tasks
    # =====================================================

    def _run_ready_tasks(self):

        while self.ready_queue:

            task, value = (
                self.ready_queue.popleft()
            )

            self.running_task = task

            future = task.step(
                value
            )

            self.running_task = None

            #
            # Task finished
            #

            if future is None:

                continue

            #
            # Sleep Future
            #

            if isinstance(
                future,
                SleepFuture,
            ):

                self._sleep_task(
                    task,
                    future,
                )

                continue

            #
            # Generic Future
            #

            future.add_done_callback(

                lambda f, t=task: self.call_soon(
                    t,
                    f.result(),
                )

            )

    # =====================================================
    # Socket Events
    # =====================================================

    def _run_socket_events(self):

        events = self.selector.select(
            timeout=0
        )

        for key, mask in events:

            callback = key.data

            callback(
                key.fileobj,
                mask,
            )

    # =====================================================
    # Observers
    # =====================================================

    def on_iteration(
        self,
        callback,
    ):
        """
        Register a callback that is invoked
        once every scheduler iteration.

        Example:

            loop.on_iteration(renderer.render)
        """

        self.iteration_callbacks.append(
            callback
        )

    # =====================================================
    # Main Loop
    # =====================================================

    def run_forever(self):

        self.running = True

        while self.running:

            self.iteration += 1

            #
            # Notify observers
            #

            for callback in self.iteration_callbacks:

                callback(self)

            #
            # Wake sleeping tasks
            #

            self._wake_sleeping_tasks()

            #
            # Execute ready tasks
            #

            self._run_ready_tasks()

            #
            # Socket Events
            #

            self._run_socket_events()

            #
            # Automatically stop
            #

            if (
                not self.ready_queue
                and not self.sleeping_heap
            ):

                self.stop()

            #
            # Prevent CPU spinning
            #

            time.sleep(0.01)

    # =====================================================
    # Stop
    # =====================================================

    def stop(self):

        self.running = False

    # =====================================================
    # Cleanup
    # =====================================================

    def close(self):

        self.selector.close()

    # =====================================================
    # Debug Helpers
    # =====================================================

    @property
    def ready_count(self):

        return len(
            self.ready_queue
        )

    @property
    def sleeping_count(self):

        return len(
            self.sleeping_heap
        )

    def __repr__(self):

        return (
            f"<EventLoop "
            f"iteration={self.iteration} "
            f"ready={self.ready_count} "
            f"sleeping={self.sleeping_count}>"
        )
    
