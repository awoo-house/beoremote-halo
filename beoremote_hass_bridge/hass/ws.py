#!/usr/bin/env python3
import asyncio
import jsons
import json
import os
import pprint

from dotenv import load_dotenv
load_dotenv()

from typing import Any
import websockets as ws

from .cursed_client import HA

pp = pprint.PrettyPrinter(width=70)



async def handle(websocket):
    ha = HA(websocket)

    while True:
        message = json.loads(await websocket.recv())
        match message['type']:
            case "auth_required":
                print('Connected to HA v' + message['ha_version'])
                await websocket.send(
                    json.dumps({
                        'type': 'auth',
                        'access_token': os.getenv('HA_AUTH_TOKEN')
                    }))

            case "auth_ok":
                # Time to subscribe to what we want...
                await ha.subscribe_events(event_type='state_changed')

            case other:
                print("Don't know what to do with message...")
                pp.pprint(message)


async def init(uri: str):
    async with ws.connect(uri) as websocket:
        await handle(websocket)
