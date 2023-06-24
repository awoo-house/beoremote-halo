#!/usr/bin/env python3
import asyncio
import sys

sys.path.append('.') # cursed.

from dotenv import load_dotenv
load_dotenv()

import beoremote_halo.ws as halo
from beoremote_halo.light import Light
import beoremote_halo.halo_raw as raw

import jsons

print(halo)

async def main():
    pages = {
        "Lighting!": [
            Light("Living Room"),
            Light("Fox's Bedroom")
        ]
    }


    await halo.init("ws://10.0.0.61:8080", pages)

if __name__ == "__main__":
    asyncio.run(main())
