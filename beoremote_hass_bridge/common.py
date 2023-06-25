from typing import Tuple

import asyncio
from dataclasses import dataclass
from datetime import datetime
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

@dataclass
class LightUpdate:
    hass_entity: str
    brightness: int
    hs_color: Tuple[float, float]






class RLQueue(asyncio.Queue):

    def __init__(self, messages_per_second: float = 1, maxsize: int = 0):
        logger.debug('RLQueue init.')
        super().__init__(maxsize=maxsize)
        self.message_delta = 1 / messages_per_second
        self.last_time = datetime.now()
        self.timeout_writer: asyncio.Task = None

    async def tw_run(self, message):
        await asyncio.sleep(self.message_delta)
        logger.debug('timeout_writer sending...')
        await super().put(message)

    async def put(self, message):
        delta = datetime.now() - self.last_time
        self.last_time = datetime.now()

        logger.debug('RLQueue put; delta is ' + str(delta.total_seconds()) + ' timeout is ' + str(self.message_delta))

        if self.timeout_writer is not None and not self.timeout_writer.done():
            logger.debug('cancelled timeout_writer')
            self.timeout_writer.cancel()

        if delta.total_seconds() <= self.message_delta:
            logger.debug('creating new timeout_writer')
            self.timeout_writer = asyncio.create_task(self.tw_run(message))
        else:
            await super().put(message)