#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

import hass
import beoremote_halo as halo



async def main():
    await hass.ws.init(os.getenv("HA_WS_API"))
    pass


if __name__ == "__main__":
    asyncio.run(main())