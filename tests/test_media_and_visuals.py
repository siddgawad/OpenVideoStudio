"""Real ffmpeg + Pillow integration tests on synthesized media (no network)."""

from pathlib import Path

import pytest

from studio.media import (concat_clips, mux_subtitles, probe_duration,
                          silence_mp3, still_plus_audio_clip, write_srt)
from studio.model import VisualSpec
from studio.visuals import render_slide, render_thumbnail


def test_silence_and_probe(tmp_path):
    mp3 = tmp_path / "a.mp3"
    silence_mp3(mp3, 2.0)
    assert mp3.stat().st_size > 0
    assert probe_duration(mp3) == pytest.approx(2.0, abs=0.3)


def test_render_slide_and_thumbnail(tmp_path):
    png = tmp_path / "slide.png"
    render_slide(VisualSpec(heading="A Very Long Heading That Should Wrap "
                                    "Or Shrink Without Failing",
                            bullets=["one", "two", "three"]),
                 "dark", png, scene_number=2, total_scenes=6)
    from PIL import Image
    with Image.open(png) as img:
        assert img.size == (1920, 1080)

    thumb = tmp_path / "thumb.png"
    render_thumbnail("Big Thumb Words", "#4f8ef7", "light", thumb)
    with Image.open(thumb) as img:
        assert img.size == (1280, 720)


def test_clip_concat_srt_mux_end_to_end(tmp_path):
    clips = []
    for i in range(2):
        audio = tmp_path / f"s{i}.mp3"
        silence_mp3(audio, 1.5)
        image = tmp_path / f"s{i}.png"
        render_slide(VisualSpec(heading=f"Scene {i}"), "dark", image)
        clip = tmp_path / f"s{i}.mp4"
        dur = still_plus_audio_clip(image, audio, clip)
        assert dur == pytest.approx(1.85, abs=0.4)
        clips.append(clip)

    body = tmp_path / "body.mp4"
    concat_clips(clips, body)
    assert probe_duration(body) == pytest.approx(3.7, abs=0.8)

    srt = tmp_path / "captions.srt"
    write_srt([(0.0, 1.85, "hello world " * 20), (1.85, 3.7, "short")], srt)
    text = srt.read_text()
    assert "-->" in text and text.count("\n\n") >= 1

    final = tmp_path / "final.mp4"
    mux_subtitles(body, srt, final)
    assert final.stat().st_size > 0
    assert probe_duration(final) == pytest.approx(probe_duration(body), abs=0.2)


def test_srt_timestamps_format(tmp_path):
    srt = tmp_path / "x.srt"
    write_srt([(0.0, 65.5, "one line")], srt)
    assert "00:00:00,000 --> 00:01:05,500" in srt.read_text()


def test_concat_requires_clips(tmp_path):
    from studio.media import MediaError
    with pytest.raises(MediaError):
        concat_clips([], tmp_path / "out.mp4")
