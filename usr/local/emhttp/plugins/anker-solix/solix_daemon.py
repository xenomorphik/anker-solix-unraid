#!/usr/bin/env python3
"""
Anker Solix Daemon for Unraid
Coordinates:
1. Docker Telemetry Poller container (anker-solix-poller)
2. apcupsd NIS Bridge (solix_nis_server.py)
3. Graceful shutdown evaluation
"""

import os
import sys
import time
import json
import logging
import subprocess

from shutdown_handler import ShutdownHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("anker_solix.daemon")


class PowerMonitorEvaluator:
    def __init__(self, time_limit_minutes=10, battery_threshold_percent=20):
        self.time_limit_minutes = time_limit_minutes
        self.battery_threshold_percent = battery_threshold_percent
        self.battery_start_time = None

    def evaluate(self, telemetry, current_time=None):
        if current_time is None:
            current_time = time.time()

        status_str = telemetry.get("status", "ONLINE")
        grid_connected = telemetry.get("grid_connected", True)
        on_battery = (status_str == "ONBATT") or (not grid_connected)
        battery_pct = telemetry.get("battery_soc", telemetry.get("battery_percentage", 100))

        if not on_battery:
            self.battery_start_time = None
            return {
                "should_shutdown": False,
                "state": "NORMAL",
                "reason": "AC Power Normal",
                "battery_start_time": None
            }

        # On battery backup power
        if self.battery_start_time is None:
            self.battery_start_time = current_time

        elapsed_seconds = current_time - self.battery_start_time
        elapsed_minutes = elapsed_seconds / 60.0

        # Check threshold 1: Battery % limit
        if battery_pct <= self.battery_threshold_percent:
            return {
                "should_shutdown": True,
                "state": "SHUTDOWN_TRIGGERED",
                "reason": f"Battery percentage ({battery_pct}%) below minimum limit ({self.battery_threshold_percent}%)",
                "battery_start_time": self.battery_start_time
            }

        # Check threshold 2: Time limit on battery
        if elapsed_minutes >= self.time_limit_minutes:
            return {
                "should_shutdown": True,
                "state": "SHUTDOWN_TRIGGERED",
                "reason": f"Time on battery exceeded {self.time_limit_minutes} minutes ({int(elapsed_minutes)}m elapsed)",
                "battery_start_time": self.battery_start_time
            }

        return {
            "should_shutdown": False,
            "state": "ON_BATTERY",
            "reason": f"Operating on battery power ({int(elapsed_minutes)}m elapsed, {battery_pct}% remaining)",
            "battery_start_time": self.battery_start_time
        }


class SolixDaemon:
    def __init__(self, config_path="/boot/config/plugins/anker-solix/anker-solix.cfg", status_path="/tmp/anker-solix/status.json"):
        self.config_path = config_path
        self.status_path = status_path
        self.evaluator = PowerMonitorEvaluator()
        self.shutdown_handler = ShutdownHandler()

    def read_config(self):
        config = {
            "ANKERUSER": "",
            "ANKERPASSWORD": "",
            "ANKERCOUNTRY": "us",
            "POLL_INTERVAL": "30",
            "TIME_LIMIT_MIN": "10",
            "BATTERY_LIMIT_PCT": "20"
        }
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        config[k.strip()] = v.strip().strip('"\'')
        return config

    def read_status(self):
        if os.path.exists(self.status_path):
            try:
                with open(self.status_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def ensure_services(self):
        # 1. Ensure Docker poller container is running
        try:
            res = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", "anker-solix-poller"], capture_output=True, text=True)
            if res.returncode != 0 or res.stdout.strip() != "true":
                logger.info("Starting anker-solix-poller container...")
                subprocess.run(["docker", "rm", "-f", "anker-solix-poller"], capture_output=True, check=False)
                subprocess.run([
                    "docker", "run", "-d", "--name", "anker-solix-poller", "--restart", "unless-stopped",
                    "-v", "/boot/config/plugins/anker-solix/anker-solix.cfg:/boot/config/plugins/anker-solix/anker-solix.cfg:ro",
                    "-v", "/tmp/anker-solix:/tmp/anker-solix",
                    "anker-solix-poller:latest"
                ], check=False)
        except Exception as e:
            logger.error(f"Error checking poller container: {e}")

        # 2. Ensure NIS bridge is running
        try:
            nis_check = subprocess.run(["pgrep", "-f", "solix_nis_server.py"], capture_output=True, text=True)
            if nis_check.returncode != 0:
                logger.info("Starting solix_nis_server.py bridge...")
                subprocess.Popen(["/usr/bin/python3", "/usr/local/emhttp/plugins/anker-solix/solix_nis_server.py"])
        except Exception as e:
            logger.error(f"Error checking NIS bridge: {e}")

    def run(self):
        logger.info("Starting Anker Solix Supervisor Daemon...")
        while True:
            try:
                cfg = self.read_config()
                self.evaluator.time_limit_minutes = int(cfg.get("TIME_LIMIT_MIN", 10))
                self.evaluator.battery_threshold_percent = int(cfg.get("BATTERY_LIMIT_PCT", 20))

                self.ensure_services()

                telemetry = self.read_status()
                if telemetry:
                    eval_result = self.evaluator.evaluate(telemetry)
                    if eval_result["should_shutdown"]:
                        logger.critical(f"SHUTDOWN TRIGGERED: {eval_result['reason']}")
                        self.shutdown_handler.execute_graceful_shutdown(reason=eval_result["reason"])

            except Exception as e:
                logger.error(f"Error in supervisor loop: {e}")

            time.sleep(10)


if __name__ == '__main__':
    daemon = SolixDaemon()
    daemon.run()
