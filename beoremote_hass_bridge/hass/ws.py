#!/usr/bin/env python3
import asyncio
import jsons
import json
import os
import pprint
import coloredlogs, logging

from beoremote_hass_bridge.common import LightUpdate

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

from dotenv import load_dotenv
load_dotenv()

from typing import Any
import websockets as ws

from .cursed_client import HA

pp = pprint.PrettyPrinter(width=80)

async def handle_hass(websocket, ha_entities: list, halo_to_hass: asyncio.Queue, hass_to_halo: asyncio.Queue):
    ha = HA(websocket)

    while True:
        message = json.loads(await websocket.recv())
        # logger.debug(pp.pformat(message))

        match message['type']:
            case "auth_required":
                logger.info('Connected to HA v' + message['ha_version'])
                await websocket.send(
                    json.dumps({
                        'type': 'auth',
                        'access_token': os.getenv('HA_AUTH_TOKEN')
                    }))

            case "auth_ok":
                # Time to subscribe to what we want...
                await ha.subscribe_events(event_type='state_changed')

            case "event":
                dat = message['event']['data']
                ctx = message['event']['context']['id']

                if dat['entity_id'] in ha_entities:
                    # logger.debug("Light Update[" + str(message['id']) + "]!\n" + pp.pformat(dat))
                    attrs = dat['new_state']['attributes']

                    await hass_to_halo.put(LightUpdate(dat['entity_id'],
                        brightness = attrs.get('brightness'),
                        hs_color = attrs.get('hs_color')
                    ))

            case other:
                logger.warning("Don't know what to do with message...\n" + pp.pformat(message))

async def handle_halo_to_hass(halo_to_hass: asyncio.Queue, websocket):
    ha = HA(websocket)

    while True:
        msg = await halo_to_hass.get()
        logger.debug("Got halo event!")
        logger.debug(msg)

        match msg:
            case LightUpdate() as lu:
                params = {}
                if lu.brightness is not None:
                    params['brightness'] = lu.brightness

                if lu.brightness_step is not None:
                    params['brightness_step'] = lu.brightness_step

                if lu.hs_color is not None:
                    params['hs_color'] = lu.hs_color

                logger.info("Will send message id: " + str(ha.msg_id + 1))

                await ha.call_service(
                    domain = 'light',
                    service = 'turn_on',
                    service_data = params,
                    target = { 'entity_id': lu.hass_entity }
                )

    

async def init(uri: str, ha_entities: list, halo_to_hass: asyncio.Queue, hass_to_halo: asyncio.Queue):
    async with ws.connect(uri, ping_timeout=None) as websocket:
        async with asyncio.TaskGroup() as tg:
            hass_events = tg.create_task(handle_hass(websocket, ha_entities, halo_to_hass, hass_to_halo))
            halo_events = tg.create_task(handle_halo_to_hass(halo_to_hass, websocket))
