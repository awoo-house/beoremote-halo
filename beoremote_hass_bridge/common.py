from typing import Tuple, Literal

import asyncio
from dataclasses import dataclass
from datetime import datetime
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

@dataclass
class LightState:
    hass_entity: str
    state: Literal["on", "off"]
    friendly_name: str | None = None
    color_mode: Literal['color_temp', 'rgb'] = 'color_temp'
    color_temp: int = 443
    hs_color: list[float] | None = None
    brightness: int | None = None

    @classmethod
    def from_ha_event(cls, evt):
        attrs = evt['attributes']

        match attrs.get('color_mode'):
            case None | 'color_temp':
                color_mode = 'color_temp'

            case _:
                color_mode = 'rgb'

        return LightState(
            hass_entity=evt['entity_id'],
            state=evt['state'],
            friendly_name=attrs['friendly_name'],
            color_mode = color_mode,
            color_temp = attrs.get('color_temp') or 443,
            hs_color = attrs.get('hs_color') or [0, 100],
            brightness = attrs.get('brightness') or 0
        )


@dataclass
class GetStatesFor:
    hass_entities: list[str]

################################################################################

class RLQueue(asyncio.Queue):
    def __init__(self, messages_per_second: float = 1, maxsize: int = 0):
        logger.debug('RLQueue init.')
        super().__init__(maxsize=maxsize)
        self.message_delta = 1 / messages_per_second
        self.last_time = datetime.now()
        self.timeout_writer: asyncio.Task | None = None
        self.latest_message = None

    def force_put_nowait(self, msg):
        super().put_nowait(msg)

    async def force_put(self, msg):
        await super().put(msg)

    async def tw_run(self):
        await asyncio.sleep(self.message_delta)
        logger.debug('timeout_writer sending...')
        await super().put(self.latest_message)

    async def put(self, message):
        delta = datetime.now() - self.last_time

        self.latest_message = message
        self.last_time = datetime.now()

        logger.debug('RLQueue put; delta is ' + str(delta.total_seconds()) + ' timeout is ' + str(self.message_delta))

        # if self.timeout_writer is not None and not self.timeout_writer.done():
        #     logger.debug('cancelled timeout_writer')
        #     self.timeout_writer.cancel()

        if delta.total_seconds() <= self.message_delta:
            if self.timeout_writer is None:
                logger.debug('[None branch] creating new timeout_writer')
                self.timeout_writer = asyncio.create_task(self.tw_run())
            elif self.timeout_writer.done():
                logger.debug('[Done branch] creating new timeout_writer')
                self.timeout_writer = asyncio.create_task(self.tw_run())
            else:
                logger.debug('waiting for timeout_writer to stop.')
        else:
            await super().put(message)