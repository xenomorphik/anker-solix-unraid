# Implementation Plan: Initial MVP Implementation - Unraid Anker Solix Plugin

## Phase 1: Environment & Project Scaffolding
- [x] Task: Initialize Python virtual environment & dependencies
  - [x] Create `requirements.txt` with `anker-solix-api`, `aiohttp`, `pytest`, `pytest-asyncio`
  - [x] Set up local virtual environment structure in project
- [x] Task: Create Unraid Plugin Directory Layout
  - [x] Create `usr/local/emhttp/plugins/anker-solix/` directory tree
  - [x] Create `.plg` manifest template (`anker-solix.plg`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Core Monitoring Daemon & Anker API Integration (TDD)
- [x] Task: Write Tests for Anker Solix API Wrapper & Power Evaluation (TDD)
  - [x] Create test fixtures with mocked Anker Solix REST API responses in `tests/test_solix_api.py`
  - [x] Write unit tests for power loss detection & threshold calculation logic in `tests/test_power_monitor.py`
- [x] Task: Implement Anker Solix API Client Wrapper (`solix_client.py`)
  - [x] Implement authentication session handling and credential loading
  - [x] Implement site/device telemetry fetcher and JSON state formatter
- [x] Task: Implement Background Daemon Loop (`solix_daemon.py`)
  - [x] Implement async polling loop writing to `/tmp/anker-solix/status.json`
  - [x] Implement threshold checking & multi-stage shutdown trigger hooks
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Native Unraid WebGUI Settings & Status Page
- [ ] Task: Write Tests for Config Reader & Status JSON Parser (TDD)
  - [ ] Create unit tests for parsing and validating plugin configuration file (`anker-solix.cfg`)
- [ ] Task: Build WebGUI Settings Page (`AnkerSolix.page` & `AnkerSolix.php`)
  - [ ] Implement configuration form fields (Email, Password, Country, Thresholds)
  - [ ] Implement live AJAX telemetry widget reading `/tmp/anker-solix/status.json`
  - [ ] Implement manual "Cancel Countdown" button endpoint
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Multi-Stage Graceful Shutdown & Notifications
- [ ] Task: Write Tests for Shutdown Handler & Notification Sender (TDD)
  - [ ] Create unit tests verifying multi-stage shutdown execution order (Notification -> Docker -> VM -> Array -> Poweroff)
- [ ] Task: Implement Graceful Shutdown Executor (`shutdown_handler.py`)
  - [ ] Implement Unraid native `/usr/local/emhttp/webGui/scripts/notify` call
  - [ ] Implement `docker stop` and `virsh shutdown` hooks
  - [ ] Implement Array stop command and system `/sbin/poweroff` trigger
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Package Bundling & Integration Testing
- [ ] Task: Build Release Package Generator
  - [ ] Create packaging script to bundle virtualenv wheels and PHP assets into `.txz` / `.plg`
- [ ] Task: End-to-End Simulation Test
  - [ ] Execute full test suite verifying mock outage detection, notification dispatch, and WebGUI status update
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
