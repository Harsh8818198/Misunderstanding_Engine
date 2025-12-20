import subprocess
import shlex
import json


def lingo_translate(text, to_lang="en"):
    """
    Translate text using Lingo CLI.
    Falls back to mock translation if CLI unavailable.
    """
    try:
        # Escape text for shell
        safe_text = shlex.quote(text)

        # Call Lingo CLI (adjust flags based on actual CLI docs)
        cmd = f"lingo translate --text {safe_text} --to {to_lang} --format json"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

        if res.returncode != 0:
            raise RuntimeError(f"Lingo CLI error: {res.stderr}")

        # Parse JSON response
        parsed = json.loads(res.stdout)
        return parsed.get("translation") or str(parsed)

    except Exception as e:
        print(f"Lingo translation failed: {e}. Using fallback.")
        # Fallback: return original text with note
        # In production, use Google Translate API or similar
        return f"[Translation unavailable - showing original]: {text}"