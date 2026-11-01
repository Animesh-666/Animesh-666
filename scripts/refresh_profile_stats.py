#!/usr/bin/env python3
"""Generate self-hosted GitHub profile statistic SVGs.

Uses only Python's standard library. In GitHub Actions, the built-in
GITHUB_TOKEN is passed through GH_TOKEN; no personal token is required.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USERNAME = "Animesh-666"
OUT = Path(__file__).resolve().parents[1] / "assets"
TODAY = datetime.now(timezone.utc).strftime("%d %b %Y")
PALETTE = ["#50f1b9", "#7fb9ff", "#f8d577", "#a991ff", "#f58dba"]


def fetch_public_repositories() -> list[dict]:
    token = os.environ.get("GH_TOKEN", "")
    repos = []
    for page in range(1, 21):
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?type=owner&per_page=100&page={page}"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Animesh-666-Profile-Cards",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(url, headers=headers)
        with urlopen(request, timeout=25) as response:
            result = json.load(response)
        if not isinstance(result, list):
            raise ValueError("GitHub repos API did not return a list")
        repos.extend(r for r in result if not r.get("private", False))
        if len(result) < 100:
            break
    return repos


def base(inner: str, title: str, subtitle: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="206" viewBox="0 0 520 206" role="img" aria-label="{escape(title)}: {escape(subtitle)}">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0b1a1d"/><stop offset="1" stop-color="#101c21"/></linearGradient></defs>
  <rect x="1" y="1" width="518" height="204" rx="17" fill="url(#bg)" stroke="#285346" stroke-width="1.5"/>
  <path d="M26 24H58" stroke="#50f1b9" stroke-width="3" stroke-linecap="round"/>
  <text x="26" y="55" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="750" fill="#e7fcf4">{escape(title)}</text>
  <text x="26" y="74" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="700" letter-spacing="1.2" fill="#69b59e">{escape(subtitle)}</text>
  {inner}
</svg>'''


def generate_stats(repos: list[dict], snapshot: bool) -> str:
    count = len(repos)
    stars = sum(int(r.get("stargazers_count") or 0) for r in repos)
    forks = sum(int(r.get("forks_count") or 0) for r in repos)
    suffix = "+" if snapshot else ""
    meta = "VERIFIED REPOSITORY SNAPSHOT" if snapshot else "CURRENT PUBLIC GITHUB DATA"
    foot = (
        "Verified subset — run GitHub Actions for full totals"
        if snapshot else f"Updated {TODAY} automatically from GitHub"
    )
    cards = [("REPOSITORIES", f"{count}{suffix}", "#50f1b9"),
             ("TOTAL STARS", f"{stars}{suffix}", "#f8d577"),
             ("TOTAL FORKS", f"{forks}{suffix}", "#7fb9ff")]
    inner = ''
    for index, (label, value, color) in enumerate(cards):
        x = 26 + index * 162
        inner += f'''
  <rect x="{x}" y="91" width="150" height="81" rx="11" fill="#132b2a" stroke="#285346" stroke-opacity=".75"/>
  <text x="{x+13}" y="112" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="700" letter-spacing=".75" fill="#9fb9b1">{label}</text>
  <text x="{x+13}" y="155" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="750" fill="{color}">{escape(value)}</text>'''
    inner += f'<text x="26" y="194" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#8ca8a0">{escape(foot)}</text>'
    return base(inner, "GitHub Stats", meta)


def generate_languages(repos: list[dict], snapshot: bool) -> str:
    languages = Counter(r.get("language") for r in repos if r.get("language"))
    total = sum(languages.values())
    foot = ("Verified subset — run workflow to update" if snapshot else f"Updated {TODAY} • primary language per repo")
    title = "Primary Languages"
    subtitle = "VERIFIED REPO SNAPSHOT" if snapshot else "PUBLIC REPOSITORY LANGUAGE MIX"
    inner = ''
    selected = languages.most_common(4)
    if not selected:
        inner += '<text x="26" y="124" font-family="Arial, Helvetica, sans-serif" font-size="17" fill="#b8cec6">No public repo language data yet</text>'
    for index, (name, value) in enumerate(selected):
        y = 92 + index * 25
        pct = value / total if total else 0
        length = max(8, int(pct * 230))
        color = PALETTE[index % len(PALETTE)]
        inner += f'''
  <text x="26" y="{y+11}" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="600" fill="#d6eee6">{escape(str(name))}</text>
  <rect x="173" y="{y+1}" width="240" height="10" rx="5" fill="#17312e"/>
  <rect x="173" y="{y+1}" width="{length}" height="10" rx="5" fill="{color}"/>
  <text x="476" y="{y+11}" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="{color}">{value} repo{'s' if value != 1 else ''}</text>'''
    inner += f'<text x="26" y="194" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#8ca8a0">{escape(foot)}</text>'
    return base(inner, title, subtitle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Make explicitly labelled snapshot from six verified repositories")
    args = parser.parse_args()
    if args.seed:
        # Verified repository metadata, used only to ship an honest, never-blank
        # design before the first successful GitHub Actions run.
        repos = [
            {"name": "VOLTLEDGER", "language": "Java", "stargazers_count": 1, "forks_count": 0},
            {"name": "FOODROUTE", "language": "TypeScript", "stargazers_count": 1, "forks_count": 0},
            {"name": "Animesh-Cosmic-Portfolio", "language": None, "stargazers_count": 1, "forks_count": 0},
            {"name": "teamtrack", "language": "JavaScript", "stargazers_count": 1, "forks_count": 0},
            {"name": "College-Course-Scheduling-System", "language": "HTML", "stargazers_count": 0, "forks_count": 0},
            {"name": "Animesh-666", "language": None, "stargazers_count": 0, "forks_count": 0},
        ]
    else:
        repos = fetch_public_repositories()
        if not repos:
            raise RuntimeError("No repositories returned; leaving existing cards untouched")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "github-stats.svg").write_text(generate_stats(repos, args.seed), encoding="utf-8")
    (OUT / "github-languages.svg").write_text(generate_languages(repos, args.seed), encoding="utf-8")
    print(f"Generated two SVGs from {len(repos)} {'verified' if args.seed else 'public'} repositories")


if __name__ == "__main__":
    try:
        main()
    except (HTTPError, URLError, OSError, ValueError, RuntimeError) as exc:
        print(f"Cannot refresh GitHub profile cards: {exc}", file=sys.stderr)
        sys.exit(1)
