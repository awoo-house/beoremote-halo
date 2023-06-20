#!/usr/bin/env python3
import asyncio



import sys
sys.path.append('.') # cursed.

import beoremote_halo.ws as halo
import beoremote_halo.halo_raw as raw

import jsons

print(halo)

async def main():
    await halo.init("ws://10.0.0.61:8080")

if __name__ == "__main__":
    # asyncio.run(main())
    conf = raw.Configuration([])
    print(jsons.dump(conf))
