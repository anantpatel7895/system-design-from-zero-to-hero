"""
runtime/context.py

Represents one HTTP request execution context.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class Context:

    def __init__(
        self,
        connection,
    ) -> None:

        self.id = str(
            uuid.uuid4()
        )

        self.started_at = time.time()

        self.connection = connection

        self.request = None

        self.response = None

        self.attributes: dict[str, Any] = {}

        self.state = {}

    # ----------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.attributes[key] = value

    # ----------------------------------------

    def get(
        self,
        key: str,
        default=None,
    ):

        return self.attributes.get(
            key,
            default,
        )

    # ----------------------------------------

    @property
    def duration(self):

        return (
            time.time()
            - self.started_at
        )

    # ----------------------------------------

    def __repr__(self):

        return (
            f"<Context "
            f"id={self.id[:8]} "
            f"duration={self.duration:.3f}s>"
        )