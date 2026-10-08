#!/usr/bin/env python3
"""
CLI helper for Anker Solix credentials verification
"""

import sys
import json
import asyncio
import argparse
import aiohttp
from anker_solix_api import api, poller

async def test_credentials(user, password, country):
    async with aiohttp.ClientSession() as session:
        client = api.AnkerSolixApi(
            email=user,
            password=password,
            countryId=country,
            websession=session
        )
        await client.update_sites()
        await poller.poll_device_details(client)
        
        dev_count = len(client.devices)
        if dev_count > 0:
            dev_names = [d.get("name", sn) for sn, d in client.devices.items()]
            return {
                "success": True,
                "message": f"Authentication successful! Found {dev_count} device(s): {', '.join(dev_names)}."
            }
        else:
            return {
                "success": True,
                "message": "Authentication successful, but no devices are bound to this account."
            }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--country", default="us")
    args = parser.parse_args()

    try:
        result = asyncio.run(test_credentials(args.user, args.password, args.country))
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "message": f"Authentication failed: {str(e)}"
        }))

if __name__ == "__main__":
    main()
