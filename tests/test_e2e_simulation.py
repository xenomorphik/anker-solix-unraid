import unittest
from unittest.mock import patch
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../usr/local/emhttp/plugins/anker-solix')))

from solix_client import SolixClient
from solix_daemon import PowerMonitorEvaluator, SolixDaemon
from shutdown_handler import ShutdownHandler


class TestEndToEndSimulation(unittest.TestCase):
    def test_end_to_end_outage_simulation(self):
        # 1. Simulate Normal AC Grid Operation
        client = SolixClient()
        evaluator = PowerMonitorEvaluator(time_limit_minutes=10, battery_threshold_percent=20)
        
        telemetry_normal = client.format_telemetry({
            "site_name": "Home Solix",
            "grid_to_home_power": 450.0,
            "battery_soc": 90,
            "is_discharging": False
        })
        eval_normal = evaluator.evaluate(telemetry_normal, current_time=1000)
        self.assertFalse(eval_normal["should_shutdown"])

        # 2. Simulate Grid Failure / Power Outage at t=1000
        telemetry_outage = client.format_telemetry({
            "site_name": "Home Solix",
            "grid_to_home_power": 0.0,
            "battery_soc": 85,
            "is_discharging": True
        })
        eval_outage_start = evaluator.evaluate(telemetry_outage, current_time=1000)
        self.assertFalse(eval_outage_start["should_shutdown"])
        self.assertEqual(eval_outage_start["state"], "ON_BATTERY")

        # 3. Simulate 11 Minutes Elapsed on Battery Power (t=1660)
        eval_outage_expired = evaluator.evaluate(telemetry_outage, current_time=1660)
        self.assertTrue(eval_outage_expired["should_shutdown"])
        self.assertIn("Time on battery exceeded 10 minutes", eval_outage_expired["reason"])

        # 4. Trigger Shutdown Execution Handler
        shutdown_handler = ShutdownHandler()
        actions = shutdown_handler.execute_graceful_shutdown(reason=eval_outage_expired["reason"], dry_run=True)
        self.assertEqual(len(actions), 5)
        self.assertEqual(actions[0]["stage"], "NOTIFICATION")
        self.assertEqual(actions[4]["stage"], "POWEROFF")


if __name__ == '__main__':
    unittest.main()
