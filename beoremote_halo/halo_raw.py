#!/usr/bin/env python3
from dataclasses import dataclass
import uuid

@dataclass
class Configuration:
    def __init__(self, pages):
        self.configuration = {"id": uuid.uuid4(), "version": "1.0.1", "pages": pages}

@dataclass
class Page:
    def __init__(self, title, buttons):
        self.id = uuid.uuid4()
        self.title = title
        self.buttons = buttons

@dataclass
class Button:
    def __init__(self, title, content, id = uuid.uuid4(), subtitle = "", value = 0, state = "active"):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.value = value
        self.state = state
        self.content = content

@dataclass
class ButtonTextContent:
    def __init__(self, text):
        self.text = text

@dataclass
class ButtonIconContent:
    def __init__(self, icon):
        self.icon = icon
