#!/usr/bin/env python3
"""
Cross-platform audio alert service.

Design goals:
- SOLID: Interface for audio alerts with platform-specific implementations
- Separation of Concerns: Isolate audio from business logic
- DRY/KISS: Minimal, dependency-free beeps with graceful fallbacks
"""

from __future__ import annotations

import os
import platform
import sys
import time
from abc import ABC, abstractmethod


class AudioAlertPlayer(ABC):
    """Abstract interface for playing simple beeps."""

    @abstractmethod
    def beep(self, frequency_hz: int, duration_ms: int) -> None:
        """Play a beep with approximate frequency and duration.

        Implementations may approximate frequency/duration when not supported.
        """

    @abstractmethod
    def available(self) -> bool:
        """Return True if audio output is available on this platform."""


class WindowsAudioAlert(AudioAlertPlayer):
    """Windows implementation using winsound."""

    def __init__(self) -> None:
        self._winsound = None
        try:
            import winsound  # type: ignore
            self._winsound = winsound
        except Exception:
            self._winsound = None

    def beep(self, frequency_hz: int, duration_ms: int) -> None:
        if not self._winsound:
            # Fallback to console bell
            _console_bell(duration_ms)
            return
        try:
            self._winsound.Beep(int(frequency_hz), int(duration_ms))
        except Exception:
            _console_bell(duration_ms)

    def available(self) -> bool:
        return self._winsound is not None


class PosixAudioAlert(AudioAlertPlayer):
    """macOS/Linux implementation using console bell or system tools when present.

    Note: Frequency and duration control are limited. We approximate via repeats.
    """

    def __init__(self) -> None:
        # Detect optional tools
        self._has_afplay = _which("afplay") is not None  # macOS
        self._has_paplay = _which("paplay") is not None  # Linux (PulseAudio)

    def beep(self, frequency_hz: int, duration_ms: int) -> None:
        # Keep it dependency-free: prefer console bell approximation
        # For emphasis, play the bell multiple times based on duration
        repeats = max(1, int(duration_ms / 200))
        for _ in range(repeats):
            _console_bell(50)
            time.sleep(0.05)

    def available(self) -> bool:
        # Console bell should generally be available
        return True


class NoOpAudioAlert(AudioAlertPlayer):
    """No-op implementation used as a safe fallback."""

    def beep(self, frequency_hz: int, duration_ms: int) -> None:  # noqa: ARG002
        return

    def available(self) -> bool:
        return False


def get_audio_player() -> AudioAlertPlayer:
    """Factory that returns a platform-appropriate audio player.

    - Windows: WindowsAudioAlert (winsound when available)
    - macOS/Linux: PosixAudioAlert (console bell approximation)
    - Fallback: NoOpAudioAlert
    """
    system = platform.system().lower()
    try:
        if system == "windows":
            return WindowsAudioAlert()
        if system in ("darwin", "linux"):
            return PosixAudioAlert()
        return NoOpAudioAlert()
    except Exception:
        return NoOpAudioAlert()


def _which(cmd: str) -> str | None:
    """Lightweight shutil.which to avoid extra imports."""
    paths = os.environ.get("PATH", "").split(os.pathsep)
    exts = [""]
    if os.name == "nt":
        pathext = os.environ.get("PATHEXT", ".EXE;.BAT;.CMD").split(";")
        exts = pathext
    for path in paths:
        full = os.path.join(path, cmd)
        for ext in exts:
            candidate = full + ext
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return None


def _console_bell(duration_ms: int) -> None:
    """Emit a simple console bell. Duration control is approximated by sleep."""
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(max(0.0, duration_ms / 1000.0))
    except Exception:
        # Last-resort fallback: do nothing
        pass


