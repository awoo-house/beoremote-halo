import asyncio
import jsons
import json
import os
import pprint
import coloredlogs, logging

from beoremote_hass_bridge.common import LightState, GetStatesFor

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

from dotenv import load_dotenv
load_dotenv()

from typing import Any
import websockets as ws

from .cursed_client import HA

pp = pprint.PrettyPrinter(width=80)



async def authenticate(websocket):
    while True:
        message = json.loads(await websocket.recv())

        match message['type']:
            case "auth_required":
                logger.info('Connected to HA v' + message['ha_version'])
                await websocket.send(
                    json.dumps({
                        'type': 'auth',
                        'access_token': os.getenv('HA_AUTH_TOKEN')
                    }))

            case "auth_ok":
                logger.info('Authentication Successful!')
                return

            case msg:
                logger.warning("Unexpected Message!\n" + pp.pformat(msg))



async def handle_hass(websocket, ha_entities: list, halo_to_hass: asyncio.Queue, hass_to_halo: asyncio.Queue):
    ha = HA(websocket)

    await ha.subscribe_events(event_type='state_changed')
    logger.debug('subscribed to events, starting recv loop.')

    while True:
        message = json.loads(await websocket.recv())
        logger.debug(pp.pformat(message))

        match message['type']:
            case "event":
                dat = message['event']['data']
                await hass_to_halo.put(LightState.from_ha_event(dat['new_state']))

            case other:
                pass
                # logger.warning("Don't know what to do with message...\n" + pp.pformat(message))

async def handle_halo_to_hass(halo_to_hass: asyncio.Queue, websocket):
    ha = HA(websocket)

    while True:
        msg = await halo_to_hass.get()
        logger.debug("Got halo event!")
        # logger.debug(msg)

        match msg:
            case LightState(hass_entity=hass_entity, state='off') as lu:
                await ha.call_service(
                    domain = 'light',
                    service = 'turn_off',
                    target = { 'entity_id': lu.hass_entity }
                )

            case LightState(hass_entity=hass_entity, state='on') as lu:
                params = {}

                if lu.brightness is not None:
                    params['brightness'] = lu.brightness

                match lu.color_mode:
                    case 'color_temp':
                        # params['color_mode'] = 'color_temp'
                        params['color_temp'] = lu.color_temp
                        pass

                    case 'rgb':
                        if lu.hs_color is not None:
                            params['hs_color'] = lu.hs_color

                logger.debug("sending update for " + lu.hass_entity)
                await ha.call_service(
                    domain = 'light',
                    service = 'turn_on',
                    service_data = params,
                    target = { 'entity_id': lu.hass_entity }
                )

            case o:
                logger.error('unhandled internal event')
                logger.error(pp.pformat(o))


async def init(uri: str, ha_entities: list, halo_to_hass: asyncio.Queue, hass_to_halo: asyncio.Queue):
    async with ws.connect(uri, ping_timeout=None) as websocket:
        await authenticate(websocket)
        logger.debug('authed, starting next tasks')

        async with asyncio.TaskGroup() as tg:
            hass_events = tg.create_task(handle_hass(websocket, ha_entities, halo_to_hass, hass_to_halo))
            halo_events = tg.create_task(handle_halo_to_hass(halo_to_hass, websocket))
