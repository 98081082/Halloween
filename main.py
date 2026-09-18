"""Photo -> Ollama Halloween phrase -> Piper monster voice -> Pi speaker."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time
import unicodedata

from ai.ollama import OllamaProvider


def spoken_text(text: str) -> str:
    """Remove non-spoken emoji/symbols without losing letters or punctuation."""
    text = "".join(c for c in text if unicodedata.category(c) not in {"So", "Sk", "Cf"}
                   and not 0xFE00 <= ord(c) <= 0xFE0F)
    text = " ".join(text.split())
    if not any(c.isalnum() for c in text):
        raise ValueError("Ollama returned no speakable text")
    return text


def load_speech_module():
    path = Path(__file__).resolve().parent / "text to speech" / "speech.py"
    spec = importlib.util.spec_from_file_location("halloween_speech", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_interaction(provider, image, voice, speak, device, style):
    started = time.perf_counter()
    result = provider.generate_halloween_line(image)
    phrase = spoken_text(result.phrase)
    print(f"Phrase: {phrase}", flush=True)
    speech_started = time.perf_counter()
    speak(voice, phrase, device, style)
    timings = dict(result.timings)
    timings["speech_s"] = time.perf_counter() - speech_started
    timings["interaction_s"] = time.perf_counter() - started
    return timings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Photo to describe and speak about")
    parser.add_argument("--url", default=os.getenv("OLLAMA_URL", "http://192.168.4.40:11434"))
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3.5:9b"))
    parser.add_argument("--voice", type=Path,
                        default=Path("/home/pi/halloween/voices/en_US-lessac-low.onnx"))
    parser.add_argument("--device", default="plughw:CARD=Headphones,DEV=0")
    parser.add_argument("--style", choices=("monster", "normal"), default="monster")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        if not args.image.is_file():
            raise ValueError(f"Photo not found: {args.image}")
        if not args.voice.is_file() or not Path(str(args.voice) + ".json").is_file():
            raise ValueError(f"Voice model or configuration missing: {args.voice}")
        if not shutil.which("aplay"):
            raise ValueError("Install alsa-utils to provide aplay")
        provider = OllamaProvider(args.url, args.model, read_timeout=args.timeout)
        from piper import PiperVoice
        voice_started = time.perf_counter()
        voice = PiperVoice.load(args.voice)
        voice_load = time.perf_counter() - voice_started
        print(f"Voice loaded in {voice_load:.2f}s.", flush=True)
        timings = run_interaction(provider, args.image, voice,
                                  load_speech_module().speak, args.device, args.style)
        timings["voice_load_s"] = voice_load
        timings["end_to_end_s"] = time.perf_counter() - started
        print(json.dumps(timings, indent=2), flush=True)
        return 0
    except Exception as exc:
        print(f"Photo-to-speech failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
