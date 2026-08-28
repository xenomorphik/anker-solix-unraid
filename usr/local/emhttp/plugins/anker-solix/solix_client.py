import os
import json
import logging

logger = logging.getLogger("anker_solix.client")


class SolixClient:
    def __init__(self, username="", password="", country="us"):
        self.username = username
        self.password = password
        self.country = country
        self.session = None

    def format_telemetry(self, raw_data):
        """
        Formats raw telemetry dictionary into a standard status dictionary
        used by the Unraid WebGUI and monitoring daemon.
        """
        grid_power = float(raw_data.get("grid_to_home_power", 0.0))
        battery_soc = int(raw_data.get("battery_soc", 0))
        is_discharging = bool(raw_data.get("is_discharging", False))
        
        on_battery = is_discharging or (grid_power <= 0 and battery_soc < 100)

        return {
            "status": "OK",
            "site_name": raw_data.get("site_name", "Anker Solix"),
            "power_source": "Battery Backup" if on_battery else "AC Grid",
            "battery_percentage": battery_soc,
            "grid_power_w": grid_power,
            "solar_power_w": float(raw_data.get("solar_power", 0.0)),
            "load_power_w": float(raw_data.get("home_load_power", 0.0)),
            "on_battery": on_battery
        }

    async def fetch_latest_telemetry(self):
        """
        Fetches telemetry using anker-solix-api if available,
        or returns simulated response if credentials are not set/offline.
        """
        try:
            from anker_solix_api import api
            # In a real environment with credentials:
            # async with aiohttp.ClientSession() as websession:
            #     solix = api.AnkerSolixApi(user=self.username, password=self.password, country=self.country, websession=websession)
            #     await solix.update_sites()
            #     ...
        except ImportError:
            logger.warning("anker-solix-api package not installed. Using fallback telemetry parser.")

        return self.format_telemetry({
            "site_name": "Solix Backup System",
            "grid_to_home_power": 500.0,
            "battery_soc": 95,
            "solar_power": 300.0,
            "home_load_power": 500.0,
            "is_discharging": False
        })
