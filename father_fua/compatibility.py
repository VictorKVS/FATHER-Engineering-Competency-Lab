from __future__ import annotations


class CompatibilityMatrix:
    def __init__(self) -> None:
        self._approved: set[tuple[str, ...]] = set()

    def approve(self, *parts: str) -> None:
        self._approved.add(tuple(parts))

    def is_approved(self, *parts: str) -> bool:
        return tuple(parts) in self._approved
