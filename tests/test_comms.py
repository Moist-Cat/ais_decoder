import json
import unittest
import unittest.mock
import socket

import requests

import ais_decoder.client as client
from ais_decoder.client import HTTPClient
from ais_decoder.server import HTTPHandler, TCPHandler, _runserver

TEST_IP = "localhost"
TEST_PORT = 9999

class TestSocketClient(unittest.TestCase):
    def setUp(self):
        self.server = _runserver(TCPHandler, host = "localhost", port = 9999)

        self.client = client.TCPClient(TEST_IP, TEST_PORT)

        # mock requests.post
        client.socket.socket.sendall = unittest.mock.Mock()
        client.socket.socket.connect = lambda *args: None
        client.socket.socket.recv = lambda *args: b"201,"

        self.test_str = "!AIVDM,2,1,5,B,53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_send_msg(self):
        res = self.client.send(self.test_str)
        self.assertIn(201, res)

    def test_send_bad_msg(self):
        res = self.client.send(self.test_str.replace("!", "#"))
        self.assertIn(400, res)

class TestSocketServer(unittest.TestCase):
    def setUp(self):
        self.server = _runserver(TCPHandler, host = "localhost", port = 9998)

        self.test_json = {
                        "msg_type": "!AIVDM",
                        "fragments": "2",
                        "fragment_num": "1",
                        "secuential_id": "5",
                        "radio_channel": "B",
                        "payload": "53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"
       }
   
    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_send_msg(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TEST_IP, TEST_PORT-1))

            sock.sendall(bytes(json.dumps(self.test_json), "ascii"))
            status, text = str(sock.recv(1024), "ascii").split(",")

        self.assertEqual(201, int(status))

class TestHTTPClient(unittest.TestCase):
    def setUp(self):
        self.server = _runserver(HTTPHandler, host = "localhost", port = 9997)

        self.client = HTTPClient(TEST_IP, 9997)

        # mock requests.post
        self.client.post = unittest.mock.Mock()

        self.test_str = "!AIVDM,2,1,5,B,53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_send_msg(self):
        res = self.client.get_message()
        self.assertEqual(200, res.status_code, res.text)

class TestHTTPServer(unittest.TestCase):
    def setUp(self):
        self.server = _runserver(HTTPHandler, host = "localhost", port = 9996)

        self.test_json = {"AIVDM": {
                        "msg_type": "!AIVDM",
                        "fragments": "2",
                        "fragment_num": "1",
                        "secuential_id": "5",
                        "radio_channel": "B",
                        "payload": "53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"
                    }
       }

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_send_msg(self):
        res = requests.post(f"http://{TEST_IP}:{TEST_PORT-3}/", json=self.test_json)
        self.assertEqual(201, res.status_code)
