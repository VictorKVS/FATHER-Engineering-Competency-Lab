from __future__ import annotations


class EmergencyStop:
    def __init__(self, engaged: bool = False) -> None:
        self._engaged = engaged

    @property
    def engaged(self) -> bool:
        return self._engaged

    def engage(self) -> None:
        self._engaged = True

    def release(self) -> None:
        self._engaged = False

    def ensure_running(self) -> None:
        if self._engaged:
            raise RuntimeError("FATHER emergency stop is engaged")
