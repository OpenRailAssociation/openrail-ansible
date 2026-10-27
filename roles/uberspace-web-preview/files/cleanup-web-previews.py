#!/usr/bin/env python3
"""Reset preview directories of closed/merged PRs to the placeholder index.html.

Counterpart to the cleanup of OpenRailAssociation/web-deployment-action, which
is not reliable. Runs on the webpreview host and uses only the stdlib.

A preview directory is reset if all of these are true:
  - its name is "<prefix>-pr-<number>" with a prefix from REPOS
  - it contains more than the placeholder index.html
  - the PR is not open on GitHub (closed or merged)

Unknown or unreachable PRs are never touched. Set GITHUB_TOKEN to avoid the
low anonymous API rate limit (60 requests/hour).
"""

import argparse
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

PREVIEW_DIR = "/var/www/virtual/openrail/web-preview.openrailassociation.org"

# Directory prefix (see dir_preview_subdir in the workflows) -> GitHub repository
REPOS = {
    "main": "OpenRailAssociation/website",
    "proj": "OpenRailAssociation/technical-committee",
    "h4r": "OpenRailAssociation/hack4rail-website",
    "osrdui": "OpenRailAssociation/osrd",
    "webdeploy": "OpenRailAssociation/web-deployment-action",
    "nge": "SchweizerischeBundesbahnen/netzgrafik-editor-frontend",
}

# Must match what web-deployment-action writes
PLACEHOLDER = "This PR has been closed or merged. The preview has been removed.\n"

DIR_RE = re.compile(r"^(?P<prefix>[a-z0-9]+)-pr-(?P<number>[0-9]+)$")


def is_placeholder_only(path: Path) -> bool:
    entries = list(path.iterdir())
    if len(entries) != 1 or entries[0].name != "index.html":
        return False
    index = entries[0]
    return (
        index.is_file()
        and not index.is_symlink()
        and index.read_text(errors="replace").strip() == PLACEHOLDER.strip()
    )


def pr_state(repo: str, number: int) -> str:
    """Return 'open', 'closed' or 'merged'. Raises on any API problem."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pulls/{number}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "cleanup-web-previews",
        },
    )
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data["state"] == "open":
        return "open"
    return "merged" if data.get("merged_at") else "closed"


def reset(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    (path / "index.html").write_text(PLACEHOLDER)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dir", default=PREVIEW_DIR, help="preview base directory")
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="only report, change nothing"
    )
    args = parser.parse_args()

    # Flush per line, otherwise output redirected to a file only appears at exit
    sys.stdout.reconfigure(line_buffering=True)

    base = Path(args.dir)
    if not base.is_dir():
        print(f"error: {base} is not a directory", file=sys.stderr)
        return 2

    counts = {"reset": 0, "open": 0, "error": 0}
    for path in sorted(base.iterdir()):
        match = DIR_RE.match(path.name)
        if not match or match["prefix"] not in REPOS:
            continue
        if path.is_symlink() or not path.is_dir() or is_placeholder_only(path):
            continue

        repo, number = REPOS[match["prefix"]], int(match["number"])
        label = f"{path.name} ({repo}#{number})"
        try:
            state = pr_state(repo, number)
        except (urllib.error.URLError, OSError, KeyError, ValueError) as err:
            print(f"ERROR   {label}: cannot determine PR state, skipped: {err}")
            counts["error"] += 1
            continue

        if state == "open":
            print(f"KEEP    {label}: PR is open")
            counts["open"] += 1
            continue

        if args.dry_run:
            print(f"WOULD   reset {label}: PR is {state}")
        else:
            try:
                reset(path)
            except OSError as err:
                print(f"ERROR   {label}: reset failed: {err}")
                counts["error"] += 1
                continue
            print(f"RESET   {label}: PR is {state}")
        counts["reset"] += 1

    verb = "would be reset" if args.dry_run else "reset"
    print(
        f"\nSummary: {counts['reset']} {verb}, {counts['open']} kept (open), "
        f"{counts['error']} errors"
    )
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
