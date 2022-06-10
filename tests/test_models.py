from time import time
import unittest
from pathlib import Path

from ais_decoder.models import NMEASentence, ValidationError

TEST_DATA_DIR = Path(__file__).parent / "test_data"

class TestValidators(unittest.TestCase):
    def setUp(self):
        self.msg = NMEASentence
        with open(TEST_DATA_DIR / "nmea-sample") as file:
            self.test_data = file.read().split("\n")
        self.test_str = "!AIVDM,2,1,5,B,53P7fG02=bcdlELcB20MLDp@"\
                        "thDr222222222216DpF@@4m@0@EPCPkmEQDa,0*3C"

    def tearDown(self):
        del self.msg

    def test_valid_msg(self):
        for item in self.test_data:
            if item:
                # it will be nmea_msg\n because we are reading a file
                # strip it
                self.msg(item)

    def test_benchmark(self):
        start = time()
        self.test_valid_msg()
        end = time() - start
        self.assertLess(end, 3)

    def test_length(self):
        test_str = self.test_str + "1"

        self.assertRaises(ValidationError, self.msg, test_str)

    def test_type_validator(self):
        test_str = self.test_str.replace("!", "#")

        self.assertRaises(ValidationError, self.msg, self.test_str.replace("!", "#"))

    def test_field_num_validator(self):
        # to avoid "TooLong" validation error
        test_str = self.test_str[:20] + ",extrafield1, extrafield2, extrafield3"

        self.assertRaises(ValidationError, self.msg, test_str)

    def test_checksum_validator(self):
        test_str = self.test_str.replace("*", "#")

        self.assertRaises(ValidationError, self.msg, test_str)

        test_str = self.test_str.replace("*", "#").replace("0", "A")

        self.assertRaises(ValidationError, self.msg, test_str)

    def test_payload_validator(self):
        test_str = self.test_str.replace("@", "ñ")

        self.assertRaises(ValidationError, self.msg, test_str)

    def test_numerical_field_validator(self):
        test_str = self.test_str.replace("2", "a")

        self.assertRaises(ValidationError, self.msg, test_str)

    def test_radio_channel_validator(self):
        test_str = self.test_str.replace("5", "")

        self.msg(test_str)
