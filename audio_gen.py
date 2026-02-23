# Audio TTS 
"""Generate Hindi TTS audio"""

from gtts import gTTS
from pathlib import Path
import os

def generate_audio(text_hindi: str, output_path: str | Path = "temp/audio.mp3") -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=text_hindi, lang="hi", slow=False)
    tts.save(str(path))

    if not path.is_file():
        raise RuntimeError("Audio file was not created")

    print(f"Audio saved → {path}")
    return str(path)