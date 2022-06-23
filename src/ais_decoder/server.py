from io import BytesIO
from uuid import uuid4
import socketserver
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

with open("nmea-sample.txt", "r+b") as file:
    data = file.readlines()

class TCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(f"received {self.data}")
        try:
            jdata = ",".join(dict(json.loads(self.data)).values())
        except json.decoder.JSONDecodeError:
            return self.request.sendall(b"400,JSON decode error")

        with open("nmea-sample.txt", "a") as file:
            file.write(jdata + "\n")
        return self.request.sendall(b"201,")


class HTTPHandler(BaseHTTPRequestHandler):
    data = data 

    def read_data(self):
        payload_len = int(self.headers.get("Content-Length"))
        return self.rfile.read(payload_len)

    def do_GET(self):
        string = data.pop()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(string)

    def do_POST(self):
        buffer = self.read_data()

        with open(str(uuid4()) + ".json", "w") as file:
            try:
                json.dump(str(buffer), file)
            except json.decoder.JSONDecodeError:
                self.send_error(400)
                return
        self.send_response(HTTPStatus.CREATED)
        self.end_headers()


def _runserver(handler, host = "localhost", port = 9999):
    with socketserver.TCPServer((host, port), handler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        print(f"Running {handler} server on http://{host}:{port}")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Shutdown")
            server.shutdown()

def runserver(handler):
    handler_cls = {"TCP": TCPHandler, "HTTP": HTTPHandler}.get(handler)
    _runserver(handler_cls)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    HANDLER = "HTTP"

    runserver(HANDLER)
