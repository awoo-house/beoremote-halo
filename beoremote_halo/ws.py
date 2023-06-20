#!/usr/bin/env python3
import asyncio
from websockets.client import connect

from .light import Light

async def init(uri: str):
    lamp = Light()

    # async for websocket in connect(uri):
    #     try:
    #         print("Ok!")

    #         async for message in websocket:
    #             print(message)

    #     except websockets.ConnectionClosed:
    #         print("Error!")
    #         await asyncio.sleep(1)
    #         continue
