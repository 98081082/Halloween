# Halloween decoration

## Photo to speaker

From `/home/pi/halloween/Halloween`, run:

```sh
/home/pi/halloween/.venv/bin/python main.py /home/pi/halloween/test-images/witch-costume.jpg
```

This loads Piper, sends the photo to Ollama, prints the generated phrase, and
plays it through the headphone output using the zombie/monster effect.
Options: `--style normal`, `--device ALSA_DEVICE`, `--voice MODEL.onnx`,
`--url http://HOST:11434`, `--model MODEL`, and `--timeout SECONDS`.
The existing speech implementation is reused, so voice adjustments apply to both
interactive speech and photo playback. Emoji are removed before synthesis.
The input photo is preserved; generated audio is temporary. Failures exit nonzero.
Timing includes voice loading, Ollama, synthesis/playback, and the full run.

## Ollama gateway

On the Pi, from `/home/pi/halloween/Halloween`:

```sh
/home/pi/halloween/.venv/bin/python -m pip install -r requirements.txt
/home/pi/halloween/.venv/bin/python gateway.py --text "Say: Happy Halloween!" --json
/home/pi/halloween/.venv/bin/python gateway.py --image /home/pi/halloween/test-images/costume.jpg
```

Defaults: `http://192.168.4.40:11434`, model `qwen3.5:9b`.
Override with `--url`, `--model`, or `OLLAMA_URL` / `OLLAMA_MODEL`.
The model must support vision for photos. `--timeout` controls the response
timeout (120 seconds by default); connection timeout is 5 seconds.

The prompt in `ai/ollama.py` selects one clearly visible costumed visitor,
references a visible detail, and requests a family-friendly witty phrase of
at most 30 words. If no suitable person is visible, it requests a generic greeting.
Model output is probabilistic: inspect real costume examples before deployment.

Images are oriented, resized to at most 768 pixels per side, and JPEG encoded
in memory. The gateway writes no photos and does not delete its input file.
Future camera code can call `OllamaProvider.generate_halloween_line(image_bytes)`
with encoded JPEG/PNG bytes, or pass a `Path`, and read `result.phrase`.
Test image URLs will be downloaded separately into `/home/pi/halloween/test-images/`
when supplied. Do not commit visitor photos.

Phrase text goes to stdout; timings go to stderr. `--json` combines both.
Timings include image preparation, request wall time, and Ollama model load,
prompt evaluation and generation times when provided by the server.
Errors exit nonzero rather than passing an error message to the speaker.
Use `main.py` for combined playback, or `text to speech/README.md` for interactive speech.

API references: [chat](https://docs.ollama.com/api/chat),
[vision image encoding](https://docs.ollama.com/capabilities/vision).

Run offline tests with `python -m unittest discover -s tests -v`.
