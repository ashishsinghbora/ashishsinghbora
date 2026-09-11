#!/usr/bin/env python3
"""
scripts/update_profile.py
-------------------------
Automated profile generator for GitHub Profile README (ashishsinghbora).

Reads configuration from `config/profile.yml`, optionally retrieves live
metadata from GitHub's REST API, and updates strictly demarcated comment
sections inside `README.md`.

Fails safely: If GitHub's API is unavailable, rate-limited, or unreachable,
existing generated sections and configured fallbacks are preserved without
corrupting or blanking out the README.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# Lightweight Standard-Library YAML Parser Fallback
# ==============================================================================

def parse_simple_yaml(text: str) -> Dict[str, Any]:
    """
    Minimal YAML parser supporting mappings, sequences, scalar types, and comments.
    Used when PyYAML is not installed to ensure zero-dependency execution.
    """
    lines = textwrap.dedent(text).splitlines()
    tokens: List[Tuple[int, str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        tokens.append((indent, stripped))

    def _parse_block(idx: int, current_indent: int) -> Tuple[Any, int]:
        res: Any = None
        while idx < len(tokens):
            indent, content = tokens[idx]
            if indent < current_indent:
                break
            if indent > current_indent:
                idx += 1
                continue

            if content.startswith("- "):
                if res is None:
                    res = []
                val = content[2:].strip()
                if not val:
                    sub_val, next_idx = _parse_block(idx + 1, indent + 2)
                    res.append(sub_val)
                    idx = next_idx
                    continue
                elif ":" in val and not (val.startswith('"') or val.startswith("'")):
                    sub_dict: Dict[str, Any] = {}
                    k, v = val.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    sub_dict[k] = v if v else None
                    sub_idx = idx + 1
                    while sub_idx < len(tokens) and tokens[sub_idx][0] > indent and not tokens[sub_idx][1].startswith("- "):
                        s_indent, s_content = tokens[sub_idx]
                        if ":" in s_content:
                            sk, sv = s_content.split(":", 1)
                            sk = sk.strip()
                            sv = sv.strip().strip('"').strip("'")
                            sub_dict[sk] = sv
                        sub_idx += 1
                    res.append(sub_dict)
                    idx = sub_idx
                    continue
                else:
                    res.append(val.strip('"').strip("'"))
                    idx += 1
            elif ":" in content:
                if res is None:
                    res = {}
                k, v = content.split(":", 1)
                k = k.strip()
                v = v.strip()
                if not v:
                    sub_val, next_idx = _parse_block(idx + 1, indent + 2)
                    res[k] = sub_val
                    idx = next_idx
                else:
                    res[k] = v.strip('"').strip("'")
                    idx += 1
            else:
                idx += 1
        return res, idx

    parsed, _ = _parse_block(0, 0)
    return parsed or {}


def load_config(config_path: Path) -> Dict[str, Any]:
    """Loads configuration from YAML with PyYAML or built-in parser."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    raw_text = config_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        config = yaml.safe_load(raw_text)
    except ImportError:
        config = parse_simple_yaml(raw_text)

    if not isinstance(config, dict):
        raise ValueError("Invalid configuration: root must be a dictionary/mapping.")

    if "username" not in config or not config["username"]:
        raise ValueError("Invalid configuration: 'username' is required.")

    return config


# ==============================================================================
# GitHub API Client
# ==============================================================================

