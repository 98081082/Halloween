# Halloween speech

The default `--style monster` lowers pitch by about 8.8 semitones while preserving
the natural speaking pace, and adds a raspy zombie growl and 90 ms echo.
Blended soft saturation adds rasp, with 31 Hz and 67 Hz modulation for roughness.
SoX shifts pitch independently of duration; Python adds rasp with headroom.
Install the system dependency with `sudo apt-get install sox`.
Use `--style normal` for the original Piper voice.

Interactive offline text-to-speech using Piper on the Raspberry Pi.
The voice is loaded once and reused. Generated audio is temporary and deleted
after playback. Timing is printed for synthesis and the complete interaction.

## Run on the Pi

```sh
cd /home/pi/halloween
.venv/bin/python "text to speech/speech.py" --model voices/en_US-lessac-low.onnx --device plughw:CARD=Headphones,DEV=0
```

Enter text at the prompt and press Enter to hear it. Type `/quit` to exit,
or press Ctrl+C. The command above selects the Pi's headphone jack.
For other outputs, inspect `aplay -L` and pass the desired `--device`.
Without that option, the program uses ALSA's default output.

## Setup

Piper and its voice have already been installed on the project Pi. The command
above assumes this repository's folder layout has been deployed there.
To set up another installation, run these commands from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r "text to speech/requirements.txt"
.venv/bin/python -m piper.download_voices --download-dir "text to speech/voices" en_US-lessac-low
.venv/bin/python "text to speech/speech.py" --device plughw:CARD=Headphones,DEV=0
```

Playback requires `aplay`, provided by the OS package `alsa-utils`.
Use `--model /path/to/voice.onnx` for another Piper voice; its matching
`voice.onnx.json` configuration must be beside it. Consult each voice's model
card for its license before redistribution.
