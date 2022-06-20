import json
import unittest
import unittest.mock
import socket

import ais_decoder.client as client
#import ais_decoder.server as server

TEST_IP = "localhost"
TEST_PORT = 9999

class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = client.Client(TEST_IP, TEST_PORT)

        # mock requests.post
        client.socket.socket.sendall = unittest.mock.Mock()
        client.socket.socket.connect = lambda *args: None
        client.socket.socket.recv = lambda *args: b"201,"

        self.test_str = "!AIVDM,2,1,5,B,53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"

    def test_send_msg(self):
        res = self.client.send(self.test_str)
        self.assertIn(201, res)

    def test_send_bad_msg(self):
        res = self.client.send(self.test_str.replace("!", "#"))
        self.assertIn(400, res)

class TestServer(unittest.TestCase):
    def setUp(self):
        # mock tcp handler
#        server.TCPHandler.handle = unittest.mock.Mock(wraps=server.TCPHandler.handle)

        self.test_json = {
                        "msg_type": "!AIVDM",
                        "fragments": "2",
                        "fragment_num": "1",
                        "secuential_id": "5",
                        "radio_channel": "B",
                        "payload": "53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"
       }

    def test_send_msg(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TEST_IP, TEST_PORT))

            sock.sendall(bytes(json.dumps(self.test_json), "ascii"))
            status, text = str(sock.recv(1024), "ascii").split(",")

        self.assertEqual(201, int(status))
