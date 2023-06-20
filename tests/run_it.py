#!/usr/bin/env python3
import asyncio



import sys
sys.path.append('.') # cursed.

import beoremote_halo.ws as halo
from beoremote_halo.light import Light
import beoremote_halo.halo_raw as raw

import jsons

print(halo)

async def main():
    conf = raw.Configuration([
        raw.Page("Lighting", [
            Light("Living Room").get_configuration()
        ])
    ])
    await halo.init("ws://10.0.0.61:8080", conf)

if __name__ == "__main__":
    asyncio.run(main())
