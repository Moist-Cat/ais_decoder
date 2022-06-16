import socketserver
import json
import threading

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

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    with socketserver.TCPServer((HOST, PORT), TCPHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        try:
            while True:
                pass
        except KeyboardInterrupt:
            server.shutdown()
