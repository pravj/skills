# Claude Code Skills

A collection of reusable [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills, organized by context.

## Skills Catalog

### Work

| Skill | Description |
|-------|-------------|
| [generate-weekly-update](work/generate-weekly-update/) | Generate weekly update documents in .docx format following established structure and formatting. Parses rough notes, infers owners from prior weeks, handles POPW (Progress on Previous Week) interactively, and generates executive summaries. |
| [transcribe-meeting](work/transcribe-meeting/) | Transcribe audio recordings (meetings, voice memos, etc.) and generate structured notes. Handles long recordings by splitting into chunks. Produces a main notes file with summary, decisions, action items, and per-topic detail files. Supports m4a, mp3, wav, ogg, webm, flac, aac, wma, mp4, mkv. |

### Personal

_Coming soon._

## Installation

### Install a single skill as a plugin

Add this repo as a marketplace, then install any skill individually:

```bash
# Add the marketplace (one-time)
claude plugin marketplaces add https://github.com/pravj/skills

# Install a specific skill
claude plugin install transcribe-meeting
claude plugin install generate-weekly-update
```

Once installed, invoke with:

```
/transcribe-meeting:transcribe-meeting
/generate-weekly-update:generate-weekly-update
```

### Install locally via --plugin-dir (for testing)

```bash
git clone https://github.com/pravj/skills.git
claude --plugin-dir ./skills/work/transcribe-meeting
```

### Manual install (symlink a single skill)

If you prefer not to use plugins, you can symlink a skill directly:

```bash
git clone https://github.com/pravj/skills.git ~/skills

# Link a single skill to your personal skills directory
ln -s ~/skills/work/transcribe-meeting/skills/transcribe-meeting ~/.claude/skills/transcribe-meeting
```

Then invoke as `/transcribe-meeting` (no namespace prefix).

## Repository Structure

Each skill is packaged as a standalone Claude Code plugin:

```
work/
  <skill-name>/
    .claude-plugin/
      plugin.json          # Plugin manifest
    skills/
      <skill-name>/
        SKILL.md            # Skill definition
        ...                 # Supporting scripts/files
```

## Prerequisites

Some skills have their own dependencies:

- **transcribe-meeting**: Requires `ffmpeg`, `ffprobe`, and `openai-whisper` (`pip install openai-whisper`)
- **generate-weekly-update**: Requires `python-docx` (`pip install python-docx`)
