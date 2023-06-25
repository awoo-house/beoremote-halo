#!/usr/bin/env python3
import asyncio


import hass
import beoremote_halo as halo




async def main():
    await hass.ws.init()
    pass


if __name__ == "__main__":
    asyncio.run(main())