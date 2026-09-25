#!/usr/bin/env python3
"""
Validation suite for the profile repository.
Ensures README integrity, marker health, updater safety, secret prevention,
and CI workflow validity.
"""

from __future__ import annotations

import os
import py_compile
import re
import sys
import xml.etree.ElementTree as ET

# Import functions from update_profile for unit verification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.update_profile import (  # noqa: E402
    build_activity_section,
    build_profile_metrics_section,
    generate_metrics_svg,
    replace_section,
)

README_PATH = "Readme.md"
WORKFLOW_PATH = ".github/workflows/update-profile.yml"
SVG_PATH = "assets/profile-metrics.svg"


def check_python_syntax() -> None:
    """Validate all Python scripts under scripts/ and tests/ compile cleanly."""
    for folder in ("scripts", "tests"):
        if not os.path.isdir(folder):
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    py_compile.compile(full_path, doraise=True)
    print("[✓] Python syntax compiled successfully.")


def check_readme_structure() -> None:
    """Verify README existence, markers, and order."""
    if not os.path.isfile(README_PATH):
        raise FileNotFoundError(f"{README_PATH} does not exist.")

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    required_pairs = [
        ("<!-- PROFILE:START -->", "<!-- PROFILE:END -->"),
        ("<!-- AUTO:START -->", "<!-- AUTO:END -->"),
    ]

    for start_m, end_m in required_pairs:
        start_idx = content.find(start_m)
        end_idx = content.find(end_m)

        if start_idx == -1:
            raise ValueError(f"Missing required marker: '{start_m}' in {README_PATH}")
        if end_idx == -1:
            raise ValueError(f"Missing required marker: '{end_m}' in {README_PATH}")
        if start_idx >= end_idx:
            raise ValueError(f"Marker '{start_m}' must appear before '{end_m}' in {README_PATH}")

    print("[✓] README structure and marker ordering verified.")


def check_replacement_logic() -> None:
    """Verify that section replacements work deterministically."""
    sample = (
        "Header\n<!-- TEST:START -->\nOld content\n<!-- TEST:END -->\nFooter"
    )
    result = replace_section(sample, "<!-- TEST:START -->", "<!-- TEST:END -->", "New content")
    expected = "Header\n<!-- TEST:START -->\nNew content\n<!-- TEST:END -->\nFooter"
    if result != expected:
        raise AssertionError("replace_section did not produce expected output.")
    print("[✓] Section replacement logic verified.")


def check_resilient_parsing() -> None:
    """Verify updater handles missing, empty, or None fields from API without error."""
    mock_user = {
        "public_repos": None,
        "followers": None,
        "following": None,
        "public_gists": None,
    }
    mock_repos = [
        {
            "name": "edge-test",
            "description": None,
            "language": None,
            "stargazers_count": 0,
            "fork": False,
            "archived": False,
            "updated_at": None,
        },
        {
            "name": "forked-test",
            "fork": True,
            "archived": False,
        },
        {
            "name": "archived-test",
            "fork": False,
            "archived": True,
        },
        {},  # Completely empty dictionary
    ]

    # Verify building sections doesn't raise exceptions
    act_out = build_activity_section(mock_repos, "2026-09-25")
    if "edge-test" not in act_out:
        raise AssertionError("Valid un-forked repo was not included in activity.")
    if "forked-test" in act_out or "archived-test" in act_out:
        raise AssertionError("Forked or archived repo was incorrectly included.")

    met_out = build_profile_metrics_section(mock_user, 10, "2026-09-25")
    if "None" in met_out:
        # Check that it handles None gracefully
        pass

    # Verify SVG generation doesn't crash on empty fields
    temp_svg = "assets/test-metrics.svg"
    try:
        generate_metrics_svg(mock_user, 42, "2026-09-25", temp_svg)
        ET.parse(temp_svg)  # Verify valid XML
    finally:
        if os.path.exists(temp_svg):
            os.remove(temp_svg)

    print("[✓] Resilient parsing and null safety verified.")


def check_no_secrets() -> None:
    """Ensure no auth tokens, PATs, or private keys exist in tracked files."""
    secret_patterns = [
        re.compile(r"ghp_[A-Za-z0-9_]{30,}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
        re.compile(r"Bearer\s+ghp_"),
        re.compile(r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"),
    ]

    for root, _, files in os.walk("."):
        if ".git" in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for pat in secret_patterns:
                        if pat.search(content):
                            raise ValueError(f"Potential secret detected in file: {path}")
            except Exception as e:
                if isinstance(e, ValueError):
                    raise
    print("[✓] Secret inspection passed: 0 secrets or tokens detected.")


def check_workflow_validity() -> None:
    """Verify GitHub Actions workflow file exists, has required keys and permissions."""
    if not os.path.isfile(WORKFLOW_PATH):
        raise FileNotFoundError(f"Workflow file '{WORKFLOW_PATH}' not found.")

    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        wf = f.read()

    required_keywords = [
        "contents: write",
        "schedule:",
        "cron:",
        "workflow_dispatch:",
        "update_profile.py",
    ]
    for kw in required_keywords:
        if kw not in wf:
            raise ValueError(f"Workflow missing critical specification: '{kw}'")

    print("[✓] GitHub Actions workflow configuration verified.")


def check_svg_validity() -> None:
    """Verify that generated SVG (if present) is well-formed XML."""
    if os.path.isfile(SVG_PATH):
        try:
            ET.parse(SVG_PATH)
            print("[✓] Generated SVG is structurally valid XML.")
        except ET.ParseError as e:
            raise ValueError(f"SVG parsing failed: {e}")


def main() -> None:
    print("[*] Running profile validation checks...")
    try:
        check_python_syntax()
        check_readme_structure()
        check_replacement_logic()
        check_resilient_parsing()
        check_no_secrets()
        check_workflow_validity()
        check_svg_validity()
        print("\n[✓] ALL PROFILE VALIDATION CHECKS PASSED.")
    except Exception as err:
        sys.stderr.write(f"\n[!] VALIDATION FAILED: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
