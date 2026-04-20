import os
import tempfile
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import patch

from pyJianYingDraft.local_materials import AudioMaterial


def write_wav(path):
    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(8000)
        wav_file.writeframes(b"\0\0" * 8000)


class AudioMaterialTest(unittest.TestCase):
    def test_wav_duration_falls_back_when_mediainfo_has_no_audio_tracks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "voice.wav")
            write_wav(path)

            fake_info = SimpleNamespace(video_tracks=[], audio_tracks=[])
            with patch("pymediainfo.MediaInfo.can_parse", return_value=True), \
                    patch("pymediainfo.MediaInfo.parse", return_value=fake_info):
                material = AudioMaterial(path)

        self.assertEqual(material.duration, 1000000)


if __name__ == "__main__":
    unittest.main()
