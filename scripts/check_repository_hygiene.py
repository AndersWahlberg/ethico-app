"""Fail CI when tracked repository files contain likely private/local material."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

FORBIDDEN_FILENAMES = {
    ".env",
    "local.properties",
    "key.properties",
}
FORBIDDEN_SUFFIXES = {
    ".db",
    ".db3",
    ".sqlite",
    ".sqlite3",
    ".jks",
    ".keystore",
    ".p12",
    ".pfx",
    ".pem",
    ".key",
}

# These rules intentionally target repository hygiene rather than trying to be a
# complete secret scanner. They catch the mistakes most likely in this project.
TEXT_RULES = {
    "Windows home-directory path": re.compile(r"[A-Za-z]:\\Users\\[^\\/\r\n]+", re.IGNORECASE),
    "macOS home-directory path": re.compile(r"/Users/[^/\s]+"),
    "Linux home-directory path": re.compile(r"/home/[^/\s]+"),
    "private-key material": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub classic token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"),
}

# Require an alphabetic character immediately before @ and at the start of the
# domain. This avoids treating generated asset names such as icon@2x.png as email.
EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]*[A-Za-z]@[A-Za-z][A-Za-z0-9.-]*\.[A-Za-z]{2,}\b"
)
ALLOWED_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "users.noreply.github.com",
}
ALLOWED_EMAILS = {
    "noreply@github.com",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def safe_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def main() -> int:
    findings: list[str] = []

    for path in tracked_files():
        relative = path.relative_to(ROOT)
        lower_name = path.name.lower()
        lower_suffix = path.suffix.lower()

        if lower_name in FORBIDDEN_FILENAMES or lower_suffix in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden tracked file: {relative}")

        # Avoid self-matching the literal detection expressions in this checker.
        if path.resolve() == SELF:
            continue

        text = safe_text(path)
        if text is None:
            continue

        for label, pattern in TEXT_RULES.items():
            if pattern.search(text):
                findings.append(f"{label}: {relative}")

        for email in EMAIL_RE.findall(text):
            normalized = email.lower()
            domain = normalized.rsplit("@", 1)[1]
            if normalized not in ALLOWED_EMAILS and domain not in ALLOWED_EMAIL_DOMAINS:
                findings.append(f"email address in tracked text: {relative}")
                break

    if findings:
        print("Repository hygiene check failed:", file=sys.stderr)
        for finding in sorted(set(findings)):
            print(f"- {finding}", file=sys.stderr)
        print(
            "Remove/sanitize personal data or secret material before committing. "
            "Use neutral placeholders for local paths.",
            file=sys.stderr,
        )
        return 1

    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
