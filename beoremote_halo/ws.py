#!/usr/bin/env python3
import asyncio
import jsons
import json

from typing import Any

import websockets as ws

from .light import Light
from .halo_raw import Configuration, Page


async def handle(websocket, pages: dict[str, list[Any]]):
    print("Connected!")

    btnMap = {}

    pgs = []
    for name, buttons in pages.items():
        for btn in buttons:
            btnMap[str(btn.id)] = btn

        pgs.append(Page(
            name, [ btn.get_configuration() for btn in buttons ]
        ))

    jcon = jsons.dumps(Configuration(pgs))
    await websocket.send(jcon)

    while True:
        message = json.loads(await websocket.recv())
        # print(message)

        if "event" in message:
            evt = message["event"]

            match evt["type"]:
                case "wheel":
                    btn_id = evt["id"]
                    if btn_id not in btnMap:
                        print("ERROR! Button " + btn_id + "not in button map: " + str(btnMap))
                    else:
                        btn = btnMap[btn_id]
                        btn.handle_wheel(evt["counts"])
                        await websocket.send(jsons.dumps(btn.get_update()))

                case "button":
                    btn_id = evt["id"]
                    if btn_id not in btnMap:
                        print("ERROR! Button " + btn_id + "not in button map: " + str(btnMap))
                    else:
                        btn = btnMap[btn_id]
                        if evt['state'] == 'pressed':
                            btn.handle_btn_down()
                            await websocket.send(jsons.dumps(btn.get_update()))
                        else:
                            btn.handle_btn_up()
                            await websocket.send(jsons.dumps(btn.get_update()))


                case other:
                    pass



async def init(uri: str, pages: dict[str, list[Any]]):
    async with ws.connect(uri) as websocket:
        await handle(websocket, pages)
