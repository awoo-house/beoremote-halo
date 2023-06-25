#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.') # cursed.

import hass.ws as hass_ws

if __name__ == "__main__":
    asyncio.run(hass_ws.init("wss://ha.fox-den.boston/api/websocket"))
    pass
