#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SessionStart hook: compact CURRENT.md brief for Claude and Codex.
# The template keeps no project-specific paths or runtime state.

import io
import json
import os
import re
import stat
import subprocess
import sys


SOURCE = "wiki/journal/CURRENT.md"
BRIEF_CAP = 4096
BRIEF_SECTIONS = (
    ("GOAL", "\ubaa9\ud45c", 1),
    ("STATE", "\ud604\uc7ac \uc0c1\ud0dc", 2),
    ("OPEN", "\ubbf8\ud574\uacb0 \uc0ac\ud56d", 2),
    ("NEXT", "\ub2e4\uc74c \uc791\uc5c5", 3),
)
EMPTY = "(\uc5c6\uc74c)"


def _git(workspace, args):
    try:
        result = subprocess.run(
            ["git", "-C", workspace, "--no-optional-locks"] + args,
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None


def _journal_newer(workspace, current_rel, journal_rel):
    dirty = _git(workspace, ["status", "--porcelain", "--", current_rel])
    if dirty is None:
        return "unavailable"
    if dirty.strip():
        return "not-applicable"
    current_time = _git(workspace, ["log", "-1", "--format=%ct", "--", current_rel])
    journal_time = _git(workspace, ["log", "-1", "--format=%ct", "--", journal_rel])
    if current_time is None or journal_time is None:
        return "unavailable"
    if not current_time.strip() or not journal_time.strip():
        return "not-applicable"
    try:
        return "newer" if int(journal_time.strip()) > int(current_time.strip()) else "normal"
    except ValueError:
        return "unavailable"


def build_brief(raw, latest=None, warnings=()):
    lines = ["SOURCE: " + SOURCE + " (full source fallback)"]
    if latest:
        lines.append("JOURNAL: " + latest)
    else:
        lines.append("JOURNAL: unavailable; inspect wiki/journal/")
    lines.extend(warnings)
    omission = "OMITTED: read CURRENT.md in full before relying on missing decisions, verification, or approval limits."
    if raw is None:
        return "\n".join(lines + ["UNAVAILABLE: read " + SOURCE + " and the latest journal manually."])
    headings = [BRIEF_SECTIONS[0][1], BRIEF_SECTIONS[1][1],
                "\uc8fc\uc694 \uacb0\uc815", "\uac80\uc99d \uacb0\uacfc",
                BRIEF_SECTIONS[2][1], BRIEF_SECTIONS[3][1]]
    sections = {}
    active = None
    for line in raw.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            active = match.group(1)
            if active not in headings or active in sections:
                return "\n".join(lines + ["INVALID STRUCTURE: read " + SOURCE + " in full."])
            sections[active] = []
        elif active and line.strip():
            if re.match(r"^\s+(?:[-*]|\d+[.)])\s+", line):
                return "\n".join(lines + ["INVALID STRUCTURE: nested list requires reading " + SOURCE + " in full."])
            item = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(.+)$", line)
            if item:
                sections[active].append(item.group(1).strip())
            elif sections[active]:
                sections[active][-1] += " " + line.strip()
            else:
                sections[active].append(line.strip())
    if set(sections) != set(headings):
        return "\n".join(lines + ["INVALID STRUCTURE: read " + SOURCE + " in full."])
    omitted = bool(sections[headings[2]] or sections[headings[3]])
    for label, heading, limit in BRIEF_SECTIONS:
        items = sections[heading]
        omitted |= len(items) > limit
        for item in items[:limit] or [EMPTY]:
            candidate = label + ": " + item
            if len("\n".join(lines + [candidate, omission]).encode("utf-8")) <= BRIEF_CAP:
                lines.append(candidate)
            else:
                omitted = True
    if omitted:
        lines.append(omission)
    return "\n".join(lines)


def _is_kind(path, predicate):
    try:
        return predicate(os.stat(path).st_mode)
    except FileNotFoundError:
        return False


def _latest_journal(workspace):
    root = os.path.join(workspace, "wiki", "journal")
    try:
        names = os.listdir(root)
    except FileNotFoundError:
        return None
    months = sorted(
        name for name in names
        if re.fullmatch(r"\d{4}-\d{2}", name) and _is_kind(os.path.join(root, name), stat.S_ISDIR)
    )
    for month in reversed(months):
        month_dir = os.path.join(root, month)
        revisions = sorted(
            name for name in os.listdir(month_dir)
            if re.fullmatch(r"r\d{3}-[a-z0-9-]+\.md", name)
            and _is_kind(os.path.join(month_dir, name), stat.S_ISREG)
        )
        if revisions:
            return "wiki/journal/" + month + "/" + revisions[-1]
    return None


def main():
    workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    current_path = os.path.join(workspace, "wiki", "journal", "CURRENT.md")
    try:
        with io.open(current_path, encoding="utf-8") as stream:
            raw = stream.read()
    except (OSError, UnicodeError):
        raw = None
    try:
        latest = _latest_journal(workspace)
        journal_unavailable = False
    except (OSError, UnicodeError):
        latest = None
        journal_unavailable = True
    warnings = []
    if journal_unavailable:
        warnings.append("[JOURNAL] SOURCE UNAVAILABLE: read wiki/journal/ manually.")
    if raw is not None:
        if len(raw.encode("utf-8")) > 10 * 1024:
            warnings.append("[current-guard] WARN: CURRENT.md exceeds 10KB; keep the brief concise.")
        if latest:
            freshness = _journal_newer(workspace, SOURCE, latest)
            if freshness == "newer":
                warnings.append("[current-guard] WARN: journal changed after CURRENT.md; synchronize state.")
            elif freshness == "unavailable":
                warnings.append("[current-guard] SOURCE UNAVAILABLE: manually read CURRENT.md and latest journal for freshness.")
        if len(re.findall(r"\(\uc5c6\uc74c(?:\)|\])", raw)) >= 5:
            warnings.append("[current-guard] WARN: CURRENT.md is an unused starter skeleton; write real work state before relying on it.")
    return emit_context(build_brief(raw, latest, warnings))


def emit_context(context):
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    # Force UTF-8 on Windows pipes so Korean stays intact without JSON escape bloat.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="strict", newline="\n")
    except Exception:
        pass
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(emit_context("SOURCE: " + SOURCE + "\nUNAVAILABLE: read CURRENT.md and the latest journal manually."))
