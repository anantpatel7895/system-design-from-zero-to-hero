"""
examples/scheduler_visualizer/scheduler_renderer.py

Pretty prints the current state of the EventLoop.
"""

from __future__ import annotations

import os
import time


class SchedulerRenderer:

    def __init__(
        self,
        refresh_rate: float = 0.25,
    ):

        self.refresh_rate = refresh_rate

    # =====================================================
    # Public
    # =====================================================

    def render(
        self,
        loop,
    ):

        self.clear()

        print("=" * 70)
        print("MINI ASYNCIO SCHEDULER")
        print("=" * 70)

        self.print_statistics(loop)

        self.print_ready_queue(loop)

        self.print_running_task(loop)

        self.print_sleeping(loop)

        # self.print_recent_events(loop)

        print("=" * 70)

        print(
            f"Iteration : {loop.iteration}"
        )

        print(
            f"Time      : {time.monotonic():.2f}"
        )

        print()

        self.print_ready_queue(loop)

        self.print_running_task(loop)

        self.print_sleeping(loop)

        print("=" * 70)

        time.sleep(
            self.refresh_rate
        )

    # =====================================================
    # READY QUEUE
    # =====================================================

    def print_ready_queue(
        self,
        loop,
    ):

        print("READY QUEUE")
        print("-" * 70)

        if not loop.ready_queue:

            print("(empty)")

        else:

            for task, _ in loop.ready_queue:

                print(task)

        print()

    # =====================================================
    # RUNNING TASK
    # =====================================================

    def print_running_task(
        self,
        loop,
    ):

        print("RUNNING TASK")
        print("-" * 70)

        if loop.running_task is None:

            print("(none)")

        else:

            print(loop.running_task)

        print()

    # =====================================================
    # SLEEPING TASKS
    # =====================================================

    def print_sleeping(
        self,
        loop,
    ):

        print("SLEEPING TASKS")
        print("-" * 70)

        if not loop.sleeping_heap:

            print("(empty)")

        else:

            now = time.monotonic()

            for (
                wake_time,
                _,
                task,
                future,
            ) in loop.sleeping_heap:

                remaining = max(
                    0.0,
                    wake_time - now,
                )

                print(
                    f"{task}"
                )

                print(
                    f"    Wake In : {remaining:.2f}s"
                )

        print()

    # =====================================================
    # Helpers
    # =====================================================

    def clear(self):

        os.system(
            "cls"
            if os.name == "nt"
            else "clear"
        )

    def print_statistics(
        self,
        loop,
    ):

        print("STATISTICS")
        print("-" * 70)

        print(
            f"Ready     : {len(loop.ready_queue)}"
        )

        print(
            f"Sleeping  : {len(loop.sleeping_heap)}"
        )

        print(
            f"Iteration : {loop.iteration}"
        )

        print()