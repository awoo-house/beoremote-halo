from typing import Tuple
from dataclasses import dataclass


@dataclass
class LightUpdate:
    hass_entity: str
    brightness: int
    hs_color: Tuple[float, float]
