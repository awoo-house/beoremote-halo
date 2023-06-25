#!/usr/bin/env python3
import asyncio
import jsons
import json
import coloredlogs, logging
import pprint
from datetime import datetime

from typing import Any

from beoremote_hass_bridge.common import LightState
import websockets as ws

from .buttons import Light, ButtonBase
from .halo_raw import Configuration, Page

pp = pprint.PrettyPrinter(width=80)

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

last_sent_time = datetime.now()

async def handle_halo_events(websocket, pages: dict[str, list[Any]], halo_to_hass: asyncio.Queue):
    global last_sent_time

    logger.debug("Halo Connected!")

    btn_map = {}
    pgs = []

    for name, buttons in pages.items():
        for btn in buttons:
            btn_map[str(btn.id)] = btn

        pgs.append(Page(
            name, [ btn.get_configuration() for btn in buttons ]
        ))

    logger.debug(pp.pformat(Configuration(pgs)))
    jcon = jsons.dumps(Configuration(pgs))
    await websocket.send(str(jcon))

    while True:
        message = json.loads(await websocket.recv())
        # logger.debug(message)

        if "event" in message:
            evt = message["event"]

            match evt["type"]:
                case "wheel":
                    btn_id = evt["id"]
                    if btn_id not in btn_map:
                        logger.error("ERROR! Button " + btn_id + "not in button map: " + str(btn_map))
                    else:
                        btn: Light = btn_map[btn_id]
                        btn.handle_wheel(evt["counts"])
                        await websocket.send(jsons.dumps(btn.get_update()))

                        last_sent_time = datetime.now()
                        await halo_to_hass.put(btn.light)

                case "button":
                    btn_id = evt["id"]
                    if btn_id not in btn_map:
                        logger.error("ERROR! Button " + btn_id + "not in button map: " + str(btn_map))
                    else:
                        btn: Light = btn_map[btn_id]
                        if evt['state'] == 'pressed':
                            btn.handle_btn_down()
                            await websocket.send(jsons.dumps(btn.get_update()))
                        else:
                            btn.handle_btn_up()
                            await halo_to_hass.put(btn.light)
                            await websocket.send(jsons.dumps(btn.get_update()))

                case 'status':
                    if evt['state'] == 'error':
                        logger.error(evt['message'])
                    # else:
                    #     logger.info(pp.pformat(evt))

                case 'system':
                    logger.info(evt)

                case 'power':
                    logger.info(evt)

                case other:
                    logger.warning("Don't know how to handle event:\n" + pprint.pformat(evt))

        else:
            logger.warning("Don't know how to handle MESSAGE:\n" + pprint.pformat(message))

async def handle_hass_to_halo(hass_to_halo: asyncio.Queue, pages: dict[str, list[Any]], websocket):
    global last_sent_time

    btn_map = {}
    for name, buttons in pages.items():
        for btn in buttons:
            btn_map[str(btn.hass_entity())] = btn

    logger.debug(btn_map)

    while True:
        msg = await hass_to_halo.get()
        logger.debug("Got hass event!")
        logger.debug(msg)

        match msg:
            case LightState(hass_entity=hass_entity) as lu:
                delta = (datetime.now() - last_sent_time).total_seconds()
                if delta <= 10.0:
                    logger.debug('ignoring hass event')
                    continue
                else:
                    logger.debug('receiving hass event; delta is: ' + str(delta))

                if hass_entity in btn_map:
                    match btn_map[hass_entity]:
                        case Light() as light:
                            logger.debug('updating light from hass!')
                            logger.debug(pprint.pformat(lu))
                            light.light = lu

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
