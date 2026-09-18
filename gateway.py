"""Generate a Halloween phrase from a photo, or test Ollama with text."""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

from ai.ollama import GatewayError, OllamaProvider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("OLLAMA_URL", "http://192.168.4.40:11434"))
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3.5:9b"))
    parser.add_argument("--timeout", type=float, default=120, help="Response timeout in seconds")
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--image", type=Path, help="Local image file")
    inputs.add_argument("--text", help="Text-only gateway test")
    parser.add_argument("--json", action="store_true", help="Output phrase and timings as JSON")
    args = parser.parse_args()
    try:
        provider = OllamaProvider(args.url, args.model, read_timeout=args.timeout)
        result = (provider.generate_halloween_line(args.image) if args.image is not None
                  else provider.generate_text(args.text))
    except (GatewayError, ValueError) as exc:
        print(f"Gateway error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(result.phrase)
        print(json.dumps(result.timings), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
