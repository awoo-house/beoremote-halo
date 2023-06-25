import json

class HA:
    def __init__(self, ws):
        self.msg_id = 0
        self.ws = ws

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            kwargs['type'] = name
            return self.send(kwargs)
        return _missing

    async def send(self, msg):
        self.msg_id += 1
        msg['id'] = self.msg_id
        await self.ws.send(json.dumps(msg))
