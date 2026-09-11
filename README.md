# Ashish Singh Bora

**Computer Science & Engineering | Systems, AI/ML & Open Source**  
Uttarakhand, India · [Portfolio](https://ashishsinghbora.github.io/Portfolio/) · [GitHub](https://github.com/ashishsinghbora) · [Linktree](https://linktr.ee/ashishsinghbora)

---

I am a Computer Science and Engineering undergraduate focused on computer vision for planetary remote sensing, autonomous electronic design automation (EDA) verification workflows, and resource-conscious systems engineering.

My work emphasizes deterministic execution, strict memory footprints (<30MB–50MB), client-side encryption, and automated closed-loop verification pipelines across bare metal Linux, single-board computers (SBCs), and Android/Termux environments.

---

## 🧭 Currently Building & Learning

<!--START_SECTION:now-->
- 🔨 **Active Systems & Engineering Projects:**
  - [**Samanvaya**](https://github.com/ashishsinghbora/Samanvaya) — Lunar optical & NIR registration engine for Chandrayaan-2 datasets under extreme shadow reversals
  - [**EDA-Agent**](https://github.com/ashishsinghbora/EDA-Agent) — Autonomous VLSI verification framework automating RTL linting, Yosys synthesis, and cocotb self-repair
- 🔬 **Active Research & Deep Learning Areas:**
  - Subpixel planetary photogrammetry and deep dense feature matching (LoFTR)
  - Linux kernel storage subsystems, FUSE/MergerFS architectures, and encrypted storage pipelines
  - Constrained edge agent orchestration (<30MB RAM footprint on Android/Termux)
- 🤝 **Open Source Engagements:**
  - Open-source Android developer ecosystem (Mihon tracking synchronization)
  - AI-driven developer tooling and CLI utilities (how-cli)
<!--END_SECTION:now-->

---

## 🚀 Selected Work

<!--START_SECTION:projects-->
### ⚙️ [Samanvaya](https://github.com/ashishsinghbora/Samanvaya)
> Planetary image registration engine for lunar optical and NIR datasets under extreme shadow reversals

- **Domain:** Computer Vision / Planetary Science
- **Technologies:** `Python` · `PyTorch` · `LoFTR` · `GDAL/Rasterio` · `Kornia`
- **Highlight:** Engineered for Smart India Hackathon (SIH) — ISRO Chandrayaan-2 payloads
- **Status:** Active Research · ★ 3 · ⑂ 2

### ⚙️ [EDA-Agent](https://github.com/ashishsinghbora/EDA-Agent)
> Autonomous EDA and VLSI verification assistant bridging SystemVerilog with cocotb closed-loop repair

- **Domain:** Hardware Verification / AI Agents
- **Technologies:** `Python` · `SystemVerilog` · `cocotb` · `Verilator` · `Yosys` · `Docker`
- **Highlight:** Automated RTL parsing, linting, synthesizability checks, and testbench synthesis
- **Status:** Active · ★ 2 · ⑂ 1

### ⚙️ [Flashcore](https://github.com/ashishsinghbora/Flashcore)
> Non-root Android utility to create bootable USB drives via USB OTG

- **Domain:** Systems / Android Platform
- **Technologies:** `Kotlin` · `Android NDK` · `C++17` · `Linux Hybrid ISO` · `UEFI WIM`
- **Highlight:** Creates Linux Hybrid, Windows UEFI (with WIM splitting), and Ventoy media without root
- **Status:** Beta · ★ 3

### ⚙️ [Void](https://github.com/ashishsinghbora/Void)
> Ultra-lightweight local agentic platform designed to run natively inside Android/Termux (<50MB RAM)

- **Domain:** Edge AI / Embedded Systems
- **Technologies:** `Python` · `Shell` · `Telegram API` · `Termux API` · `Local LLMs`
- **Highlight:** Eliminates server overhead; rich TUI, Telegram control, and cloud brain sync
- **Status:** Active · ★ 1

### ⚙️ [ETS](https://github.com/ashishsinghbora/ETS)
> Client-side encrypted tiered storage pipeline for Linux SBCs and low-resource home servers

- **Domain:** Systems / Cloud Storage
- **Technologies:** `Shell` · `Python` · `MergerFS` · `Rclone` · `AES-256-GCM` · `Systemd`
- **Highlight:** Unifies local NVMe/SSD cache with encrypted cloud remotes into a zero-buffer mount
- **Status:** Active · ★ 1
<!--END_SECTION:projects-->

---

## 🌐 Open Source Contributions

I believe in contributing meaningful engineering back to the software ecosystem I rely on. External contributions are clearly distinguished from personal repositories:

| Project | Upstream Repository | Role | Contribution & Impact | Reference |
| :--- | :--- | :--- | :--- | :--- |
| **how-cli** | [`FireHead90544/how-cli`](https://github.com/FireHead90544/how-cli) | Core Contributor | Modernized architecture: lazy LLM loading, provider isolation, modular error handling, comprehensive test suites, and fixed PyPI packaging workflow. | [PR #7 (Merged)](https://github.com/FireHead90544/how-cli/pull/7) |
| **Mihon** | [`mihonapp/mihon`](https://github.com/mihonapp/mihon) | Contributor | Resolved missing start date issue when initiating tracking manually in Tachiyomi/Mihon tracker core, backed by Kotlin unit tests. | [PR #3930](https://github.com/mihonapp/mihon/pull/3930) |
| **ColoredCow Portal** | [`ColoredCow/portal`](https://github.com/ColoredCow/portal) | Security Researcher | Identified and responsibly disclosed public Laravel debug exposure leaking sensitive production environment details. | [Issue #3887](https://github.com/ColoredCow/portal/issues/3887) |

---

## 🛠️ Technical Stack & Core Competencies

All technologies listed below are directly reflected in working code across my public repositories:

- **Languages:** Python (Modern 3.10+), Kotlin, TypeScript, Bash / POSIX Shell, SystemVerilog / Verilog, C++ (NDK integration)
- **Machine Learning & Computer Vision:** PyTorch, Kornia, LoFTR (Deep Feature Matching), Phase Congruency, Subpixel Photogrammetry, GeoTIFF / GDAL / Rasterio
- **Systems & Infrastructure:** Linux (Arch Linux, Debian, Termux), Storage Pipelines (MergerFS, Rclone, AES-256-GCM, systemd user services), Android Architecture & NDK, OTG Storage & Filesystem Partitioning (GPT/MBR, FAT32/NTFS WIM splitting), Docker
- **Hardware & EDA Tooling:** Verilator (Linting & Simulation), Yosys (Gate-Level Synthesis), cocotb (Cocotb Testbench Generation & Co-simulation), Icarus Verilog
- **Developer Tooling & Testing:** Git, GitHub Actions (CI/CD Automation), Pytest, Playwright, Vitest, Textual / Rich TUI

---

## 📐 Engineering Approach

```text
Problem Domain Analysis → First-Principles Architecture → Minimal Dependencies → Automated Testing → Benchmarking → Verifiable Delivery
```

- **Zero-Bloat First:** Eliminate unnecessary web servers, heavy runtimes, or unneeded dependencies when a lean daemon or standard POSIX shell pipeline solves the problem cleanly.
- **Strict Resource Constraints:** Optimize for edge targets, memory budgets (<30MB–50MB RSS), and resilient error handling under low-resource conditions.
- **Verifiable Automation:** Every major workflow should be deterministic, covered by automated test suites, and integrated into continuous deployment pipelines.

---

## 📊 Overview & Profile Metrics

<!--START_SECTION:stats-->
| Metric | Value / Overview |
| :--- | :--- |
| **Public Repositories** | `15` |
| **Featured Repositories Stars** | `★ 10` |
| **GitHub Community Followers** | `38` |
| **Core Languages** | `Python` · `Kotlin` · `TypeScript` · `Shell` · `SystemVerilog` |
| **Engineering Discipline** | Low-resource footprints, deterministic pipelines, verifiable CI/CD |
<!--END_SECTION:stats-->

---

## ⚡ Recent Activity

<!--START_SECTION:activity-->
- **Merged Pull Request** [Refactor/modernize how cli](https://github.com/FireHead90544/how-cli/pull/7) in [`FireHead90544/how-cli`](https://github.com/FireHead90544/how-cli)
- **Opened Pull Request** [Fix missing start date when starting tracking manually](https://github.com/mihonapp/mihon/pull/3930) in [`mihonapp/mihon`](https://github.com/mihonapp/mihon)
- **Opened Issue** [[Security Issue] Public Laravel Debug Mode Exposes Sensitive Application Information](https://github.com/ColoredCow/portal/issues/3887) in [`ColoredCow/portal`](https://github.com/ColoredCow/portal)
- **Closed Issue** [GitHub Actions PyPI publish workflow failing with HTTP 400](https://github.com/FireHead90544/how-cli/issues/8) in [`FireHead90544/how-cli`](https://github.com/FireHead90544/how-cli)
- **Pushed updates** to [`ashishsinghbora/Samanvaya`](https://github.com/ashishsinghbora/Samanvaya): *Harden raster I/O paths and enforce tile memory budgets*
- **Pushed updates** to [`ashishsinghbora/ETS`](https://github.com/ashishsinghbora/ETS): *adopt light-first high-contrast theme for universal clarity*
<!--END_SECTION:activity-->

---

## 🔗 Connect

- **Portfolio:** [ashishsinghbora.github.io/Portfolio](https://ashishsinghbora.github.io/Portfolio/)
- **GitHub:** [@ashishsinghbora](https://github.com/ashishsinghbora)
- **Linktree:** [linktr.ee/ashishsinghbora](https://linktr.ee/ashishsinghbora)
- **Buy Me a Coffee:** [buymeacoffee.com/ashishsinghbora](https://www.buymeacoffee.com/ashishsinghbora)
