"""ffmpeg / ffprobe wrappers. All media operations shell out to ffmpeg —
no Python media libraries (D-004). Stages write to temp names and rename on
success so a crash never leaves a half-written asset behind.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass


def _find(binary: str) -> str:
    path = shutil.which(binary)
    if path:
        return path
    # winget's per-user shim dir is often missing from non-login shells
    winget = (Path(os.environ.get("LOCALAPPDATA", "")) /
              "Microsoft" / "WinGet" / "Links" / f"{binary}.exe")
    if winget.is_file():
        return str(winget)
    raise MediaError(
        f"{binary} not found on PATH. Install it (Windows: `winget install "
        f"Gyan.FFmpeg`, macOS: `brew install ffmpeg`, Debian: `apt install ffmpeg`).")


def run(binary: str, args: list[str]) -> str:
    exe = _find(binary)
    proc = subprocess.run([exe, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-8:]
        raise MediaError(f"{binary} failed ({proc.returncode}):\n" + "\n".join(tail))
    return proc.stdout


def ffmpeg(args: list[str]) -> None:
    run("ffmpeg", ["-hide_banner", "-y", *args])


def probe_duration(path: Path) -> float:
    out = run("ffprobe", ["-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    try:
        return float(out.strip())
    except ValueError as exc:
        raise MediaError(f"could not read duration of {path}: {out!r}") from exc


def silence_mp3(path: Path, seconds: float) -> None:
    """Synthesize silent narration audio (offline TTS stand-in)."""
    tmp = path.with_suffix(".tmp.mp3")
    ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", f"{seconds:.2f}", "-q:a", "9", str(tmp)])
    tmp.replace(path)


def still_plus_audio_clip(image: Path, audio: Path, out: Path,
                          *, tail_s: float = 0.35) -> float:
    """Render one scene clip: static image + narration audio, with a short
    tail of silence so cuts don't clip the last word. Returns clip duration."""
    duration = probe_duration(audio) + tail_s
    tmp = out.with_suffix(".tmp.mp4")
    ffmpeg([
        "-loop", "1", "-framerate", "30", "-i", str(image),
        "-i", str(audio),
        "-t", f"{duration:.3f}",
        "-af", f"apad=pad_dur={tail_s}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-shortest",
        str(tmp),
    ])
    tmp.replace(out)
    return probe_duration(out)


def concat_clips(clips: list[Path], out: Path) -> None:
    """Lossless concat of uniformly-encoded scene clips."""
    if not clips:
        raise MediaError("no clips to concatenate")
    listing = out.with_suffix(".concat.txt")
    # concat demuxer wants forward slashes and quoted paths
    listing.write_text(
        "".join(f"file '{c.resolve().as_posix()}'\n" for c in clips),
        encoding="utf-8")
    tmp = out.with_suffix(".tmp.mp4")
    try:
        ffmpeg(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
                str(tmp)])
    finally:
        listing.unlink(missing_ok=True)
    tmp.replace(out)


def _srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(entries: list[tuple[float, float, str]], out: Path) -> None:
    """entries: (start_s, end_s, text). Splits long narration into <=90-char
    caption lines spread evenly across the scene's time window."""
    blocks: list[str] = []
    n = 1
    for start, end, text in entries:
        chunks = _split_caption(text)
        span = (end - start) / len(chunks)
        for i, chunk in enumerate(chunks):
            s = start + i * span
            e = start + (i + 1) * span
            blocks.append(f"{n}\n{_srt_time(s)} --> {_srt_time(e)}\n{chunk}\n")
            n += 1
    out.write_text("\n".join(blocks), encoding="utf-8", newline="\n")


def _split_caption(text: str, limit: int = 90) -> list[str]:
    words = text.split()
    chunks, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            chunks.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        chunks.append(cur)
    return chunks or [text]


def mux_subtitles(video: Path, srt: Path, out: Path) -> None:
    """Attach captions as a soft subtitle track (toggleable in players)."""
    tmp = out.with_suffix(".tmp.mp4")
    ffmpeg(["-i", str(video), "-i", str(srt),
            "-c", "copy", "-c:s", "mov_text",
            "-metadata:s:s:0", "language=eng",
            str(tmp)])
    tmp.replace(out)
