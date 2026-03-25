#!/usr/bin/env python3
"""
Transcribe audio files by splitting into chunks and using Whisper.
Supports: m4a, mp3, wav, ogg, webm, flac, aac, wma, mp4, mkv

Usage:
    python3 transcribe.py <audio_file> [--output <output_file>] [--model <whisper_model>] [--chunk-minutes <minutes>]

Examples:
    python3 transcribe.py meeting.m4a
    python3 transcribe.py meeting.mp3 --output notes/meeting-transcript.txt
    python3 transcribe.py meeting.m4a --model medium --chunk-minutes 5
"""

import whisper
import subprocess
import os
import sys
import glob
import argparse
import tempfile
import shutil
import time


def get_audio_duration(audio_file):
    """Get duration of audio file in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", audio_file],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def split_audio(audio_file, chunk_dir, chunk_duration):
    """Split audio into chunks using ffmpeg."""
    ext = os.path.splitext(audio_file)[1] or ".m4a"
    # Use aac codec for m4a/mp4, copy for others where possible
    codec_args = ["-c:a", "aac"] if ext in [".m4a", ".mp4"] else ["-c", "copy"]

    subprocess.run(
        ["ffmpeg", "-y", "-i", audio_file,
         "-f", "segment", "-segment_time", str(chunk_duration)]
        + codec_args +
        [os.path.join(chunk_dir, f"chunk_%03d{ext}")],
        check=True, capture_output=True
    )

    chunk_files = sorted(glob.glob(os.path.join(chunk_dir, f"chunk_*{ext}")))
    return chunk_files


def transcribe_chunks(chunk_files, model, chunk_duration):
    """Transcribe each chunk and combine with correct timestamps."""
    all_segments = []
    for i, chunk_file in enumerate(chunk_files):
        print(f"  Transcribing chunk {i+1}/{len(chunk_files)}...", flush=True)
        result = model.transcribe(chunk_file, language=None, verbose=False)
        lang = result.get("language", "unknown")
        print(f"    Detected language: {lang}", flush=True)

        offset = i * chunk_duration
        for seg in result["segments"]:
            start = seg["start"] + offset
            text = seg["text"].strip()
            if text:
                mins = int(start // 60)
                secs = int(start % 60)
                all_segments.append(f"{mins}:{secs:02d}: {text}")

    return all_segments


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("--output", "-o", help="Output transcript file path")
    parser.add_argument("--model", "-m", default="base",
                        help="Whisper model: tiny, base, small, medium, large (default: base)")
    parser.add_argument("--chunk-minutes", type=int, default=10,
                        help="Chunk duration in minutes (default: 10)")
    args = parser.parse_args()

    audio_file = os.path.abspath(args.audio_file)
    if not os.path.exists(audio_file):
        print(f"Error: File not found: {audio_file}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_file = os.path.abspath(args.output)
    else:
        base = os.path.splitext(audio_file)[0]
        output_file = f"{base}-transcript.txt"

    chunk_duration = args.chunk_minutes * 60

    # Get duration
    duration = get_audio_duration(audio_file)
    duration_mins = int(duration // 60)
    duration_secs = int(duration % 60)
    num_chunks = max(1, int(duration // chunk_duration) + (1 if duration % chunk_duration > 0 else 0))

    print(f"Audio: {os.path.basename(audio_file)} ({duration_mins}m {duration_secs}s)")
    print(f"Model: {args.model} | Chunks: {num_chunks} x {args.chunk_minutes}min")

    # Create temp directory for chunks
    chunk_dir = tempfile.mkdtemp(prefix="whisper_chunks_")

    try:
        # Split
        print("Splitting audio...", flush=True)
        chunk_files = split_audio(audio_file, chunk_dir, chunk_duration)
        print(f"  Created {len(chunk_files)} chunks", flush=True)

        # Load model
        print(f"Loading Whisper model '{args.model}'...", flush=True)
        start_time = time.time()
        model = whisper.load_model(args.model)
        print(f"  Model loaded in {time.time() - start_time:.1f}s", flush=True)

        # Transcribe
        print("Transcribing...", flush=True)
        start_time = time.time()
        segments = transcribe_chunks(chunk_files, model, chunk_duration)
        elapsed = time.time() - start_time
        print(f"  Transcribed in {elapsed:.1f}s ({elapsed/duration:.1f}x realtime)", flush=True)

        # Write output
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w") as f:
            f.write("\n".join(segments))
            f.write("\n")

        print(f"\nTranscript saved: {output_file}")
        print(f"Lines: {len(segments)}")

    finally:
        # Cleanup temp chunks
        shutil.rmtree(chunk_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
