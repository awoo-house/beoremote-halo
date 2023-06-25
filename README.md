# Building

To make sure the dependencies are installed, used [poetry][]

    $ poetry install

Then, you can drop into a poetry shell with

    $ poetry shell

and work as normal, e.g.

    $ python tests/run_it.py

# Necessary Environment Variables

When running locally, `beoremote_hass_bridge` will respect a `.env` file; make sure you have

    HA_WS_API=wss://wherever.ha-is.com/api/websocket
    HA_AUTH_TOKEN=token

set.



[poetry]: https://python-poetry.org/