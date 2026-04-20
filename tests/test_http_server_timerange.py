import unittest

from http_server import timerange_from_payload
from pyJianYingDraft import SEC


class TimerangeFromPayloadTest(unittest.TestCase):
    def test_uses_duration_when_present(self):
        timerange = timerange_from_payload({"start": "2s", "duration": "3s"})

        self.assertEqual(timerange.start, 2 * SEC)
        self.assertEqual(timerange.duration, 3 * SEC)

    def test_converts_end_to_duration(self):
        timerange = timerange_from_payload({"start": "2s", "end": "5s"})

        self.assertEqual(timerange.start, 2 * SEC)
        self.assertEqual(timerange.duration, 3 * SEC)

    def test_requires_duration_or_end(self):
        with self.assertRaises(KeyError):
            timerange_from_payload({"start": "2s"})

    def test_rejects_end_before_start(self):
        with self.assertRaises(ValueError):
            timerange_from_payload({"start": "5s", "end": "2s"})


if __name__ == "__main__":
    unittest.main()
