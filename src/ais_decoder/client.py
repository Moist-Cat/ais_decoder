import asyncio
from http import HTTPStatus
from typing import Tuple
import os
import json
import urllib.parse

import socket

from ais_decoder.models import NMEASentence, ValidationError

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

class HTTPClient:
    """
    Asynchronous HTTP client.
    """
    
    def __init__(self, host, port, socket_host="localhost", socket_port=9999):
        super().__init__()
        self._socket_host = socket_host
        self._socket_port = socket_port
        self.server_url = urllib.parse.urlsplit(f"http://{host}:{port}/")

    async def _receive_msg(self):
        reader, writer = await asyncio.open_connection(self._socket_host, self._socket_port)
        data = await reader.read(100)
        msg = NMEASentence(data.decode())
        return msg 

    async def send_message(self):
        """Send messages from queue"""
        url = self.server_url
        msg = await self._receive_msg()
#        if url.scheme == 'https':
#            reader, writer = await asyncio.open_connection(
#                url.hostname, 443, ssl=True)
#        else:
        reader, writer = await asyncio.open_connection(
                url.hostname, url.port)

        data = json.dumps(msg.as_dict())
        query = (
            f"POST {url.path or '/'} HTTP/1.0\r\n"
            f"Host: {url.hostname}\r\n"
            f"User-Agent: python/requests2.0.1\r\n"
            f"Content-Length: {len(data)}\r\n"
            f"\r\n{data}\r\n"
        )

        writer.write(query.encode('latin-1'))
        line = await reader.readline()
        line = line.decode('latin1').rstrip()

        # Ignore the body, close the socket
        writer.close()

        return HTTPStatus(int(line.split(" ")[1]))

if __name__ == "__main__":
    import sys

    host, port = sys.argv[1:]
    cli = HTTPClient(host, int(port))

    asyncio.run(cli.send_message())
