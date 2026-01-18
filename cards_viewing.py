import os
import time
import json
import re
from collections import Counter
from google import genai
from google.genai import types

# Use folder relative to this script
img_dir = os.path.join(os.path.dirname(__file__), "img")
_EXTS = {"jpg", "jpeg", "png", "webp"}


def _load_env_file():
    """Lightweight loader for a .env file located in the project root.

    This sets environment variables that are not already present in `os.environ`.
    """
    # Look for a .env in the script directory first, then the parent directory
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, ".env")),
    ]
    root_env = None
    for c in candidates:
        if os.path.exists(c):
            root_env = c
            break
    if not root_env:
        return
    try:
        with open(root_env, "r") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # best-effort only; don't crash the import
        return


_load_env_file()
_api_key = os.environ.get("GEMINI_API_KEY")
if _api_key:
    client = genai.Client(api_key=_api_key)
else:
    client = None

# Keep the last-seen card lists for player and dealer
prev_player = []
prev_dealer = []

# Cumulative total per-rank counter (combined for player+dealer)
total_counter = Counter()

# Prompt requesting strict JSON output for both player and dealer.
PROMPT = (
    "You are given an image of a poker game where cards may be visible for the player (bottom side) "
    "and the dealer (across from the player). Identify the cards visible for each side and return ONLY valid JSON "
    "with two top-level keys: \"player\" and \"dealer\". Each should be an object with two keys:\n"
    "  - count: integer number of cards detected for that side\n"
    "  - cards: array of card ranks as strings (use A,2,3,4,5,6,7,8,9,10,J,Q,K)\n"
    "Example: {\"player\": {\"count\": 2, \"cards\": [\"A\", \"10\"]}, \"dealer\": {\"count\": 1, \"cards\": [\"K\"]}}\n"
    "If no cards are visible for a side, return {\"count\": 0, \"cards\": []} for that side. RETURN ONLY THE JSON OBJECT."
)

def extract_json(text: str):
    """Try to extract a JSON object from text. Returns parsed object or raises ValueError."""
    # Quick attempt if the response is clean
    text = text.strip()
    # If it already looks like JSON
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    # Try to find a {...} substring
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        candidate = m.group(1)
        # Try progressively shorter tails to handle trailing markdown or backticks
        start = candidate.find("{")
        for end in range(len(candidate), start, -1):
            try:
                return json.loads(candidate[:end])
            except Exception:
                continue
    raise ValueError("No valid JSON found in response")
def analyze_image_bytes(image_bytes: bytes, mime: str):
    """Analyze image bytes with the Gemini model and return (player_cards, dealer_cards).

    Raises ValueError on parsing/validation errors or other exceptions from the client.
    """
    print("Analyzing image bytes")
    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Set the environment variable or add a .env file with GEMINI_API_KEY."
        )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime),
            PROMPT,
        ],
    )

    raw = response.text
    print(raw)
    parsed = extract_json(raw)

    if not isinstance(parsed, dict) or "player" not in parsed or "dealer" not in parsed:
        raise ValueError(f"parsed JSON missing 'player' or 'dealer' keys: {parsed}")

    player_obj = parsed.get("player", {})
    dealer_obj = parsed.get("dealer", {})

    player_cards = player_obj.get("cards", [])
    dealer_cards = dealer_obj.get("cards", [])

    if not isinstance(player_cards, list) or not isinstance(dealer_cards, list):
        raise ValueError(f"'cards' for player or dealer is not a list: {parsed}")

    normalized_player = [str(c).strip() for c in player_cards]
    normalized_dealer = [str(c).strip() for c in dealer_cards]

    return normalized_player, normalized_dealer


def analyze_image_file(path: str):
    print("Reached")
    """Read an image file from `path` and return (player_cards, dealer_cards)."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    ext = path.rsplit(".", 1)[-1].lower()
    if ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif ext == "png":
        mime = "image/png"
    elif ext == "webp":
        mime = "image/webp"
    else:
        raise ValueError(f"Unsupported image extension: {ext}")

    with open(path, "rb") as f:
        image_bytes = f.read()

    print("Anazlyzing")
    return analyze_image_bytes(image_bytes, mime)


__all__ = ["analyze_image_file", "analyze_image_bytes", "extract_json"]
