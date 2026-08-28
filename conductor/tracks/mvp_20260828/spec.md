# Specification: Initial MVP Implementation - Unraid Anker Solix Power Monitor & Graceful Shutdown Plugin

## 1. Overview
This track delivers the initial Minimum Viable Product (MVP) of the **Unraid Anker Solix Power Monitor & Graceful Shutdown Plugin**. The MVP connects an Unraid server to Anker Solix power devices via the `anker-solix-api` Python library, provides a native Unraid WebGUI settings page, runs an asynchronous background daemon to monitor battery/grid power states, and executes a multi-stage graceful shutdown of Docker containers, VMs, Array storage, and host power when battery power thresholds are breached.

## 2. Functional Requirements

### 2.1 Unraid WebGUI Settings & Status Interface
- **Settings Form (`.page` file):**
  - Anker Account Email (`ANKERUSER`)
  - Anker Account Password (`ANKERPASSWORD`)
  - Anker Country Code (`ANKERCOUNTRY` e.g., `us`, `de`, `gb`)
  - Polling Interval (seconds, default: `30`s)
  - Shutdown Time Limit on Battery (minutes, default: `10` min)
  - Battery Percentage Threshold (%, default: `20`%)
  - Custom Notification Webhook URL (optional)
- **Live Status Widget:**
  - Reads live telemetry state from `/tmp/anker-solix/status.json`.
  - Displays Power Source (`AC Grid` / `Battery Backup`), Battery Charge (`%`), Solar Input (`W`), Output Load (`W`), and Current System State (`Normal`, `On Battery Warning`, `Shutdown Countdown Active`).
  - Manual "Cancel Shutdown" override button during active countdown.

### 2.2 Background Monitoring Daemon (`solix_daemon.py`)
- Python 3 daemon using `asyncio` and `anker-solix-api`.
- Periodically polls Anker Solix cloud API and updates local state file `/tmp/anker-solix/status.json`.
- Evaluates power loss conditions:
  - Detects when grid input drops to 0 and battery is discharging.
  - Tracks elapsed time on battery power.
  - Checks if elapsed time on battery >= Shutdown Time Limit OR remaining battery % <= Battery Threshold.
- Triggers multi-stage shutdown sequence upon threshold breach:
  1. Sends Unraid system notification (`/usr/local/emhttp/webGui/scripts/notify`) & custom webhook alert.
  2. Stops running Docker containers (`docker stop`).
  3. Gracefully shuts down Virtual Machines (`virsh shutdown`).
  4. Safely unmounts and stops Unraid Storage Array (`/usr/local/emhttp/webGui/scripts/rc.disk` / array stop hook).
  5. Power off Unraid system (`/sbin/poweroff`).

### 2.3 Packaging & Installation
- Standard Unraid `.plg` XML manifest file.
- Bundles pre-packaged Python virtual environment with `anker-solix-api` and `aiohttp` pre-installed for offline boot reliability.

## 3. Non-Functional Requirements
- **Offline Boot Resiliency:** No runtime `pip install` commands required during Unraid boot or execution.
- **Fail-Safe Operation:** If Anker API connection fails temporarily (e.g. transient network glitch), retry up to 3 times before raising a status error; never trigger shutdown solely on an API timeout unless battery state was previously known to be discharging.

## 4. Acceptance Criteria
- [ ] Settings page allows saving Anker credentials and threshold preferences.
- [ ] Daemon connects to Anker Solix API using `anker-solix-api` and writes `/tmp/anker-solix/status.json`.
- [ ] WebGUI status widget displays live telemetry from status JSON.
- [ ] Simulated power outage triggers notification and multi-stage graceful shutdown sequence.
- [ ] Pytest test suite passes with mocked Anker API responses.

## 5. Out of Scope for MVP
- Multi-site or multi-station aggregate load balancing.
- Historical graph telemetry persistence beyond RAM logs.
