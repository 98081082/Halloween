"""Interactive, offline Piper speech for the Raspberry Pi."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import wave


def speak(voice, text: str, device: str) -> None:
    """Generate a temporary WAV, play it, and remove it even on failure."""
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="halloween-speech-") as directory:
        wav_path = Path(directory) / "speech.wav"
        with wave.open(str(wav_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        generated = time.perf_counter()
        with wave.open(str(wav_path), "rb") as wav_file:
            duration = wav_file.getnframes() / wav_file.getframerate()
        print(f"Generated {duration:.2f}s of audio in {generated - started:.2f}s.", flush=True)
        subprocess.run(
            ["aplay", "-q", "-D", device, str(wav_path)],
            check=True,
            timeout=duration + 15,
        )
    print(f"Finished in {time.perf_counter() - started:.2f}s total.", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", type=Path,
        default=Path(__file__).resolve().parent / "voices" / "en_US-lessac-low.onnx",
        help="Piper ONNX voice file (its .onnx.json file must be alongside it)",
    )
    parser.add_argument("--device", default="default", help="ALSA playback device; see aplay -L")
    args = parser.parse_args()
    if not args.model.is_file() or not Path(str(args.model) + ".json").is_file():
        print(f"Voice model or configuration missing: {args.model}", file=sys.stderr)
        print("Download it with: python -m piper.download_voices --download-dir voices en_US-lessac-low", file=sys.stderr)
        return 1
    if shutil.which("aplay") is None:
        print("Audio player missing: install the alsa-utils operating-system package.", file=sys.stderr)
        return 1
    try:
        from piper import PiperVoice

        started = time.perf_counter()
        voice = PiperVoice.load(args.model)
        print(f"Voice loaded in {time.perf_counter() - started:.2f}s.", flush=True)
    except Exception as exc:
        print(f"Could not load Piper voice: {exc}", file=sys.stderr)
        return 1

    print("Enter text to speak. Type /quit to exit.", flush=True)
    while True:
        try:
            text = input("Text> ").strip()
        except EOFError:
            print()
            return 0
        if text.lower() in {"/quit", "/exit"}:
            return 0
        if not text:
            continue
        try:
            speak(voice, text, args.device)
        except subprocess.TimeoutExpired:
            print("Audio playback timed out. Check the output device.", file=sys.stderr)
        except subprocess.CalledProcessError:
            print("Audio playback failed. Use aplay -L to find a device and pass --device.", file=sys.stderr)
        except Exception as exc:
            print(f"Speech failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nGoodbye.")
        sys.exit(0)
