#!/usr/bin/env python3
"""
Unit tests for profile updater and validator.
"""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from scripts.update_profile import (
    build_activity_section,
    build_profile_metrics_section,
    generate_metrics_svg,
    get_target_username,
    replace_section,
)


class TestProfileUpdater(unittest.TestCase):
    def test_target_username_default(self):
        # Username should fallback to ashishsinghbora if env is not set
        user = get_target_username()
        self.assertTrue(len(user) > 0)

    def test_replace_section_success(self):
        content = "Line1\n<!-- TEST:START -->\nOld Body\n<!-- TEST:END -->\nLine2"
        updated = replace_section(content, "<!-- TEST:START -->", "<!-- TEST:END -->", "New Body")
        expected = "Line1\n<!-- TEST:START -->\nNew Body\n<!-- TEST:END -->\nLine2"
        self.assertEqual(updated, expected)

    def test_replace_section_missing_marker(self):
        content = "Line1\n<!-- OTHER:START -->\nLine2"
        with self.assertRaises(ValueError):
            replace_section(content, "<!-- TEST:START -->", "<!-- TEST:END -->", "Body")

    def test_build_activity_filtering(self):
        mock_repos = [
            {"name": "forked-one", "fork": True, "archived": False},
            {"name": "archived-one", "fork": False, "archived": True},
            {"name": "ashishsinghbora", "fork": False, "archived": False},
            {
                "name": "legit-project",
                "fork": False,
                "archived": False,
                "description": "A high-performance Linux daemon",
                "language": "C++",
                "stargazers_count": 42,
                "updated_at": "2026-09-25T10:00:00Z",
                "html_url": "https://github.com/ashishsinghbora/legit-project",
            },
        ]
        result = build_activity_section(mock_repos, "2026-09-25")
        self.assertIn("legit-project", result)
        self.assertNotIn("forked-one", result)
        self.assertNotIn("archived-one", result)
        self.assertNotIn("[ashishsinghbora]", result)
        self.assertIn("★ 42", result)
        self.assertIn("`C++`", result)

    def test_build_profile_metrics(self):
        mock_user = {
            "public_repos": 23,
            "followers": 105,
            "following": 549,
            "public_gists": 2,
        }
        result = build_profile_metrics_section(mock_user, 303, "2026-09-25")
        self.assertIn("`23`", result)
        self.assertIn("★ 303", result)
        self.assertIn("`105`", result)
        self.assertIn("`549`", result)
        self.assertIn("`2`", result)

    def test_svg_generation(self):
        mock_user = {
            "public_repos": 23,
            "followers": 105,
            "following": 549,
        }
        test_svg = "assets/test-unit.svg"
        try:
            generate_metrics_svg(mock_user, 303, "2026-09-25", test_svg)
            self.assertTrue(os.path.isfile(test_svg))
            # Verify it is valid XML
            tree = ET.parse(test_svg)
            root = tree.getroot()
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        finally:
            if os.path.exists(test_svg):
                os.remove(test_svg)


if __name__ == "__main__":
    unittest.main()
