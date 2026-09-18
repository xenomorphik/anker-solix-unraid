import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import json
import os
import sys

# Ensure plugin path is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../usr/local/emhttp/plugins/anker-solix')))

from solix_client import SolixClient


class TestSolixClient(unittest.TestCase):
    def setUp(self):
        self.client = SolixClient(
            username="user@example.com",
            password="secretpassword",
            country="us"
        )

    def test_initialization(self):
        self.assertEqual(self.client.username, "user@example.com")
        self.assertEqual(self.client.password, "secretpassword")
        self.assertEqual(self.client.country, "us")

    def test_format_status_normal(self):
        raw_telemetry = {
            "site_name": "Home Solix",
            "grid_to_home_power": 450.0,
            "battery_soc": 85,
            "solar_power": 600.0,
            "home_load_power": 450.0,
            "is_discharging": False
        }
        formatted = self.client.format_telemetry(raw_telemetry)
        self.assertEqual(formatted["status"], "OK")
        self.assertEqual(formatted["power_source"], "AC Grid")
        self.assertEqual(formatted["battery_percentage"], 85)
        self.assertFalse(formatted["on_battery"])

    def test_format_status_on_battery(self):
        raw_telemetry = {
            "site_name": "Home Solix",
            "grid_to_home_power": 0.0,
            "battery_soc": 40,
            "solar_power": 0.0,
            "home_load_power": 350.0,
            "is_discharging": True
        }
        formatted = self.client.format_telemetry(raw_telemetry)
        self.assertEqual(formatted["power_source"], "Battery Backup")
        self.assertEqual(formatted["battery_percentage"], 40)
        self.assertTrue(formatted["on_battery"])

    def test_authenticate_empty(self):
        import asyncio
        empty_client = SolixClient(username="", password="")
        result = asyncio.run(empty_client.authenticate())
        self.assertFalse(result["success"])
        self.assertIn("empty", result["message"].lower())

    def test_authenticate_simulated(self):
        import asyncio
        result = asyncio.run(self.client.authenticate())
        self.assertIn("success", result)


if __name__ == '__main__':
    unittest.main()
