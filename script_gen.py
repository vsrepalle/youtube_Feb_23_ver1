"""English script generation + Hindi translation"""

from googletrans import Translator   # ← This line is correct
from typing import Tuple

def build_english_script(data: dict) -> str:
    parts = [
        data["hook_text"].strip(),
        "\n\n" + data["details"].strip(),
        "\n\n" + data["subscribe_hook"].strip()
    ]
    return "\n".join(filter(None, parts)).strip()

from deep_translator import GoogleTranslator

def translate_to_hindi(text: str) -> str:
    try:
        translator = GoogleTranslator(source='auto', target='hi')
        return translator.translate(text)
    except Exception as e:
        print(f"Deep-translator failed: {e}")
        # Fallback to original googletrans
        from googletrans import Translator
        try:
            return Translator().translate(text, dest="hi").text
        except:
            return text