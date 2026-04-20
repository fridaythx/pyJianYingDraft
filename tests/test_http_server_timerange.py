import unittest

from http_server import subtitle_transform_y, text_from_payload, timerange_from_payload
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

    def test_adds_speaker_prefix_to_display_text(self):
        segment = {"speaker": "韩立", "text": "适才相戏尔"}

        self.assertEqual(text_from_payload(segment), "韩立：适才相戏尔")
        self.assertEqual(segment["text"], "适才相戏尔")

    def test_keeps_existing_prefix_separator(self):
        self.assertEqual(
            text_from_payload({"textPrefix": "韩立：", "text": "适才相戏尔"}),
            "韩立：适才相戏尔"
        )

    def test_moves_multiline_subtitle_above_bottom_margin(self):
        segment = {
            "position": {"y": -0.9},
            "style": {"size": 24},
        }
        text = "第一行\n第二行\n第三行"

        self.assertGreater(subtitle_transform_y(segment, text, {"height": 1920}, 160), -0.9)

    def test_keeps_subtitle_y_when_already_above_bottom_margin(self):
        segment = {
            "position": {"y": -0.4},
            "style": {"size": 24},
        }

        self.assertEqual(subtitle_transform_y(segment, "一行字幕", {"height": 1920}, 160), -0.4)


if __name__ == "__main__":
    unittest.main()
