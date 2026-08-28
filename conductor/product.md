# Product Definition: Unraid Anker Solix Power Monitor & Graceful Shutdown Plugin

## Vision & Overview
The **Unraid Anker Solix Power Monitor & Graceful Shutdown Plugin** provides seamless integration between Unraid OS and Anker Solix power devices (Solarbanks, Portable Power Stations, Smart Meters, and Inverters). By leveraging the `anker-solix-api` Python client, the plugin continuously tracks grid connectivity, power draw, and battery charge levels. In the event of a power outage where the Unraid server runs on battery power, the plugin executes configurable threshold checks and triggers an automated, graceful shutdown of Docker containers, Virtual Machines, and Unraid array storage to preserve system state and data integrity.

## Key Features & Functionality

### 1. Authentication & Cloud Integration
- Integrates with the Anker Solix cloud API via account credentials (`ANKERUSER`, `ANKERPASSWORD`, `ANKERCOUNTRY`).
- Provides a dedicated Unraid WebGUI settings page for secure configuration.
- Supports and recommends Anker "Family Share" secondary accounts to prevent invalidating mobile app sessions.

### 2. Live Monitoring & Status Dashboard
- Embedded status page / widget inside Unraid WebGUI displaying real-time battery percentage, grid status, solar input, and current load.
- Background monitoring daemon/script running on a configurable polling interval (e.g., every 30-60 seconds).

### 3. Configurable Shutdown Triggers
- Dual-trigger conditions:
  1. **Maximum Time on Battery:** Triggers shutdown after running on battery power for $N$ minutes (e.g., 10 minutes).
  2. **Minimum Battery Percentage:** Triggers shutdown when remaining battery level drops below $X\%$ (e.g., 20%).
- Manual override / cancel shutdown capability from Unraid WebGUI during countdown.

### 4. Graceful Multi-Stage Shutdown Sequence
- **Stage 1:** Trigger native Unraid notifications (Email, Push, Discord/Telegram) warning of impending shutdown.
- **Stage 2:** Gracefully stop running Docker containers and Virtual Machines (VMs).
- **Stage 3:** Safely unmount and stop the Unraid storage array.
- **Stage 4:** Issue final system poweroff command (`shutdown -h now`).

### 5. Notification & Alerting
- Full integration with Unraid's native Notification Manager for real-time status alerts (Power Lost, On Battery, Shutdown Triggered, Power Restored).

## Target Audience & Use Cases
- **Unraid Home Server Operators** who use Anker Solix power stations / solarbanks as emergency UPS/battery backups.
- **Homelab Engineers** seeking automated, zero-touch power protection for critical home storage, media servers, and self-hosted databases.
