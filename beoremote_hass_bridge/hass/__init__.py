import asyncio
import aiohttp

import os
from urllib.parse import urlparse, urlunparse

from beoremote_hass_bridge.common import LightState
from beoremote_hass_bridge.beoremote_halo.buttons import ButtonBase, Light

import pprint
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

pp = pprint.PrettyPrinter(width = 80)

async def get_state(entity_id: str) -> dict:
    uri = urlunparse(urlparse(os.getenv('HA_URI'))._replace(path="/api/states/%s" % entity_id))

    headers = {
        'Authorization': 'Bearer %s' % os.getenv('HA_AUTH_TOKEN'),
        'content-type': 'application/json'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(uri) as resp:
            return await resp.json()

async def initialize(pages: dict[str, list[ButtonBase]]) -> None:
    print(pages)
    for page, buttons in pages.items():
        for button in buttons:
            match button:
                case Light() as l:
                    state = await get_state(l.hass_entity())
                    logger.info("Got state for %s / %s", page, l.hass_entity())
                    logger.debug(pprint.pformat(state))

                    l.light = LightState.from_ha_event(state)