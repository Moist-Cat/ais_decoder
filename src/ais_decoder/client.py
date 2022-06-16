from typing import Tuple
import os
import json

import socket

from ais_decoder.models import NMEASentence, ValidationError

class Client():

    def __init__(self, ip: str, port: int) -> Tuple[int, str]:
        self.ip= ip or os.environ.get("AIS_SERVER_URL", "localhost")
        self.port = port or os.environ.get("AIS_SERVER_PORT", 9999)

        self._response = None

    def send(self, data) -> Tuple[int, str]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.ip, self.port))
            try:
                msg = NMEASentence(data)
            except ValidationError as exc:
                return (400, str(exc))

            sock.sendall(bytes(json.dumps(msg.as_dict()), "ascii"))
            status, text = str(sock.recv(1024), "ascii").split(",")

            return (int(status), text)
