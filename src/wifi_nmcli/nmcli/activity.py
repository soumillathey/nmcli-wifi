"""activity.py — Thread synchronization and watchdog suspension manager for nmcli."""
from __future__ import annotations

import contextlib
import threading
import time
from collections.abc import Iterator

_lock = threading.RLock()
_busy_event = threading.Event()
_suspended_until = 0.0


def suspend_watchdog(duration: float = 10.0) -> None:
    """Suspend watchdog monitoring for at least duration seconds."""
    global _suspended_until
    with _lock:
        target = time.time() + duration
        _suspended_until = max(_suspended_until, target)


def is_watchdog_suspended() -> bool:
    """Return True if watchdog is currently in a suspended cooldown window."""
    with _lock:
        return time.time() < _suspended_until


def is_nmcli_busy() -> bool:
    """Return True if an nmcli command or connection handshake is currently executing."""
    return _busy_event.is_set()


@contextlib.contextmanager
def nmcli_lock(cooldown: float = 0.0) -> Iterator[None]:
    """Serialized context manager ensuring no concurrent nmcli collisions."""
    with _lock:
        _busy_event.set()
        try:
            yield
        finally:
            _busy_event.clear()
            if cooldown > 0:
                suspend_watchdog(cooldown)
