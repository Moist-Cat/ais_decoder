"""
Commands to manage the package.

Currently:
    runserver:
        run the socket server

    send [message]:
        Send a message to the server
"""

import sys

from ais_decoder.client import HTTPClient
from ais_decoder.server import runserver


def get_command(args = sys.argv[1:]):
    """Get command and args from the comand line"""
    command = args[0]
    if len(args) > 1:
        arg = args[1]

    if command == "runserver":
        runserver()
    elif command == "send":
        c = HTTPClient()
        c.get_message()
        print(c.send_message())
