#!/usr/bin/env python3
import uuid

from .halo_raw import *

class Light:
    def __init__(self, name, brightness = 55, state = "on"):
        self.id = uuid.uuid4()
        self.name = name
        self.brightness = brightness
        self.state = state

    def get_configuration(self) -> Button:
        content = ButtonIconContent("lights")

        state = "active" if self.state == "on" else "inactive"

        return Button(self.name,
               content,
               id = self.id,
               value = self.brightness,
               state = state)
