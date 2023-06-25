import asyncio
import aiohttp

import os
from urllib.parse import urlparse, urlunparse

from common import RLQueue, LightUpdate

async def initialize(_to_hass: RLQueue, entity_id: str) -> None:
    uri = urlunparse(urlparse(os.getenv('HA_URI'))._replace(path="/api/states/%s" % entity_id))
    print(uri)

    headers = {
        'Authorization': 'Bearer %s' % os.getenv('HA_AUTH_TOKEN'),
        'content-type': 'application/json'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(uri) as resp:
            print(resp.status)
            body = await resp.json()
            print(body)

            await _to_hass.force_put(LightUpdate(
                hass_entity=entity_id,
                state=body.get('state'),
                hs_color=body['attributes'].get('hs_color'),
                brightness=body['attributes'].get('brightness')
            ))