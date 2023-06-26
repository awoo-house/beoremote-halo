#!/usr/bin/env python3
import uuid

from dataclasses import replace
import jsons
import datetime

from .halo_raw import *
from beoremote_hass_bridge.common import LightState

LONG_PRESS_DURATION = 0.5

class ButtonBase:
    def hass_entity(self) -> str | None:
        pass

    def get_configuration(self) -> Button | None:
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

def clamp(lower, upper, n): return max(lower, min(upper, n))

def pct(out_max: float, in_max: float, n: float) -> int:
    return round((n / in_max) * out_max)

class Light(ButtonBase):
    def __init__(self, light_state: LightState, default = False) -> None:
        self.light: LightState = light_state
        self.down_time: datetime | None = None
        self.default = default
        self.id: uuid.UUID = uuid.uuid4()

    def mk_light(hass_entity: str, default = False):
        return Light(LightState(
            hass_entity=hass_entity,
            friendly_name='',
            state='on'
        ), default=default)

    def hass_entity(self) -> str:
        return self.light.hass_entity

    def get_configuration(self) -> Button:
        match self.light.color_mode:
            case 'color_temp':
                content = ButtonIconContent("lights")
                return Button(
                    id=self.id,
                    title=self.light.friendly_name,
                    content=content,
                    value=pct(100, 255, self.light.brightness),
                    state='active' if self.light.state == 'on' else 'inactive',
                    default=self.default
                )

            case 'rgb':
                content = ButtonIconContent("rgb_lights")
                print(self.light.hs_color)
                [hue, _] = self.light.hs_color
                return Button(
                    id=self.id,
                    title = self.light.friendly_name,
                    content=content,
                    value=pct(100, 360, hue),
                    state='active' if self.light.state == 'on' else 'inactive',
                    default=self.default
                )

    def handle_wheel(self, counts: int):
        if self.light.color_mode == 'color_temp':
            self.light = replace(
                self.light,
                brightness = clamp(0, 255, self.light.brightness + (counts * 2.5)),
                state = 'on' if self.light.brightness > 0 else 'off'
            )

        else:
            [hue, sat] = self.light.hs_color
            self.light = replace(
                self.light,
                hs_color = [clamp(0, 360, hue + (counts * 3.6)), sat]
            )

    def handle_btn_down(self):
        self.down_time = datetime.datetime.now()
        pass

    def handle_btn_up(self):
        now = datetime.datetime.now()
        press_duration = now - self.down_time
        self.down_time = None

        if(press_duration.total_seconds() >= LONG_PRESS_DURATION):
            match self.light.color_mode:
                case 'color_temp':
                    self.light = replace(
                        self.light,
                        color_mode='rgb'
                    )

                case 'rgb':
                    self.light = replace(
                        self.light,
                        color_mode='color_temp'
                    )

        else:
            newState = "on" if self.light.state == 'off' else 'off'
            self.light = replace(self.light, state = newState)
