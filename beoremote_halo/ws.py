#!/usr/bin/env python3
import asyncio
import jsons

import websockets as ws

from .light import Light
from .halo_raw import Configuration


async def handle(websocket, conf: Configuration):
    print("Connected!")
    jcon = jsons.dumps(conf)
    print(jcon)
    await websocket.send(jcon)

    while True:
        message = await websocket.recv()
        print(message)



async def init(uri: str, conf: Configuration):
    async with ws.connect(uri) as websocket:
        await handle(websocket, conf)
