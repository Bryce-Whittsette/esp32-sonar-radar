import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viewer"))
from protocol import parse_line


class ProtocolTests(unittest.TestCase):
    def test_valid_return(self):
        reading = parse_line("v1,7,90,1000,ok\r\n")
        self.assertEqual(
            (reading.sequence, reading.angle, reading.distance_mm), (7, 90, 1000)
        )

    def test_no_return(self):
        self.assertEqual(parse_line("v1,0,15,0,no_return").status, "no_return")

    def test_rejects_noise_and_invalid_measurements(self):
        for line in [
            "boot",
            "# header",
            "v1,1,90,NaN,ok",
            "v1,1,181,100,ok",
            "v1,1,90,-1,ok",
            "v1,1,90,0,ok",
            "v1,1,90,100,no_return",
            "v2,1,90,100,ok",
            "x" * 129,
            "v1,1,90,4001,ok",
            "v1,-1,90,100,ok",
        ]:
            with self.subTest(line=line):
                self.assertIsNone(parse_line(line))
