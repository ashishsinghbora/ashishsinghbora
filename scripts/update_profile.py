#!/usr/bin/env python3
"""
Automated profile updater for Ashish Singh Bora's GitHub profile.
Fetches GitHub API data, updates marked README sections, and generates
a self-contained, theme-adaptive metrics SVG dashboard.
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

README_PATH = "Readme.md"
SVG_PATH = "assets/profile-metrics.svg"
DEFAULT_USER = "ashishsinghbora"


def get_target_username() -> str:
    """Determine the GitHub username dynamically from environment or git remote."""
    env_owner = os.environ.get("GITHUB_REPOSITORY_OWNER")
    if env_owner and env_owner.strip():
        return env_owner.strip()

    env_repo = os.environ.get("GITHUB_REPOSITORY")
    if env_repo and "/" in env_repo:
        return env_repo.split("/")[0].strip()

    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        match = re.search(r"github\.com[:/]([^/]+)/", remote_url)
        if match:
            return match.group(1).strip()
    except Exception:
        pass

    return DEFAULT_USER


def fetch_github_api(path: str, token: str | None = None) -> Any:
    """Query GitHub REST API with authorization and strict timeout."""
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ashishsinghbora-profile-updater",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=15) as response:
            return json.load(response)
    except HTTPError as e:
        sys.stderr.write(f"GitHub API HTTP error {e.code} on {path}\n")
        raise
    except URLError as e:
        sys.stderr.write(f"GitHub API network error: {e.reason} on {path}\n")
        raise


def replace_section(content: str, start_marker: str, end_marker: str, new_body: str) -> str:
    """Safely replace content between markers while preserving exact markers."""
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    if not pattern.search(content):
        raise ValueError(f"Marker pair '{start_marker}' ... '{end_marker}' not found in target file.")

    replacement = f"{start_marker}\n{new_body.strip()}\n{end_marker}"
    return pattern.sub(replacement, content, count=1)


def generate_metrics_svg(
    user_data: dict[str, Any],
    total_stars: int,
    sync_date: str,
    output_path: str,
) -> None:
    """Generate a clean, high-DPI terminal-styled SVG metrics telemetry widget."""
    public_repos = str(user_data.get("public_repos", 0))
    followers = str(user_data.get("followers", 0))
    following = str(user_data.get("following", 0))
    stars_str = f"{total_stars}+"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 145" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
  <defs>
    <style>
      .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1.2px; }}
      .titlebar {{ fill: #161b22; }}
      .header-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; fill: #8b949e; font-weight: 500; }}
      .metric-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; fill: #8b949e; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }}
      .metric-val {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 22px; fill: #58a6ff; font-weight: 700; }}
      .metric-sub {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 10px; fill: #3fb950; font-weight: 500; }}
      .accent-green {{ fill: #3fb950; }}
      .accent-blue {{ fill: #58a6ff; }}
      .accent-purple {{ fill: #bc8cff; }}
      .accent-orange {{ fill: #f0883e; }}
      .divider {{ stroke: #21262d; stroke-width: 1px; }}
    </style>
  </defs>

  <!-- Background Box -->
  <rect class="bg" x="1" y="1" width="838" height="143" rx="8" />

  <!-- Terminal Top Bar -->
  <path class="titlebar" d="M 1 9 C 1 4.5 4.5 1 9 1 L 831 1 C 835.5 1 839 4.5 839 9 L 839 30 L 1 30 Z" />
  <line x1="1" y1="30" x2="839" y2="30" stroke="#30363d" stroke-width="1" />

  <!-- Terminal Window Controls -->
  <circle cx="16" cy="15" r="4.5" fill="#ff5f56" />
  <circle cx="30" cy="15" r="4.5" fill="#ffbd2e" />
  <circle cx="44" cy="15" r="4.5" fill="#27c93f" />

  <!-- Terminal Title & Status -->
  <text class="header-text" x="62" y="19">ashish@archlinux:~/telemetry --sys-stats</text>
  <circle cx="740" cy="15" r="3.5" fill="#3fb950" />
  <text class="header-text" x="750" y="19" fill="#3fb950">LIVE SYNC · {html.escape(sync_date)}</text>

  <!-- Metric 1: Public Repositories -->
  <g transform="translate(30, 48)">
    <text class="metric-label" x="0" y="20">Repositories</text>
    <text class="metric-val" x="0" y="52">{html.escape(public_repos)}</text>
    <text class="metric-sub accent-blue" x="0" y="70">● Public Projects</text>
  </g>

  <line class="divider" x1="220" y1="45" x2="220" y2="130" />

  <!-- Metric 2: Earned Stars -->
  <g transform="translate(245, 48)">
    <text class="metric-label" x="0" y="20">Ecosystem Stars</text>
    <text class="metric-val accent-purple" x="0" y="52">{html.escape(stars_str)}</text>
    <text class="metric-sub accent-purple" x="0" y="70">★ Public &amp; Network</text>
  </g>

  <line class="divider" x1="435" y1="45" x2="435" y2="130" />

  <!-- Metric 3: Community Followers -->
  <g transform="translate(460, 48)">
    <text class="metric-label" x="0" y="20">Network Followers</text>
    <text class="metric-val accent-green" x="0" y="52">{html.escape(followers)}</text>
    <text class="metric-sub accent-green" x="0" y="70">↑ Following {html.escape(following)}</text>
  </g>

  <line class="divider" x1="645" y1="45" x2="645" y2="130" />

  <!-- Metric 4: Platform Focus -->
  <g transform="translate(670, 48)">
    <text class="metric-label" x="0" y="20">Primary Stack</text>
    <text class="metric-val accent-orange" x="0" y="52">Linux/AI</text>
    <text class="metric-sub accent-orange" x="0" y="70">Arch · Python · C++</text>
  </g>
</svg>
"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content.strip() + "\n")


def build_activity_section(repos: list[dict[str, Any]], sync_date: str) -> str:
    """Format top recently updated repositories excluding forks and archived repos."""
    # Filter out forks, archived repos, and the profile repository itself
    active_repos: list[dict[str, Any]] = []
    for r in repos:
        if not isinstance(r, dict):
            continue
        if r.get("fork", False) or r.get("archived", False):
            continue
        name = r.get("name", "")
        if name.lower() in ("ashishsinghbora", ".github"):
            continue
        active_repos.append(r)

    # Sort descending by updated_at
    active_repos.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)

    lines: list[str] = [
        "| Repository | Description | Language | Stars | Last Pushed |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ]

    for repo in active_repos[:6]:
        name = repo.get("name", "unknown")
        url = repo.get("html_url", f"https://github.com/ashishsinghbora/{name}")
        raw_desc = (repo.get("description") or "—").strip()
        # Clean markdown characters and truncate cleanly
        desc = raw_desc.replace("|", "\\|").replace("\n", " ")
        if len(desc) > 95:
            desc = desc[:92].rstrip() + "..."

        lang = repo.get("language") or "—"
        stars = repo.get("stargazers_count", 0)
        raw_updated = repo.get("updated_at") or repo.get("pushed_at") or ""
        updated_fmt = raw_updated[:10] if len(raw_updated) >= 10 else "—"

        lines.append(f"| **[{name}]({url})** | {desc} | `{lang}` | ★ {stars} | `{updated_fmt}` |")

    lines.append("")
    lines.append(f"> ⚡ *Automated live sync executed on `{sync_date}` via GitHub Actions.*")
    return "\n".join(lines)


def build_profile_metrics_section(user_data: dict[str, Any], total_stars: int, sync_date: str) -> str:
    """Build markdown table for profile metrics."""
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    following = user_data.get("following", 0)
    public_gists = user_data.get("public_gists", 0)

    rows = [
        "| Metric | Specification | Status |",
        "| :--- | :--- | :---: |",
        f"| **Public Repositories** | Active open source repositories | `{public_repos}` |",
        f"| **Total Stars Earned** | Public repositories & ecosystem contributions | `★ {total_stars}` |",
        f"| **Followers** | Technical peers & collaborators | `{followers}` |",
        f"| **Following** | Engineers, researchers & projects followed | `{following}` |",
        f"| **Public Gists** | Standalone scripts, configs & benchmarks | `{public_gists}` |",
        f"| **Telemetry Status** | Last automated verification timestamp | `{sync_date} (UTC)` |",
    ]
    return "\n".join(rows)


def update_profile(
    readme_path: str = README_PATH,
    svg_path: str = SVG_PATH,
    token: str | None = None,
) -> bool:
    """
    Main update coordinator.
    Returns True if README or SVG changed, False if identical.
    """
    if not os.path.exists(readme_path):
        raise FileNotFoundError(f"Target README '{readme_path}' does not exist.")

    with open(readme_path, "r", encoding="utf-8") as f:
        original_readme = f.read()

    username = get_target_username()
    token = token or os.environ.get("GITHUB_TOKEN")

    # Fetch live data from GitHub API
    user_data = fetch_github_api(f"/users/{username}", token=token)
    repos_data = fetch_github_api(f"/users/{username}/repos?per_page=100&sort=updated", token=token)

    if not isinstance(user_data, dict) or not isinstance(repos_data, list):
        raise ValueError("Invalid API payload received from GitHub.")

    total_stars = sum(
        r.get("stargazers_count", 0) for r in repos_data if isinstance(r, dict)
    )

    # Use deterministic UTC date (YYYY-MM-DD)
    sync_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Generate sections
    activity_content = build_activity_section(repos_data, sync_date)
    profile_content = build_profile_metrics_section(user_data, total_stars, sync_date)

    updated_readme = replace_section(
        original_readme,
        "<!-- AUTO:START -->",
        "<!-- AUTO:END -->",
        activity_content,
    )
    updated_readme = replace_section(
        updated_readme,
        "<!-- PROFILE:START -->",
        "<!-- PROFILE:END -->",
        profile_content,
    )

    # Generate SVG
    generate_metrics_svg(user_data, total_stars, sync_date, svg_path)

    # Check for changes in README
    changed = updated_readme != original_readme
    if changed:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_readme)
        print(f"[+] Updated {readme_path} successfully.")
    else:
        print(f"[=] {readme_path} is already up-to-date (idempotent).")

    return changed


def main() -> None:
    try:
        update_profile()
    except Exception as err:
        sys.stderr.write(f"[-] Profile update failed: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
