from typing import Tuple
import os
import json

from requests import Session
import socket

from ais_decoder.models import NMEASentence, ValidationError
from ais_decoder.settings import HOST, PORT

class TCPClient:

    def __init__(self, ip: str=None, port: int=None) -> Tuple[int, str]:
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

class HTTPClient(Session):
    server_url: str = f"http://{HOST}:9999"
    messages: list = []
    _last_response = None

    def get_message(self):
        res = self.get(self.server_url)
        self._last_response = res
        try:
            msg = NMEASentence(res.text)
        except ValidationError:
            pass
        else:
            self.messages.append(msg)
        return res

    def send_message(self):
        res = self.post(self.server_url, json=self.messages.pop().as_dict())
        self._last_response = res

        return res

if __name__ == "__main__":
    cli = HTTPClient()
    print(cli.get_message())
    print(cli.send_message())
