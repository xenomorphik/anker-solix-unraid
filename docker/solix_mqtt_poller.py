#!/usr/bin/env python3
"""
Anker Solix S2000 Poller & Telemetry Daemon
Maintains cloud session & MQTT stream with Anker Cloud.
Writes live status to /tmp/anker-solix/status.json for host consumption.
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
import aiohttp
from anker_solix_api import api, poller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("solix_poller")

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/boot/config/plugins/anker-solix/anker-solix.cfg")
STATUS_PATH = os.environ.get("STATUS_PATH", "/tmp/anker-solix/status.json")

def load_config():
    config = {
        "ANKERUSER": "",
        "ANKERPASSWORD": "",
        "ANKERCOUNTRY": "us",
        "POLL_INTERVAL": "15",
        "BATTERY_LIMIT_PCT": "20",
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        config[k.strip()] = v.strip().strip('"').strip("'")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return config

async def run_poller():
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    
    while True:
        cfg = load_config()
        user = cfg.get("ANKERUSER")
        pwd = cfg.get("ANKERPASSWORD")
        country = cfg.get("ANKERCOUNTRY", "us")
        poll_int = int(cfg.get("POLL_INTERVAL", "15"))

        if not user or not pwd:
            logger.warning("Anker credentials not configured. Waiting 10s...")
            await asyncio.sleep(10)
            continue

        logger.info(f"Connecting to Anker Cloud API for user {user}...")
        try:
            async with aiohttp.ClientSession() as session:
                solix_api = api.AnkerSolixApi(
                    email=user,
                    password=pwd,
                    countryId=country,
                    websession=session
                )
                await solix_api.update_sites()
                await poller.poll_device_details(solix_api)

                if not solix_api.devices:
                    logger.warning("No Solix devices found on account. Retrying in 30s...")
                    await asyncio.sleep(30)
                    continue

                # Locate S2000 or first PPS/Device
                sn = list(solix_api.devices.keys())[0]
                dev_info = solix_api.devices[sn]
                logger.info(f"Targeting device: {dev_info.get('name')} (SN: {sn}, Model: {dev_info.get('device_pn')})")

                # Start MQTT Session
                mqtt = await solix_api.startMqttSession()
                prefix = mqtt.get_topic_prefix(dev_info)
                sub_topic = prefix + "#"
                mqtt.subscribe(sub_topic)
                logger.info(f"Subscribed to MQTT topic: {sub_topic}")

                last_request = 0
                while True:
                    now = time.time()
                    # Solix S2000 refreshes telemetry frame on status_request
                    if now - last_request >= poll_int:
                        try:
                            mqtt.status_request(dev_info)
                            last_request = now
                        except Exception as req_err:
                            logger.debug(f"Status request error: {req_err}")

                    # Check received data
                    data = mqtt.mqtt_data.get(sn, {})
                    if data:
                        battery_soc = data.get("battery_soc", 100)
                        battery_soh = data.get("battery_soh", 100)
                        ac_in_power = data.get("ac_input_power", 0)
                        ac_out_power = data.get("ac_output_power", data.get("output_power_total", 0))
                        grid_plugged = data.get("ac_input_plug_status", 1) == 1
                        temp = data.get("temperature", 25)
                        charging = data.get("charge", False)

                        # Determine status
                        if not grid_plugged:
                            status_str = "ONBATT"
                        elif charging and battery_soc < 100:
                            status_str = "CHARGING"
                        else:
                            status_str = "ONLINE"

                        # Runtime calculation (Capacity 2010 Wh)
                        # Remaining Wh = (SOC / 100) * 2010 Wh
                        # Remaining Minutes = (Remaining Wh / Output W) * 60
                        remaining_wh = (float(battery_soc) / 100.0) * 2010.0
                        if ac_out_power > 10:
                            time_left_min = round((remaining_wh / float(ac_out_power)) * 60.0, 1)
                        else:
                            time_left_min = 600.0

                        status_payload = {
                            "timestamp": datetime.now().isoformat(),
                            "device_name": dev_info.get("name", "Anker SOLIX S2000"),
                            "device_sn": sn,
                            "device_pn": dev_info.get("device_pn", "AS220"),
                            "status": status_str,
                            "battery_soc": battery_soc,
                            "battery_soh": battery_soh,
                            "input_power_w": ac_in_power,
                            "output_power_w": ac_out_power,
                            "time_left_min": time_left_min,
                            "temperature_c": temp,
                            "grid_connected": grid_plugged,
                            "wifi_signal": data.get("wifi_signal", 100),
                            "sw_version": data.get("sw_version", "1.0.2.2"),
                            "raw_telemetry": data
                        }

                        # Atomic file write
                        tmp_path = STATUS_PATH + ".tmp"
                        with open(tmp_path, "w") as f:
                            json.dump(status_payload, f, indent=2)
                        os.replace(tmp_path, STATUS_PATH)

                    await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Solix poller encountered error: {e}. Reconnecting in 10s...", exc_info=True)
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(run_poller())
    except KeyboardInterrupt:
        logger.info("Poller stopped by user.")
