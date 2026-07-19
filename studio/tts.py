"""Narration stage. Speaker protocol keeps TTS provider-independent:

- EdgeSpeaker    — free Microsoft neural voices via the edge-tts package
- SilentSpeaker  — offline stand-in (ffmpeg-synthesized silence, ~150 wpm pacing)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .media import MediaError, silence_mp3


class TTSError(RuntimeError):
    pass


class EdgeSpeaker:
    def __init__(self, voice: str):
        self.voice = voice

    def speak(self, text: str, out: Path) -> None:
        tmp = out.with_suffix(".tmp.mp3")
        # edge-tts ships a CLI entry point; run it via the current interpreter
        # so it works without PATH assumptions.
        proc = subprocess.run(
            [sys.executable, "-m", "edge_tts", "--voice", self.voice,
             "--text", text, "--write-media", str(tmp)],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0 or not tmp.is_file() or tmp.stat().st_size == 0:
            tmp.unlink(missing_ok=True)
            tail = (proc.stderr or "").strip().splitlines()[-5:]
            raise TTSError(
                "edge-tts failed (is `pip install edge-tts` done and the "
                "network up?):\n" + "\n".join(tail))
        tmp.replace(out)


class SilentSpeaker:
    """Deterministic offline narration: silence sized to reading pace."""

    WORDS_PER_SECOND = 2.5

    def speak(self, text: str, out: Path) -> None:
        seconds = max(1.5, len(text.split()) / self.WORDS_PER_SECOND)
        try:
            silence_mp3(out, seconds)
        except MediaError as exc:
            raise TTSError(str(exc)) from exc


def get_speaker(voice: str, offline: bool):
    return SilentSpeaker() if offline else EdgeSpeaker(voice)
