"""
future.py

A Future represents a value that will become available later.

Responsibilities:
- Store result
- Store exception
- Track completion state
- Notify callbacks
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional


class Future:
    """
    A minimal implementation inspired by asyncio.Future.
    """

    def __init__(self) -> None:
        self._done: bool = False
        self._result: Any = None
        self._exception: Optional[Exception] = None
        self._callbacks: List[Callable[[Future], None]] = []

    # --------------------------------------------------
    # State
    # --------------------------------------------------

    def done(self) -> bool:
        """
        Return True if the Future has completed.
        """
        return self._done

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    def result(self) -> Any:
        """
        Return the result.

        Raises:
            RuntimeError
                if Future is not complete.

            Exception
                if Future completed with an exception.
        """

        if not self._done:
            raise RuntimeError(
                "Future is not completed."
            )

        if self._exception is not None:
            raise self._exception

        return self._result

    # --------------------------------------------------
    # Complete Successfully
    # --------------------------------------------------

    def set_result(self, value: Any) -> None:
        """
        Complete the Future successfully.
        """

        if self._done:
            raise RuntimeError(
                "Future already completed."
            )

        self._done = True
        self._result = value

        self._run_callbacks()

    # --------------------------------------------------
    # Complete With Error
    # --------------------------------------------------

    def set_exception(
        self,
        exc: Exception,
    ) -> None:

        if self._done:
            raise RuntimeError(
                "Future already completed."
            )

        self._done = True
        self._exception = exc

        self._run_callbacks()

    # --------------------------------------------------
    # Callbacks
    # --------------------------------------------------

    def add_done_callback(
        self,
        callback: Callable[[Future], None],
    ) -> None:
        """
        Register a callback.

        If the Future is already completed,
        execute the callback immediately.
        """

        if self._done:
            callback(self)
            return

        self._callbacks.append(callback)

    def _run_callbacks(self) -> None:
        """
        Execute all registered callbacks.
        """

        while self._callbacks:

            callback = self._callbacks.pop(0)

            callback(self)

    # --------------------------------------------------
    # Debug
    # --------------------------------------------------

    def __repr__(self) -> str:

        if self._done:

            if self._exception is not None:
                return (
                    f"<Future "
                    f"done exception={self._exception}>"
                )

            return (
                f"<Future "
                f"done result={self._result!r}>"
            )

        return "<Future pending>"