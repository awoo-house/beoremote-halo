#!/usr/bin/env python3
import asyncio
import jsons
import json
import coloredlogs, logging

from typing import Any

import websockets as ws

from .buttons import Light, ButtonBase
from .halo_raw import Configuration, Page

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


async def handle_halo_events(websocket, pages: dict[str, list[Any]], halo_to_hass: asyncio.Queue):
    logger.debug("Halo Connected!")

    btn_map = {}
    pgs = []

    for name, buttons in pages.items():
        for btn in buttons:
            btn_map[str(btn.id)] = btn

        pgs.append(Page(
            name, [ btn.get_configuration() for btn in buttons ]
        ))

    jcon = jsons.dumps(Configuration(pgs))
    await websocket.send(jcon)

    while True:
        message = json.loads(await websocket.recv())
        # logger.debug(message)

        if "event" in message:
            evt = message["event"]

            match evt["type"]:
                case "wheel":
                    btn_id = evt["id"]
                    if btn_id not in btn_map:
                        print("ERROR! Button " + btn_id + "not in button map: " + str(btn_map))
                    else:
                        btn = btn_map[btn_id]
                        btn.handle_wheel(evt["counts"])
                        await websocket.send(jsons.dumps(btn.get_update()))

                case "button":
                    btn_id = evt["id"]
                    if btn_id not in btn_map:
                        print("ERROR! Button " + btn_id + "not in button map: " + str(btn_map))
                    else:
                        btn = btn_map[btn_id]
                        if evt['state'] == 'pressed':
                            btn.handle_btn_down()
                            await websocket.send(jsons.dumps(btn.get_update()))
                        else:
                            btn.handle_btn_up()
                            await websocket.send(jsons.dumps(btn.get_update()))


                case other:
                    pass


async def handle_hass_to_halo(hass_to_halo: asyncio.Queue, pages: dict[str, list[Any]], websocket):
    btn_map = {}
    for name, buttons in pages.items():
        for btn in buttons:
            btn_map[str(btn.name)] = btn

    logger.debug(btn_map)

    while True:
        msg = await hass_to_halo.get()
        logger.debug("Got hass event!")
        logger.debug(msg)

        match msg['type']:
            case 'light_update':
                if msg['hass_entity'] in btn_map:
                    attrs = msg['attributes']
                    match btn_map[msg['hass_entity']]:
                        case Light() as light:
                            if 'brightness' in attrs:
                                light.brightness = round((attrs['brightness'] / 255) * 100)
                                light.on = True
                            else:
                                light.brightness = 0
                                light.on = False

                            msg = jsons.dumps(light.get_update())
                            logger.debug("Sending updated light state: " + msg)
                            await websocket.send(msg)

                

async def init(uri: str, pages: dict[str, list[Any]], halo_to_hass: asyncio.Queue, hass_to_halo: asyncio.Queue):
    logger.debug('beoremote init')

    async with ws.connect(uri, ping_timeout=None) as websocket:
        logger.info('beoremote connected')
        async with asyncio.TaskGroup() as tg:
            halo_events = tg.create_task(handle_halo_events(websocket, pages, halo_to_hass))
            hass_events = tg.create_task(handle_hass_to_halo(hass_to_halo, pages, websocket))

        logger.error('tasks completed.')
