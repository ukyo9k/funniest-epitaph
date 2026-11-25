#!/usr/bin/env python3
"""Famous Last Words: The Funniest Epitaph.

Writes a single one-line tombstone epitaph to $MAKEFUN_OUTPUT_DIR/entry.txt
(default /output/entry.txt), then verifies the file round-trips exactly.

The epitaph (63 chars, one line, no stage directions, no explanation):

    My doctor gave me a year to live. Turns out he was an optimist.
"""

import os
import sys

EPITAPH = "My doctor gave me a year to live. Turns out he was an optimist."

MAX_CHARS = 150
MAX_BYTES = 150  # the gate counts UTF-8 characters; bytes stay in step here


class ValidationError(ValueError):
    """One failed epitaph rule, with a short machine-readable code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def validate(text):
    """Check every gate rule for the epitaph, in order of strictness.

    Raises ValidationError with a code on the first failing rule:
    not-a-string, blank, too-long, too-many-bytes, multi-line.
    """
    if not isinstance(text, str):
        raise ValidationError("not-a-string", "epitaph is not a string")
    if not text.strip():
        raise ValidationError("blank", "epitaph is empty or only whitespace")
    if len(text) > MAX_CHARS:
        raise ValidationError(
            "too-long", f"epitaph is {len(text)} chars, max {MAX_CHARS}"
        )
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValidationError(
            "too-many-bytes",
            f"epitaph is {len(text.encode('utf-8'))} UTF-8 bytes, max {MAX_BYTES}",
        )
    if any(ch in text for ch in ("\n", "\r")):
        raise ValidationError("multi-line", "epitaph must be a single line")
    return True


def output_path():
    """Resolve the entry file path from the environment, defaulting to /output."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(out_dir, "entry.txt")


def write_entry(path):
    """Write the epitaph to ``path``, creating the directory if needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(EPITAPH + "\n")
    return path


def verify_entry(path):
    """Read the file back and confirm it is byte-for-byte the epitaph."""
    with open(path, encoding="utf-8") as f:
        written = f.read()
    expected = EPITAPH + "\n"
    if written != expected:
        raise ValidationError(
            "round-trip-mismatch",
            f"file content {written!r} does not match epitaph {expected!r}",
        )
    return written


def main():
    try:
        validate(EPITAPH)
        path = write_entry(output_path())
        verify_entry(path)
    except ValidationError as exc:
        print(f"invalid epitaph [{exc.code}]: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"could not write entry: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {path} ({len(EPITAPH)} chars): {EPITAPH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
