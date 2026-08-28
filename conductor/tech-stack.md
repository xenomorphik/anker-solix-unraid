# Technology Stack: Unraid Anker Solix Power Monitor & Graceful Shutdown Plugin

## Core Architecture & Languages
- **Backend Monitoring Daemon:** Python 3 (using `asyncio`, `aiohttp`, `structlog` / standard `logging`)
  - Handles background polling of Anker Solix API, threshold evaluation, countdown timer management, and triggering system shutdown commands.
- **WebGUI Interface & Settings Page:** Native Unraid PHP (`.page` file format) + HTML5 / CSS3 / JavaScript (jQuery)
  - Renders settings controls, status widgets, log viewers, and manual override triggers within Unraid's management interface.

## Dependency Management & Offline Boot Reliability
- **Python Virtual Environment:** Self-contained `/usr/local/emhttp/plugins/anker-solix/venv` bundled directly into the plugin release package (`.txz`).
- **Zero-Network Boot:** All required wheels (`anker-solix-api`, `aiohttp`, etc.) are pre-built and extracted locally during Unraid boot, guaranteeing offline execution during power or internet outages.

## Libraries & Integrations
- **API Client:** `anker-solix-api` (Python package from PyPI)
  - Manages cloud authentication tokens (`ANKERUSER`, `ANKERPASSWORD`, `ANKERCOUNTRY`), site discovery, device details, and telemetry parsing.
- **Unraid System Utilities:**
  - `/usr/local/emhttp/webGui/scripts/notify`: Unraid native notification sender.
  - `/sbin/poweroff` / `shutdown`: Unraid OS power off commands.
  - `docker stop` / `virsh shutdown`: Container and VM graceful shutdown hooks.

## Packaging & Distribution
- **Package Manifest:** Standard Unraid `.plg` XML manifest file.
- **Distribution:** Hosted via GitHub Releases with GitHub Actions automated release bundling (`.txz` / `.tar.gz` archive containing Python virtualenv and PHP WebGUI assets).

## Development & Testing Tools
- **Test Suite:** `pytest` / `pytest-asyncio` for Python unit tests and API mocking.
- **Code Quality:** `flake8` / `black` for Python styling; `php -l` for PHP syntax checking.
