import unittest
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../usr/local/emhttp/plugins/anker-solix')))

from solix_daemon import PowerMonitorEvaluator


class TestPowerMonitor(unittest.TestCase):
    def setUp(self):
        self.evaluator = PowerMonitorEvaluator(
            time_limit_minutes=10,
            battery_threshold_percent=20
        )

    def test_grid_power_ok(self):
        telemetry = {
            "on_battery": False,
            "battery_percentage": 90,
            "grid_power": 500
        }
        res = self.evaluator.evaluate(telemetry, current_time=1000)
        self.assertFalse(res["should_shutdown"])
        self.assertEqual(res["state"], "NORMAL")
        self.assertIsNone(res["battery_start_time"])

    def test_battery_percentage_threshold_breached(self):
        telemetry = {
            "on_battery": True,
            "battery_percentage": 15,  # Below 20%
            "grid_power": 0
        }
        res = self.evaluator.evaluate(telemetry, current_time=1000)
        self.assertTrue(res["should_shutdown"])
        self.assertIn("Battery percentage (15%) below minimum limit (20%)", res["reason"])

    def test_battery_time_limit_breached(self):
        # First check when battery outage starts at t=1000
        telemetry = {
            "on_battery": True,
            "battery_percentage": 80,
            "grid_power": 0
        }
        res1 = self.evaluator.evaluate(telemetry, current_time=1000)
        self.assertFalse(res1["should_shutdown"])
        self.assertEqual(res1["state"], "ON_BATTERY")

        # Check at t=1601 (10 minutes + 1 sec later)
        res2 = self.evaluator.evaluate(telemetry, current_time=1601)
        self.assertTrue(res2["should_shutdown"])
        self.assertIn("Time on battery exceeded 10 minutes", res2["reason"])


if __name__ == '__main__':
    unittest.main()
