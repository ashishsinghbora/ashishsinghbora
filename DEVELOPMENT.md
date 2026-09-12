# Profile Development & Automation Guide

This repository powers the GitHub profile README for [@ashishsinghbora](https://github.com/ashishsinghbora). It uses an automated, zero-dependency Python generator executed via GitHub Actions to keep project metrics, current focus, and genuine activity updated without overwriting manually curated sections.

---

## 🏗️ Architecture Overview

```text
ashishsinghbora/
├── .github/workflows/
│   └── update-profile.yml    # Daily cron & push workflow
├── config/
│   └── profile.yml           # Declarative profile configuration
├── scripts/
│   └── update_profile.py     # Pure-Python generator & section updater
├── tests/
│   └── test_update_profile.py# Automated unit test suite
├── DEVELOPMENT.md            # Developer documentation
└── README.md                 # Profile README with bounded dynamic sections
```

Dynamic sections inside [README.md](README.md) are strictly delimited by HTML comment markers:
- `<!--START_SECTION:now-->` ... `<!--END_SECTION:now-->`: Current focus (building, learning, contributing)
- `<!--START_SECTION:projects-->` ... `<!--END_SECTION:projects-->`: Featured repositories with live stars/forks
- `<!--START_SECTION:stats-->` ... `<!--END_SECTION:stats-->`: Profile overview and repo metrics
- `<!--START_SECTION:activity-->` ... `<!--END_SECTION:activity-->`: Genuine recent GitHub PR, issue, and push events

Sections are optional: if a section's delimiters are omitted from `README.md`, the generator gracefully skips updating that section without error. Any content outside these marker blocks is static and will never be modified or overwritten by automation.

---

## ⚙️ How to Modify Your Profile

### 1. Update What You're Currently Working On
Edit the `now` block in [`config/profile.yml`](config/profile.yml):
```yaml
now:
  building:
    - name: "Samanvaya"
      url: "https://github.com/ashishsinghbora/Samanvaya"
      description: "Lunar optical & NIR registration engine"
  learning:
    - "Subpixel planetary photogrammetry and LoFTR"
  contributing:
    - "Mihon tracking synchronization"
```

### 2. Add or Reorder Featured Repositories
Add an entry to `featured_repositories` in [`config/profile.yml`](config/profile.yml):
```yaml
featured_repositories:
  - name: "NewProject"
    repo: "ashishsinghbora/NewProject"
    tagline: "One-line clear description"
    domain: "Systems / Machine Learning"
    tech: "Python, PyTorch, C++"
    status: "Active"
    highlight: "Key architectural or performance achievement"
```

The generator will automatically query GitHub's API for the repository's live stars, forks, and default URL. If GitHub's API is unreachable, it seamlessly falls back to the configured description and status.

### 3. Record Meaningful External Contributions
Add an entry to `open_source_contributions` in [`config/profile.yml`](config/profile.yml) and reference it in the manual table within [README.md](README.md).

---

## 🧪 Local Testing

Run the test suite with standard Python (no external dependencies required):

```bash
python3 -m unittest discover -s tests -v
```

Simulate the README generation without writing to disk:

```bash
python3 scripts/update_profile.py --dry-run
```

Apply updates locally:

```bash
python3 scripts/update_profile.py
```

Verify that the README matches the current configuration:

```bash
python3 scripts/update_profile.py --check
```

---

## 🤖 GitHub Actions Workflow

The workflow at [`.github/workflows/update-profile.yml`](.github/workflows/update-profile.yml):
1. Runs automatically on a daily schedule (`06:00 UTC`), on manual trigger (`workflow_dispatch`), and on pushes touching `config/**` or `scripts/**`.
2. Uses minimum necessary token permissions: `permissions: contents: write`.
3. Runs the test suite before touching anything.
4. Executes [`scripts/update_profile.py`](scripts/update_profile.py) with `${{ secrets.GITHUB_TOKEN }}` to fetch authenticated metrics (1,000 requests/hour limit).
5. Compares `git diff --quiet README.md`. If changes exist, commits with `chore(profile): auto-update README [skip ci]` to prevent workflow loops.
6. Does not create empty commits if no data changed.

---

## 🛡️ Reliability & Security Guarantees

- **Zero-Dependency Fallback:** Uses Python's standard library (`urllib`, `json`, `re`, `pathlib`). Optional `PyYAML` is supported when available.
- **Fail-Safe Behavior:** If GitHub's API experiences rate limiting or downtime, existing generated sections are preserved. The README will never be overwritten with empty content.
- **No Secrets Stored:** Uses temporary GitHub Actions runtime tokens only. No personal access tokens or keys are committed.
