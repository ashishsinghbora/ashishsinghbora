#!/usr/bin/env python3
"""Update dynamic sections of the GitHub profile README."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen

API = "https://api.github.com"
USER = os.environ.get("GITHUB_REPOSITORY_OWNER", "ashishsinghbora")
README = "Readme.md"


def github(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ashishsinghbora-profile-updater",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(f"{API}{path}", headers=headers)
    with urlopen(req, timeout=20) as response:
        return json.load(response)


def replace_section(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{body}\n{end}"
    return pattern.sub(replacement, text, count=1)


def main() -> None:
    with open(README, encoding="utf-8") as f:
        readme = f.read()

    user = github(f"/users/{USER}")
    repos = github(f"/users/{USER}/repos?per_page=100&sort=updated")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    activity = [
        "**Automated profile update**",
        "",
        f"Last updated: **{now}**",
        "",
        f"Public repositories: **{user.get('public_repos', 0)}** · "
        f"Followers: **{user.get('followers', 0)}** · "
        f"Following: **{user.get('following', 0)}**",
        "",
        "**Recently updated repositories:**",
    ]

    for repo in repos[:6]:
        activity.append(
            f"- [{repo['name']}]({repo['html_url']}) · "
            f"★ {repo['stargazers_count']} · {repo.get('language') or '—'}"
        )

    metrics = "\n".join([
        "| Public repositories | **" + str(user.get("public_repos", 0)) + "** |",
        "| Followers | **" + str(user.get("followers", 0)) + "** |",
        "| Following | **" + str(user.get("following", 0)) + "** |",
        "| Public gists | **" + str(user.get("public_gists", 0)) + "** |",
    ])

    readme = replace_section(
        readme, "<!-- AUTO:START -->", "<!-- AUTO:END -->", "\n".join(activity)
    )
    readme = replace_section(
        readme, "<!-- PROFILE:START -->", "<!-- PROFILE:END -->", metrics
    )

    with open(README, "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
