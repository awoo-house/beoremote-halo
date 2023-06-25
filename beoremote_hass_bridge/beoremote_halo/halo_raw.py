#!/usr/bin/env python3
from typing import Literal
from dataclasses import dataclass
import uuid

@dataclass
class Configuration:
    def __init__(self, pages):
        self.configuration = {"id": uuid.uuid4(), "version": "1.0.1", "pages": pages}

@dataclass
class Page:
    title: str
    buttons: list
    id: uuid.UUID = uuid.uuid4()

@dataclass
class Button:
    id: uuid.UUID
    title: str
    content: object
    subtitle: str = ''
    value: int = 0
    state: Literal['active', 'inactive'] = 'active'
    default: bool = False

@dataclass
class ButtonTextContent:
    text: str

@dataclass
class ButtonIconContent:
    icon: str
