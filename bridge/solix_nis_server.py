#!/usr/bin/env python3
"""
Anker Solix apcupsd NIS Bridge
Listens on TCP port 3551 (apcupsd NIS protocol).
Serves live Anker Solix status to Unraid's native UPS subsystem.
Maintains /var/run/apcupsd.pid so Dynamix UPS widget and dashboard activate.
"""

import os
import sys
import time
import json
import socket
import struct
import signal
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("solix_nis_bridge")

STATUS_PATH = os.environ.get("STATUS_PATH", "/tmp/anker-solix/status.json")
PID_FILE = "/var/run/apcupsd.pid"
BIND_HOST = os.environ.get("BIND_HOST", "0.0.0.0")
BIND_PORT = int(os.environ.get("BIND_PORT", "3551"))
START_TIME = datetime.now()

def cleanup(signum, frame):
    logger.info("Stopping Solix NIS Bridge...")
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

def read_status():
    if os.path.exists(STATUS_PATH):
        try:
            with open(STATUS_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading status.json: {e}")
    return {}

def send_nis_line(sock, line):
    encoded = line.encode("latin-1", errors="replace")
    sock.sendall(struct.pack("!H", len(encoded)) + encoded)

def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        status_info = read_status()
        
        # Read telemetry
        model = status_info.get("device_name", "Anker SOLIX S2000")
        serial = status_info.get("device_sn", "UNKNOWN")
        sw_ver = status_info.get("sw_version", "1.0.2.2")
        status_str = status_info.get("status", "ONLINE")
        bcharge = float(status_info.get("battery_soc", 100))
        load_watts = float(status_info.get("output_power_w", 0))
        nompower = 2000.0
        load_pct = round((load_watts / nompower) * 100.0, 1)
        time_left = float(status_info.get("time_left_min", 300.0))
        temp = float(status_info.get("temperature_c", 25.0))
        grid_in = float(status_info.get("input_power_w", 0))
        linev = 120.0 if status_str == "ONLINE" or grid_in > 0 else 0.0

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_str = START_TIME.strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "APC      : 001,036,0875\n",
            f"DATE     : {now_str}\n",
            "HOSTNAME : Unraid\n",
            "VERSION  : 3.14.14 (31 May 2016) slackware\n",
            f"UPSNAME  : SolixS2000\n",
            "CABLE    : Custom Cable Smart\n",
            f"MODEL    : {model}\n",
            "UPSMODE  : Stand Alone\n",
            f"STARTTIME: {start_str}\n",
            f"STATUS   : {status_str}\n",
            f"LINEV    : {linev:.1f} Volts\n",
            f"LOADPCT  : {load_pct:.1f} Percent\n",
            f"BCHARGE  : {bcharge:.1f} Percent\n",
            f"TIMELEFT : {time_left:.1f} Minutes\n",
            "MBATTCHG : 10 Percent\n",
            "MINTIMEL : 5 Minutes\n",
            "MAXTIME  : 0 Seconds\n",
            f"ITEMP    : {temp:.1f} C\n",
            "BATTV    : 48.0 Volts\n",
            f"LINEFREQ : 60.0 Hz\n",
            f"NOMPOWER : {int(nompower)} Watts\n",
            f"SERIALNO : {serial}\n",
            f"FIRMWARE : {sw_ver}\n",
            f"END APC  : {now_str}\n"
        ]

        for l in lines:
            send_nis_line(conn, l)
        
        # End packet (0 length)
        conn.sendall(struct.pack("!H", 0))
    except Exception as e:
        logger.debug(f"Client handling error: {e}")
    finally:
        conn.close()

def main():
    # Write PID file so Unraid's Dynamix UPS widget detects active daemon
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((BIND_HOST, BIND_PORT))
    server.listen(10)
    logger.info(f"Anker Solix NIS Server listening on {BIND_HOST}:{BIND_PORT} (PID {os.getpid()})...")

    while True:
        try:
            conn, addr = server.accept()
            handle_client(conn, addr)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Socket accept error: {e}")

    cleanup(None, None)

if __name__ == "__main__":
    main()
