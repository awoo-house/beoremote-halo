#!/usr/bin/env python3
import logging
import os
import signal
import asyncio
from dotenv import load_dotenv
load_dotenv()

import hass
import beoremote_halo as halo



async def main():
    pages = {
        "Lighting!": [
            halo.buttons.Light("light.hue_color_lamp_1", default=True),
            halo.buttons.Light("Fox's Bedroom")
        ]
    }

    async with asyncio.TaskGroup() as tg:
        halo_to_hass = asyncio.Queue()
        hass_to_halo = asyncio.Queue()

        hass_task = tg.create_task(hass.ws.init(os.getenv("HA_WS_API"), ["light.hue_color_lamp_1"], halo_to_hass, hass_to_halo))
        halo_task = tg.create_task(halo.ws.init("ws://10.0.0.61:8080", pages, halo_to_hass, hass_to_halo))

        def handler(signum, frame):
            hass_task.cancel()
            halo_task.cancel()
            exit(0)

        signal.signal(signal.SIGINT, handler)


if __name__ == "__main__":
    asyncio.run(main())