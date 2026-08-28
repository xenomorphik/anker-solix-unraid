# Product Guidelines: Unraid Anker Solix Power Monitor & Graceful Shutdown Plugin

## Brand Identity & Aesthetic
- **Design Philosophy:** Native Unraid WebGUI look and feel. Integrates seamlessly into Unraid's modern dark/light themes without introducing jarring visual discrepancies.
- **Visual Style:** Clean, tabular, and metric-focused dashboard widgets. Uses standard Unraid status badges (Green = Online/AC Power, Orange = On Battery, Red = Shutdown Countdown / Critical Battery).
- **Typography:** Inherits default Unraid web font hierarchy (`Open Sans` / system sans-serif) for visual consistency across Unraid settings pages.

## Voice & Tone
- **Voice:** Professional, reassuring, and precise. System power & storage state changes affect server reliability, so communication must be unambiguous.
- **Tone during Normal Operation:** Clear, informative, and unobtrusive.
- **Tone during Power Outage / Battery State:** Direct, urgent, and transparent with explicit countdown numbers and progress indicators.

## Custom Notification & Alerting Preferences
- **Multi-Channel Alerting:** Supports Unraid native notification manager (Email, Push) plus optional user-defined custom webhooks (e.g. Discord, Telegram, Gotify, NTFY, or generic HTTP POST) for power state changes.
- **Event Triggers for Notifications:**
  - *Power Disconnected / Operating on Battery*
  - *Battery Percentage Warnings (e.g. 50%, 30%)*
  - *Graceful Shutdown Initiated (Countdown Active)*
  - *Power Restored / AC Power Reconnected*

## User Experience (UX) Principles
1. **Zero-Surprise Safety First:** Never initiate an automatic shutdown without clear, visible warning logs, Unraid system notifications, custom webhook alerts, and a configurable delay allowance.
2. **Native Integration:** Use native Unraid WebGUI PHP/HTML patterns (`page` file structure, standard Unraid form helpers) and native notification APIs.
3. **Resilient Error Recovery:** If API requests fail due to transient network glitches, retry gracefully before raising a disconnect alert. Clearly inform the user if credentials or session tokens expire.
4. **Accessible Status at a Glance:** The most critical metrics—Power Source (AC vs Battery), Battery % Remaining, Estimated Runtime, and Shutdown Timer Status—must be visible immediately upon opening the plugin page.
