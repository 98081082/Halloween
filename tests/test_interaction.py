from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from main import run_interaction, spoken_text


class InteractionTests(unittest.TestCase):
    def test_phrase_is_sent_to_speech(self):
        provider = Mock()
        provider.generate_halloween_line.return_value = SimpleNamespace(
            phrase="Spooky hat! \U0001f383", timings={"request_s": 1})
        speak = Mock()
        timings = run_interaction(provider, b"photo", "voice", speak, "device", "monster")
        provider.generate_halloween_line.assert_called_once_with(b"photo")
        speak.assert_called_once_with("voice", "Spooky hat!", "device", "monster")
        self.assertIn("interaction_s", timings)

    def test_gateway_failure_does_not_play(self):
        provider = Mock()
        provider.generate_halloween_line.side_effect = RuntimeError("offline")
        speak = Mock()
        with self.assertRaises(RuntimeError):
            run_interaction(provider, b"photo", None, speak, "device", "monster")
        speak.assert_not_called()

    def test_playback_failure_propagates(self):
        provider = Mock()
        provider.generate_halloween_line.return_value = SimpleNamespace(phrase="Boo!", timings={})
        with self.assertRaises(RuntimeError):
            run_interaction(provider, b"photo", None, Mock(side_effect=RuntimeError("audio")),
                            "device", "monster")

    def test_empty_speech_rejected(self):
        with self.assertRaises(ValueError):
            spoken_text("\U0001f383")

    def test_punctuation_preserved(self):
        self.assertEqual(spoken_text("You're spooky, witch!"), "You're spooky, witch!")
