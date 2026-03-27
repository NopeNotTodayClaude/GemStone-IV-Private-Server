#!/usr/bin/env python3
"""
Trim an MP3 by MPEG frame boundaries without external dependencies.

This preserves a valid MP3 stream when ffmpeg is unavailable.
"""

from __future__ import annotations

import sys
from pathlib import Path


BITRATES = {
    ("1", 3): [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],
    ("2", 3): [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
}

SAMPLE_RATES = {
    "1": [44100, 48000, 32000, 0],
    "2": [22050, 24000, 16000, 0],
    "2.5": [11025, 12000, 8000, 0],
}


def id3_size(blob: bytes) -> int:
    if len(blob) < 10 or blob[:3] != b"ID3":
        return 0
    flags = blob[5]
    size_bytes = blob[6:10]
    size = (
        ((size_bytes[0] & 0x7F) << 21)
        | ((size_bytes[1] & 0x7F) << 14)
        | ((size_bytes[2] & 0x7F) << 7)
        | (size_bytes[3] & 0x7F)
    )
    footer = 10 if (flags & 0x10) else 0
    return 10 + size + footer


def parse_frame_header(header: bytes):
    if len(header) != 4:
        return None
    value = int.from_bytes(header, "big")
    if ((value >> 21) & 0x7FF) != 0x7FF:
        return None

    version_bits = (value >> 19) & 0x3
    layer_bits = (value >> 17) & 0x3
    bitrate_idx = (value >> 12) & 0xF
    sample_idx = (value >> 10) & 0x3
    padding = (value >> 9) & 0x1

    if layer_bits != 0x1:
        return None  # only layer III supported here

    if version_bits == 0x3:
        version = "1"
        samples_per_frame = 1152
    elif version_bits == 0x2:
        version = "2"
        samples_per_frame = 576
    elif version_bits == 0x0:
        version = "2.5"
        samples_per_frame = 576
    else:
        return None

    bitrate_key = ("1", 3) if version == "1" else ("2", 3)
    bitrate_kbps = BITRATES[bitrate_key][bitrate_idx]
    sample_rate = SAMPLE_RATES[version][sample_idx]
    if bitrate_kbps == 0 or sample_rate == 0:
        return None

    if version == "1":
        frame_len = int((144000 * bitrate_kbps) / sample_rate) + padding
    else:
        frame_len = int((72000 * bitrate_kbps) / sample_rate) + padding

    return frame_len, samples_per_frame, sample_rate


def trim_mp3(src: Path, dst: Path, seconds: float) -> int:
    data = src.read_bytes()
    start = id3_size(data)
    pos = start
    total_seconds = 0.0
    end = start

    while pos + 4 <= len(data):
        header = parse_frame_header(data[pos:pos + 4])
        if not header:
            pos += 1
            continue

        frame_len, samples_per_frame, sample_rate = header
        if frame_len <= 4 or pos + frame_len > len(data):
            break

        end = pos + frame_len
        total_seconds += samples_per_frame / sample_rate
        pos += frame_len
        if total_seconds >= seconds:
            break

    if end <= start:
        raise RuntimeError("Could not locate valid MP3 frames.")

    dst.write_bytes(data[:end])
    return end


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: trim_mp3.py <src.mp3> <dst.mp3> <seconds>")
        return 2

    src = Path(argv[1])
    dst = Path(argv[2])
    seconds = float(argv[3])
    trim_mp3(src, dst, seconds)
    print(dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
