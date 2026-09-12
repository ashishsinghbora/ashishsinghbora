#!/usr/bin/env python3
"""
tests/test_update_profile.py
----------------------------
Comprehensive test suite for the profile automation script.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path so scripts module can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import update_profile


class TestSimpleYamlParser(unittest.TestCase):
    """Verifies that the standard-library YAML parser behaves correctly."""

    def test_parse_basic_mapping_and_lists(self):
        sample = """
        username: "testuser"
        count: 42
        now:
          building:
            - name: "ProjectAlpha"
              url: "https://github.com/testuser/ProjectAlpha"
              description: "High-performance cache"
          learning:
            - "Distributed consensus"
            - "eBPF tracepoints"
        featured_repositories:
          - "Repo1"
          - "Repo2"
        """
        parsed = update_profile.parse_simple_yaml(sample)
        self.assertEqual(parsed["username"], "testuser")
        self.assertIn("now", parsed)
        self.assertEqual(len(parsed["now"]["building"]), 1)
        self.assertEqual(parsed["now"]["building"][0]["name"], "ProjectAlpha")
        self.assertEqual(len(parsed["now"]["learning"]), 2)
        self.assertEqual(parsed["featured_repositories"], ["Repo1", "Repo2"])

    def test_parse_actual_profile_config(self):
        cfg_path = REPO_ROOT / "config" / "profile.yml"
        cfg = update_profile.load_config(cfg_path)
        self.assertEqual(cfg["username"], "ashishsinghbora")
        self.assertIn("now", cfg)
        self.assertIn("featured_repositories", cfg)
        self.assertTrue(len(cfg["featured_repositories"]) >= 3)


class TestConfigValidation(unittest.TestCase):
    """Verifies validation rules for configuration loading."""

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            update_profile.load_config(Path("non_existent_config.yml"))

    def test_missing_username_raises_error(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w+", suffix=".yml", delete=False) as f:
            f.write("featured_repositories:\n  - RepoA\n")
            f_path = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                update_profile.load_config(f_path)
        finally:
            f_path.unlink()


class TestSectionExtractionAndReplacement(unittest.TestCase):
    """Verifies strictly scoped delimited section extraction and replacement."""

    def setUp(self):
        self.sample_readme = (
            "# Title\n\n"
            "Static preface text.\n\n"
            "<!--START_SECTION:testsec-->\n"
            "Old content\n"
            "<!--END_SECTION:testsec-->\n\n"
            "Static suffix text.\n"
        )

    def test_extract_section(self):
        extracted = update_profile.extract_section(self.sample_readme, "testsec")
        self.assertEqual(extracted, "Old content")

    def test_replace_section(self):
        new_content = "New dynamic line 1\nNew dynamic line 2"
        result = update_profile.replace_section(self.sample_readme, "testsec", new_content)
        expected = (
            "# Title\n\n"
            "Static preface text.\n\n"
            "<!--START_SECTION:testsec-->\n"
            "New dynamic line 1\nNew dynamic line 2\n"
            "<!--END_SECTION:testsec-->\n\n"
            "Static suffix text.\n"
        )
        self.assertEqual(result, expected)
        # Ensure static outside parts are completely untouched
        self.assertTrue(result.startswith("# Title\n\nStatic preface text.\n\n"))
        self.assertTrue(result.endswith("\n\nStatic suffix text.\n"))

    def test_replace_section_missing_marker_raises(self):
        with self.assertRaises(ValueError):
            update_profile.replace_section(self.sample_readme, "missing_sec", "text")

    def test_has_section(self):
        self.assertTrue(update_profile.has_section(self.sample_readme, "testsec"))
        self.assertFalse(update_profile.has_section(self.sample_readme, "missing_sec"))


class TestGenerators(unittest.TestCase):
    """Verifies generation of Markdown for each dynamic section."""

    def setUp(self):
        self.config = {
            "username": "ashishsinghbora",
            "now": {
                "building": [
                    {
                        "name": "Samanvaya",
                        "url": "https://github.com/ashishsinghbora/Samanvaya",
                        "description": "Planetary image registration",
                    }
                ],
                "learning": ["Photogrammetry", "Linux Storage"],
                "contributing": ["how-cli refactor"],
            },
            "featured_repositories": [
                {
                    "name": "Samanvaya",
                    "repo": "ashishsinghbora/Samanvaya",
                    "tagline": "Planetary image registration engine",
                    "domain": "Computer Vision",
                    "tech": "Python, PyTorch",
                    "status": "Active Research",
                    "highlight": "Smart India Hackathon",
                }
            ],
        }

    def test_generate_now_markdown(self):
        md = update_profile.generate_now_markdown(self.config)
        self.assertIn("[**Samanvaya**](https://github.com/ashishsinghbora/Samanvaya)", md)
        self.assertIn("Planetary image registration", md)
        self.assertIn("Photogrammetry", md)
        self.assertIn("how-cli refactor", md)

    def test_generate_projects_markdown_offline_fallback(self):
        mock_client = MagicMock()
        mock_client.get_repo.return_value = None  # Simulates API failure / rate limit

        md = update_profile.generate_projects_markdown(self.config, mock_client)
        self.assertIn("### ⚙️ [Samanvaya](https://github.com/ashishsinghbora/Samanvaya)", md)
        self.assertIn("Planetary image registration engine", md)
        self.assertIn("- **Domain:** Computer Vision", md)
        self.assertIn("- **Technologies:** `Python` · `PyTorch`", md)
        self.assertIn("Smart India Hackathon", md)

    def test_generate_projects_markdown_live_stats(self):
        mock_client = MagicMock()
        mock_client.get_repo.return_value = {
            "stargazers_count": 12,
            "forks_count": 4,
            "html_url": "https://github.com/ashishsinghbora/Samanvaya",
            "description": "Live fetched description",
        }

        md = update_profile.generate_projects_markdown(self.config, mock_client)
        self.assertIn("★ 12", md)
        self.assertIn("⑂ 4", md)

    def test_generate_stats_markdown_offline(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = None

        current = "| Metric | Details |\n| :--- | :--- |\n| Existing | Content |"
        stats = update_profile.generate_stats_markdown(self.config, mock_client, current)
        self.assertEqual(stats, current)

    def test_generate_activity_preserves_on_api_failure(self):
        mock_client = MagicMock()
        mock_client.get_user_events.return_value = None  # API offline

        cached_activity = "- **Opened PR** in test-repo"
        result = update_profile.generate_activity_markdown(self.config, mock_client, cached_activity)
        self.assertEqual(result, cached_activity)

    def test_generate_activity_parses_real_events(self):
        mock_client = MagicMock()
        mock_client.get_user_events.return_value = [
            {
                "type": "PullRequestEvent",
                "repo": {"name": "FireHead90544/how-cli"},
                "payload": {
                    "action": "closed",
                    "pull_request": {
                        "number": 7,
                        "title": "Refactor/modernize how cli",
                        "html_url": "https://github.com/FireHead90544/how-cli/pull/7",
                        "merged": True,
                    },
                },
                "created_at": "2026-09-10T10:46:38Z",
            },
            {
                "type": "IssuesEvent",
                "repo": {"name": "ColoredCow/portal"},
                "payload": {
                    "action": "opened",
                    "issue": {
                        "number": 3887,
                        "title": "Public Laravel Debug Mode Exposes Sensitive Information",
                        "html_url": "https://github.com/ColoredCow/portal/issues/3887",
                    },
                },
                "created_at": "2026-09-10T21:58:02Z",
            },
        ]

        activity = update_profile.generate_activity_markdown(self.config, mock_client, "")
        self.assertIn("Merged Pull Request", activity)
        self.assertIn("#7: Refactor/modernize how cli", activity)
        self.assertIn("FireHead90544/how-cli", activity)
        self.assertIn("Opened Issue", activity)
        self.assertIn("#3887", activity)
        self.assertIn("ColoredCow/portal", activity)


class TestIdempotency(unittest.TestCase):
    """Verifies that running update on already up-to-date content produces no mutations."""

    def test_idempotent_execution(self):
        readme_path = REPO_ROOT / "README.md"
        config_path = REPO_ROOT / "config" / "profile.yml"
        original_content = readme_path.read_text(encoding="utf-8")

        try:
            # Mock API to return predictable responses
            with patch.object(update_profile.GitHubClient, "get_repo", return_value=None), \
                 patch.object(update_profile.GitHubClient, "get_user", return_value=None), \
                 patch.object(update_profile.GitHubClient, "get_user_events", return_value=None):
                
                # First pass
                update_profile.update_readme(config_path, readme_path, dry_run=False)
                pass1 = readme_path.read_text(encoding="utf-8")

                # Second pass
                changed = update_profile.update_readme(config_path, readme_path, dry_run=False)
                pass2 = readme_path.read_text(encoding="utf-8")

                self.assertFalse(changed, "Second run should report no changes (idempotent)")
                self.assertEqual(pass1, pass2, "Second run output must be byte-for-byte identical")
        finally:
            readme_path.write_text(original_content, encoding="utf-8")

    def test_partial_sections_handling(self):
        """Ensures update_readme succeeds when only a subset of sections are present."""
        import tempfile
        config_path = REPO_ROOT / "config" / "profile.yml"
        partial_readme = (
            "# Title\n\n"
            "<!--START_SECTION:now-->\nold now\n<!--END_SECTION:now-->\n"
        )
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write(partial_readme)
            temp_path = Path(f.name)

        try:
            with patch.object(update_profile.GitHubClient, "get_repo", return_value=None), \
                 patch.object(update_profile.GitHubClient, "get_user", return_value=None), \
                 patch.object(update_profile.GitHubClient, "get_user_events", return_value=None):
                changed = update_profile.update_readme(config_path, temp_path, dry_run=False)
                self.assertTrue(changed)
                updated_content = temp_path.read_text(encoding="utf-8")
                self.assertIn("Active Systems & Engineering Projects", updated_content)
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
