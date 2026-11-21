"""Regression tests for the offline audio boundary; no DSP emulation."""
import tempfile
import unittest
import wave
from pathlib import Path

from multistomp_lab.audio_offline import BackendUnavailable, process_wav


class OfflineAudioTests(unittest.TestCase):
    def test_bit_exact_stereo_pcm_bypass(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "in.wav"
            target = Path(directory) / "out.wav"
            payload = bytes(range(256)) * 8
            with wave.open(str(source), "wb") as writer:
                writer.setnchannels(2)
                writer.setsampwidth(2)
                writer.setframerate(44100)
                writer.writeframes(payload)
            report = process_wav(str(source), str(target))
            self.assertEqual(report["status"], "bit_exact_pcm_bypass_only")
            self.assertEqual(report["sample_rate"], 44100)
            with wave.open(str(target), "rb") as reader:
                self.assertEqual(reader.readframes(999999), payload)

    def test_effect_request_fails_closed(self):
        with self.assertRaises(BackendUnavailable):
            process_wav("does-not-exist.wav", "out.wav", effect_slots=1)

    def test_refuses_overwrite(self):
        with self.assertRaises(ValueError):
            process_wav("same.wav", "same.wav")


if __name__ == "__main__":
    unittest.main()
