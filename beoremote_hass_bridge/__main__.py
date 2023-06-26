#!/usr/bin/env python3
import logging
from urllib.parse import urlparse, urlunparse
import os
import signal
import asyncio
from dotenv import load_dotenv
load_dotenv()

from beoremote_hass_bridge.common import RLQueue, GetStatesFor

import beoremote_hass_bridge.hass as hass
import beoremote_hass_bridge.hass.ws as hass_ws
import beoremote_hass_bridge.beoremote_halo.ws as halo_ws
import beoremote_hass_bridge.beoremote_halo.buttons as halo_buttons



async def main():
    hass_uri = urlparse(os.getenv("HA_URI"))
    hass_ws_uri = None
    if hass_uri.scheme == 'https':
        hass_ws_uri = hass_uri._replace(scheme = 'wss')
    else:
        hass_ws_uri = hass_uri._replace(scheme = 'ws')

    hass_ws_uri = hass_ws_uri._replace(path = '/api/websocket')


    pages = {
        "Den Lighting": [
            halo_buttons.Light.mk_light("light.hue_color_lamp_1", default = True),
            halo_buttons.Light.mk_light("light.foxs_bedroom")
        ]
    }

    await hass.initialize(pages)

    async with asyncio.TaskGroup() as tg:
        halo_to_hass = RLQueue(messages_per_second=3)
        hass_to_halo = RLQueue(messages_per_second=3)

        hass_task = tg.create_task(hass_ws.init(urlunparse(hass_ws_uri), ["light.hue_color_lamp_1"], halo_to_hass, hass_to_halo))
        halo_task = tg.create_task(halo_ws.init(os.getenv("BEOREMOTE_HALO_URI"), pages, halo_to_hass, hass_to_halo))

        def handler(signum, frame):
            hass_task.cancel()
            halo_task.cancel()
            exit(0)

        signal.signal(signal.SIGINT, handler)



if __name__ == "__main__":
    asyncio.run(main())