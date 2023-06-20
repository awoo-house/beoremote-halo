#!/usr/bin/env python3
import uuid

import jsons

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
        print(">>>> " + str(upd))
        return upd



class Light(ButtonBase):
    def __init__(self, name, brightness = 55, on = True):
        self.id = uuid.uuid4()
        self.name = name
        self.brightness = brightness
        self.on = on
        self.default = True

    def get_configuration(self) -> Button:
        content = ButtonIconContent("lights")

        state = "active" if self.on else "inactive"

        return Button(self.name,
               content,
               id = self.id,
               value = self.brightness,
               state = state)

    def handle_wheel(self, counts: int):
        self.brightness = self.brightness + counts
        pass

    def handle_btn_down(self):
        pass

    def handle_btn_up(self):
        # If short press
        self.on = not self.on
        print(self.on)
        pass