class GitHubClient:
    """Safe wrapper for GitHub REST API calls with error handling."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ashishsinghbora-profile-updater",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _get(self, endpoint: str) -> Optional[Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"[GitHub API Warning] HTTP {e.code} for {url}: {e.reason}\n")
            return None
        except urllib.error.URLError as e:
            sys.stderr.write(f"[GitHub API Warning] Network error for {url}: {e.reason}\n")
            return None
        except Exception as e:
            sys.stderr.write(f"[GitHub API Warning] Unexpected error for {url}: {e}\n")
            return None

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        return self._get(f"/users/{username}")

    def get_repo(self, repo_full_name: str) -> Optional[Dict[str, Any]]:
        return self._get(f"/repos/{repo_full_name}")

    def get_user_events(self, username: str, limit: int = 30) -> Optional[List[Dict[str, Any]]]:
        data = self._get(f"/users/{username}/events/public?per_page={limit}")
        if isinstance(data, list):
            return data
        return None


# ==============================================================================
# Section Generators
# ==============================================================================

def generate_now_markdown(config: Dict[str, Any]) -> str:
    """Generates the 'Currently Building & Learning' section."""
    now_cfg = config.get("now", {})
    building = now_cfg.get("building", [])
    learning = now_cfg.get("learning", [])
    contributing = now_cfg.get("contributing", [])

    lines: List[str] = []

    if building:
        lines.append("- 🔨 **Active Systems & Engineering Projects:**")
        for item in building:
            if isinstance(item, dict):
                name = item.get("name", "")
                url = item.get("url", "")
                desc = item.get("description", "")
                if url:
                    lines.append(f"  - [**{name}**]({url}) — {desc}")
                else:
                    lines.append(f"  - **{name}** — {desc}")
            else:
                lines.append(f"  - {item}")

    if learning:
        lines.append("- 🔬 **Active Research & Deep Learning Areas:**")
        for item in learning:
            lines.append(f"  - {item}")

    if contributing:
        lines.append("- 🤝 **Open Source Engagements:**")
        for item in contributing:
            lines.append(f"  - {item}")

    return "\n".join(lines)


def generate_projects_markdown(config: Dict[str, Any], client: GitHubClient) -> str:
    """Generates the 'Selected Projects' section with live or fallback metadata."""
    featured = config.get("featured_repositories", [])
    lines: List[str] = []

    for item in featured:
        if isinstance(item, str):
            repo_name = item
            full_repo = f"{config['username']}/{item}"
            tagline = ""
            domain = ""
            tech = ""
            status = "Active"
            highlight = ""
        elif isinstance(item, dict):
            repo_name = item.get("name", "")
            full_repo = item.get("repo", f"{config['username']}/{repo_name}")
            tagline = item.get("tagline", "")
            domain = item.get("domain", "")
            tech = item.get("tech", "")
            status = item.get("status", "Active")
            highlight = item.get("highlight", "")
        else:
            continue

        # Fetch live stats if available
        repo_data = client.get_repo(full_repo)
        stars_str = ""
        forks_str = ""
        html_url = f"https://github.com/{full_repo}"

        if repo_data:
            stars = repo_data.get("stargazers_count", 0)
            forks = repo_data.get("forks_count", 0)
            html_url = repo_data.get("html_url", html_url)
            live_desc = repo_data.get("description")
            if live_desc and not tagline:
                tagline = live_desc
            stars_str = f" · ★ {stars}" if stars > 0 else ""
            forks_str = f" · ⑂ {forks}" if forks > 0 else ""

        # Format markdown block
        lines.append(f"### ⚙️ [{repo_name}]({html_url})")
        if tagline:
            lines.append(f"> {tagline}")
        lines.append("")
        if domain:
            lines.append(f"- **Domain:** {domain}")
        if tech:
            tech_formatted = " · ".join([f"`{t.strip()}`" for t in tech.split(",")]) if isinstance(tech, str) else " · ".join([f"`{t}`" for t in tech])
            lines.append(f"- **Technologies:** {tech_formatted}")
        if highlight:
            lines.append(f"- **Highlight:** {highlight}")
        lines.append(f"- **Status:** {status}{stars_str}{forks_str}")
        lines.append("")

    return "\n".join(lines).strip()


def generate_stats_markdown(config: Dict[str, Any], client: GitHubClient, current_section: str) -> str:
    """Generates the lightweight, reliable Markdown statistics table."""
    username = config["username"]
    user_data = client.get_user(username)

    # If GitHub API failed or rate-limited and we have existing content, preserve it
    if not user_data:
        if current_section and "| Metric |" in current_section:
            return current_section.strip()
        # Clean static baseline
        return (
            "| Metric | Details |\n"
            "| :--- | :--- |\n"
            "| **Primary Focus** | Computer Vision, Autonomous EDA Tooling, Edge Agent Systems |\n"
            "| **Core Languages** | Python, Kotlin, TypeScript, Shell (Bash/Zsh), SystemVerilog |\n"
            "| **Engineering Standard** | Zero-bloat, deterministic execution, memory-constrained design |"
        )

    public_repos = user_data.get("public_repos", 15)
    followers = user_data.get("followers", 0)

    # Compute star count across featured repositories
    total_stars = 0
    featured = config.get("featured_repositories", [])
    for item in featured:
        full_repo = item.get("repo") if isinstance(item, dict) else f"{username}/{item}"
        rdata = client.get_repo(full_repo)
        if rdata:
            total_stars += rdata.get("stargazers_count", 0)

    stats_lines = [
        "| Metric | Value / Overview |",
        "| :--- | :--- |",
        f"| **Public Repositories** | `{public_repos}` |",
        f"| **Featured Repositories Stars** | `★ {total_stars}` |",
        f"| **GitHub Community Followers** | `{followers}` |",
        "| **Core Languages** | `Python` · `Kotlin` · `TypeScript` · `Shell` · `SystemVerilog` |",
        "| **Engineering Discipline** | Low-resource footprints, deterministic pipelines, verifiable CI/CD |",
    ]
    return "\n".join(stats_lines)


def generate_activity_markdown(config: Dict[str, Any], client: GitHubClient, current_section: str) -> str:
    """
    Generates genuine recent activity feed from GitHub public events.
    Preserves current section if API fails or returns no events.
    """
    username = config["username"]
    events = client.get_user_events(username, limit=35)

    if not events:
        if current_section and current_section.strip():
            return current_section.strip()
        return "- *Activity feed temporarily cached. Refreshes on scheduled workflow run.*"

    activity_entries: List[str] = []
    seen_keys = set()

    for event in events:
        etype = event.get("type")
        repo_name = event.get("repo", {}).get("name", "")
        payload = event.get("payload", {})
        created_at = event.get("created_at", "")
        date_str = created_at[:10] if created_at else ""

        if etype == "PullRequestEvent":
            action = payload.get("action", "opened")
            pr = payload.get("pull_request", {})
            title = pr.get("title", "")
            pr_url = pr.get("html_url", f"https://github.com/{repo_name}")
            pr_num = pr.get("number", "")
            key = f"pr:{repo_name}:{pr_num}:{action}"
            if key not in seen_keys and title:
                seen_keys.add(key)
                verb = "Merged" if action == "closed" and pr.get("merged") else action.capitalize()
                activity_entries.append(
                    f"- **{verb} Pull Request** [#{pr_num}: {title}]({pr_url}) in [`{repo_name}`](https://github.com/{repo_name}) <sub style=\"color:gray\">({date_str})</sub>"
                )

        elif etype == "IssuesEvent":
            action = payload.get("action", "opened")
            issue = payload.get("issue", {})
            title = issue.get("title", "")
            issue_url = issue.get("html_url", f"https://github.com/{repo_name}")
            issue_num = issue.get("number", "")
            key = f"issue:{repo_name}:{issue_num}:{action}"
            if key not in seen_keys and title:
                seen_keys.add(key)
                verb = action.capitalize()
                activity_entries.append(
                    f"- **{verb} Issue** [#{issue_num}: {title}]({issue_url}) in [`{repo_name}`](https://github.com/{repo_name}) <sub style=\"color:gray\">({date_str})</sub>"
                )

        elif etype == "PushEvent":
            commits = payload.get("commits", [])
            if commits:
                # Find first non-merge commit
                meaningful_commits = [c for c in commits if not c.get("message", "").startswith("Merge ")]
                selected_commit = meaningful_commits[0] if meaningful_commits else commits[0]
                msg = selected_commit.get("message", "").split("\n")[0].strip()
                key = f"push:{repo_name}:{msg[:30]}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    activity_entries.append(
                        f"- **Pushed updates** to [`{repo_name}`](https://github.com/{repo_name}): *{msg}* <sub style=\"color:gray\">({date_str})</sub>"
                    )

        elif etype == "ReleaseEvent":
            release = payload.get("release", {})
            tag = release.get("tag_name", "")
            rel_url = release.get("html_url", f"https://github.com/{repo_name}")
            key = f"release:{repo_name}:{tag}"
            if key not in seen_keys:
                seen_keys.add(key)
                activity_entries.append(
                    f"- **Published Release** [`{tag}`]({rel_url}) in [`{repo_name}`](https://github.com/{repo_name}) <sub style=\"color:gray\">({date_str})</sub>"
                )

        if len(activity_entries) >= 6:
            break

    if not activity_entries:
        if current_section and current_section.strip():
            return current_section.strip()
        return "- *Recent activity synchronizing with GitHub.*"

    return "\n".join(activity_entries)


# ==============================================================================
# README Section Extraction & Replacement
# ==============================================================================

def extract_section(readme_text: str, section_name: str) -> str:
    """Extracts existing text between section markers."""
    pattern = re.compile(
        rf"<!--START_SECTION:{re.escape(section_name)}-->\s*(.*?)\s*<!--END_SECTION:{re.escape(section_name)}-->",
        re.DOTALL,
    )
    match = pattern.search(readme_text)
    return match.group(1) if match else ""


def replace_section(readme_text: str, section_name: str, new_content: str) -> str:
    """
    Safely replaces content between <!--START_SECTION:name--> and <!--END_SECTION:name-->.
    Raises ValueError if markers are not found.
    """
    pattern = re.compile(
        rf"(<!--START_SECTION:{re.escape(section_name)}-->)(.*?)(<!--END_SECTION:{re.escape(section_name)}-->)",
        re.DOTALL,
    )
    if not pattern.search(readme_text):
        raise ValueError(f"Section delimiters not found for: '{section_name}'")

    replacement = f"\\1\n{new_content.strip()}\n\\3"
    return pattern.sub(replacement, readme_text, count=1)


# ==============================================================================
# Main Orchestrator
# ==============================================================================

def update_readme(config_path: Path, readme_path: Path, dry_run: bool = False) -> bool:
    """
    Main execution pipeline:
    1. Read configuration
    2. Read current README
    3. Generate updated sections
    4. Replace sections
    5. Write back if modified
    """
    config = load_config(config_path)
    if not readme_path.is_file():
        raise FileNotFoundError(f"README file not found at: {readme_path}")

    current_readme = readme_path.read_text(encoding="utf-8")
    client = GitHubClient()

    # Extract existing content for fallback safety
    curr_now = extract_section(current_readme, "now")
    curr_projects = extract_section(current_readme, "projects")
    curr_stats = extract_section(current_readme, "stats")
    curr_activity = extract_section(current_readme, "activity")

    # Generate sections
    new_now = generate_now_markdown(config)
    new_projects = generate_projects_markdown(config, client)
    new_stats = generate_stats_markdown(config, client, curr_stats)
    new_activity = generate_activity_markdown(config, client, curr_activity)

    # Perform targeted updates
    updated = current_readme
    updated = replace_section(updated, "now", new_now)
    updated = replace_section(updated, "projects", new_projects)
    updated = replace_section(updated, "stats", new_stats)
    updated = replace_section(updated, "activity", new_activity)

    if updated == current_readme:
        print("README is already up to date. No changes required.")
        return False

    if dry_run:
        print("Dry-run enabled: Changes detected, but file was not modified.")
        return True

    readme_path.write_text(updated, encoding="utf-8")
    print(f"Successfully updated generated sections in {readme_path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Update GitHub Profile README.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/profile.yml"),
        help="Path to YAML configuration file.",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=Path("README.md"),
        help="Path to README.md file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate updates without writing to disk.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if README is up-to-date; exit with code 1 if out-of-sync.",
    )

    args = parser.parse_args()

    try:
        changed = update_readme(args.config, args.readme, dry_run=args.dry_run or args.check)
        if args.check and changed:
            print("Check failed: README is out of sync with configuration/API.")
            sys.exit(1)
    except Exception as err:
        sys.stderr.write(f"[ERROR] Failed to update README: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
