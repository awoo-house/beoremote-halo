#!/usr/bin/env python3
import uuid

import jsons
import datetime

from .halo_raw import *



class ButtonBase:
    def get_configuration(self) -> Button:
        pass

    def handle_wheel(self, counts: int):
        pass

    def handle_btn_down(self):
        pass

    def handle_btn_up(self):
        pass

    def get_update(self):
        btn_dict = jsons.dump(self.get_configuration())
        btn_dict["type"] = "button"
        upd = {"update": btn_dict}
        # print(">>>> " + str(upd))
        return upd

def clamp(lower, upper, n): return max(lower, min(upper, n))

class Light(ButtonBase):
    def __init__(self, hass_entity, name = '', brightness = 0, on = True, default = False):
        self.__LONG_PRESS_DURATION__ = 0.5 # in seconds

        self.id = uuid.uuid4()
        self.hass_entity = hass_entity
        self.name = name
        self.brightness = brightness
        self.on = on
        self.hs_color = [0, 100]
        self.default = default

        self.mode = "brightness"

        self.down_time = None

    def get_configuration(self) -> Button:
        content = ButtonIconContent(
            "lights" if self.mode == "brightness" else "rgb_lights"
        )

        state = "active" if self.on else "inactive"

        [hue, _] = self.hs_color
        value = self.brightness if self.mode == "brightness" else round((hue / 360) * 100)

        return Button(self.name,
               content,
               default = self.default,
               id = self.id,
               value = value,
               state = state)

    def handle_wheel(self, counts: int):
        if self.mode == "brightness":
            self.brightness = clamp(0, 100, self.brightness + counts)
            self.on = self.brightness > 0
        else:
            [hue, sat] = self.hs_color
            self.hs_color = [clamp(0, 360, hue + (counts * 3.6)), sat]

    def handle_btn_down(self):
        self.down_time = datetime.datetime.now()
        pass

    def handle_btn_up(self):
        now = datetime.datetime.now()
        press_duration = now - self.down_time
        self.down_time = None

        if(press_duration.total_seconds() >= self.__LONG_PRESS_DURATION__):
            self.mode = "hue" if self.mode == "brightness" else "brightness"

        else:
            self.on = not self.on
