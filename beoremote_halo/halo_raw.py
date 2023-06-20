#!/usr/bin/env python3
from dataclasses import dataclass
import uuid

@dataclass
class Configuration:
    def __init__(self, pages):
        self.id = uuid.uuid4()
        self.version = "1.0.1"
        self.pages = pages

@dataclass
class Page:
    def __init__(self, title, buttons):
        self.id = uuid.uuid4()
        self.title = title
        self.buttons = buttons

@dataclass
class Button:
    def __init__(self, title, content, state = "active"):
        self.id = uuid.uuid4()
        self.title = title
        self.subtitle = ""
        self.value = 0
        self.state = state
        self.content = content

@dataclass
class ButtonTextContent:
    def __init__(self, text):
        self.text = text

@dataclass
class ButtonIconContext:
    def __init__(self, icon):
        self.icon = icon
