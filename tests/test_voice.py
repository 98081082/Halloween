from array import array
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import wave

from main import load_speech_module


class VoiceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("sox"), "SoX is required")
    def test_low_pitch_preserves_duration(self):
        rate = 22050
        samples = array("h", (round(5000 * math.sin(2 * math.pi * 440 * i / rate))
                              for i in range(rate * 2)))
        if sys.byteorder != "little":
            samples.byteswap()
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "in.wav", Path(directory) / "out.wav"
            with wave.open(str(source), "wb") as audio:
                audio.setparams((1, 2, rate, 0, "NONE", "not compressed"))
                audio.writeframes(samples.tobytes())
            load_speech_module().monster_effect(source, target)
            with wave.open(str(target), "rb") as audio:
                self.assertEqual(audio.getframerate(), rate)
                self.assertAlmostEqual(audio.getnframes() / rate, 2.09, delta=0.05)
                output = array("h", audio.readframes(audio.getnframes()))
            if sys.byteorder != "little":
                output.byteswap()
            # Estimate fundamental over a settled one-second region.
            middle = output[rate // 2:rate * 3 // 2]
            crossings = sum(a <= 0 < b for a, b in zip(middle, middle[1:]))
            self.assertAlmostEqual(crossings, 264, delta=15)
