---
name: transcribe-meeting
description: Transcribe audio recordings (meetings, voice memos, etc.) and generate structured notes. Use when the user has an audio file and wants a transcript, summary, or topic-wise notes. Handles long recordings by splitting into chunks. Supports m4a, mp3, wav, ogg, webm, flac, aac, wma, mp4, mkv. TRIGGER when: user mentions transcribing audio, meeting recording, voice memo, or generating notes from a recording.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
---

# Transcribe Meeting & Generate Notes

You help users transcribe audio recordings and produce structured, dated notes with per-topic detail files.

## Prerequisites

The user's machine needs:
- `ffmpeg` and `ffprobe` (for splitting audio)
- `python3` with `openai-whisper` installed (`pip install openai-whisper`)

If any are missing, tell the user what to install before proceeding.

## Step 1: Find the audio file

- If the user provided a file path or name, locate it using Glob.
- Supported formats: `.m4a`, `.mp3`, `.wav`, `.ogg`, `.webm`, `.flac`, `.aac`, `.wma`, `.mp4`, `.mkv`
- Confirm the file exists and get its duration:
  ```
  ffprobe -v quiet -show_entries format=duration -of csv=p=0 "<audio_file>"
  ```

## Step 2: Transcribe

Run the transcription script that ships with this skill:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/transcribe.py" "<audio_file>" --output "<output_transcript_path>" --model base --chunk-minutes 10
```

**Model guidance:**
- `base` — fast, good for clear English audio (default)
- `small` — better accuracy, still reasonable speed
- `medium` — good for mixed languages (Hindi+English, etc.) or noisy audio
- `large` — best accuracy, slow on CPU

If the user mentions mixed languages (Hindi, etc.) or poor audio quality, suggest `medium` or `small` model.

**Output naming convention:** Place the transcript next to the audio file as `<audio_basename>-transcript.txt` unless the user specifies otherwise.

## Step 3: Read the transcript and generate notes

After transcription completes, read the full transcript file.

### 3a: Create the main notes file

Create a dated notes file named: `YYYY-MM-DD-<short-descriptive-name>-notes.md`

Use today's date. Derive the short name from the audio file name or the content.

Structure:

```markdown
# Meeting Notes: <descriptive title>
**Date:** YYYY-MM-DD
**Duration:** Xm Ys
**Source:** <audio file name>

## Summary
<3-5 sentence high-level summary of the entire recording>

## Key Decisions
- <bullet list of concrete decisions made, if any>

## Action Items
- [ ] <actionable tasks mentioned, with owner if identifiable>

## Topics Discussed
1. **<Topic 1 name>** (timestamp range) — <1-2 sentence summary>
   → Detailed notes: `<topic-file-name>.md`
2. **<Topic 2 name>** (timestamp range) — <1-2 sentence summary>
   → Detailed notes: `<topic-file-name>.md`
...

## Participants
- <names mentioned in the recording, if identifiable>
```

### 3b: Create per-topic detail files

For each major topic discussed, create a separate file named:
`YYYY-MM-DD-<topic-slug>.md`

Structure:

```markdown
# <Topic Title>
**From:** <parent notes file name>
**Timestamp range:** M:SS - M:SS

## Summary
<2-4 sentence summary of this topic>

## Details
<Detailed notes on this topic, organized logically>
<Include specific numbers, names, decisions mentioned>
<Quote notable statements with timestamps>

## Key Takeaways
- <main points from this topic>
```

**How to identify topics:**
- Look for natural conversation shifts, new agenda items, or subject changes
- A topic should be substantial enough to warrant its own file (at least 2-3 minutes of discussion)
- Minor tangents or brief asides do not need their own file — include them in the main notes

## Step 4: Confirm with the user

After generating all files, list what was created:
- The transcript file
- The main notes file
- Each topic file

Ask if the user wants to:
- Adjust any topic boundaries
- Rename any files
- Add or merge topics
- Re-run with a better Whisper model (if quality was poor)

## Notes on transcript quality

- Whisper `base` model struggles with Hindi and code-switched audio — garbled/repetitive text is a sign of this. Recommend re-running with `medium` or `small`.
- Long silences or background noise can produce hallucinated repetitive text (e.g., the same phrase repeated many times). Flag these sections to the user.
- Proper nouns, technical terms, and acronyms are often mistranscribed. Do your best to infer the correct terms from context when generating notes.
