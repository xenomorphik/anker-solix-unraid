import os
import sys
import time
import json
import logging
import asyncio

from solix_client import SolixClient

logger = logging.getLogger("anker_solix.daemon")


class PowerMonitorEvaluator:
    def __init__(self, time_limit_minutes=10, battery_threshold_percent=20):
        self.time_limit_minutes = time_limit_minutes
        self.battery_threshold_percent = battery_threshold_percent
        self.battery_start_time = None

    def evaluate(self, telemetry, current_time=None):
        if current_time is None:
            current_time = time.time()

        on_battery = telemetry.get("on_battery", False)
        battery_pct = telemetry.get("battery_percentage", 100)

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
        self.client = SolixClient()
        self.evaluator = PowerMonitorEvaluator()

    def read_config(self):
        config = {
            "ANKERUSER": "",
            "ANKERPASSWORD": "",
            "ANKERCOUNTRY": "us",
            "POLL_INTERVAL": 30,
            "TIME_LIMIT_MIN": 10,
            "BATTERY_LIMIT_PCT": 20
        }
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        config[k.strip()] = v.strip().strip('"\'')
        return config

    def write_status(self, data):
        os.makedirs(os.path.dirname(self.status_path), exist_ok=True)
        with open(self.status_path, "w") as f:
            json.dump(data, f, indent=2)

    async def run(self):
        logger.info("Starting Anker Solix monitoring daemon...")
        while True:
            cfg = self.read_config()
            self.evaluator.time_limit_minutes = int(cfg.get("TIME_LIMIT_MIN", 10))
            self.evaluator.battery_threshold_percent = int(cfg.get("BATTERY_LIMIT_PCT", 20))
            
            telemetry = await self.client.fetch_latest_telemetry()
            evaluation = self.evaluator.evaluate(telemetry)

            telemetry.update({
                "evaluation": evaluation,
                "timestamp": int(time.time())
            })
            self.write_status(telemetry)

            if evaluation["should_shutdown"]:
                logger.critical(f"SHUTDOWN TRIGGERED: {evaluation['reason']}")
                # In production daemon, invoke shutdown_handler.py here

            await asyncio.sleep(int(cfg.get("POLL_INTERVAL", 30)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    daemon = SolixDaemon()
    asyncio.run(daemon.run())
