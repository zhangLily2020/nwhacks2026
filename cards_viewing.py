import os
import time
import json
import re
from collections import Counter
from google import genai
from google.genai import types

# Use folder relative to this script
img_dir = os.path.join(os.path.dirname(__file__), "img")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
_EXTS = {"jpg", "jpeg", "png", "webp"}

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

try:
    while True:
        # get image files in alphabetical order
        try:
            files = sorted(
                f for f in os.listdir(img_dir)
                if os.path.isfile(os.path.join(img_dir, f)) and f.rsplit(".", 1)[-1].lower() in _EXTS
            )
        except FileNotFoundError:
            # img folder may not exist yet; wait and retry
            time.sleep(1)
            continue

        if not files:
            # nothing to process; wait and retry
            time.sleep(1)
            continue

        for fname in files:
            path = os.path.join(img_dir, fname)
            if not os.path.exists(path):
                continue

            ext = fname.rsplit(".", 1)[-1].lower()
            if ext in ("jpg", "jpeg"):
                mime = "image/jpeg"
            elif ext == "png":
                mime = "image/png"
            elif ext == "webp":
                mime = "image/webp"
            else:
                continue

            try:
                with open(path, "rb") as f:
                    image_bytes = f.read()

                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime),
                        PROMPT,
                    ],
                )

                raw = response.text
                try:
                    parsed = extract_json(raw)
                except Exception as e:
                    print(f"{fname}: failed to parse JSON from model response: {e}")
                    # Keep the file for retry later
                    time.sleep(1)
                    continue

                # Validate structure
                if not isinstance(parsed, dict) or "player" not in parsed or "dealer" not in parsed:
                    print(f"{fname}: parsed JSON missing 'player' or 'dealer' keys: {parsed}")
                    time.sleep(1)
                    continue

                # Extract card lists for each side
                player_obj = parsed.get("player", {})
                dealer_obj = parsed.get("dealer", {})

                player_cards = player_obj.get("cards", [])
                dealer_cards = dealer_obj.get("cards", [])

                if not isinstance(player_cards, list) or not isinstance(dealer_cards, list):
                    print(f"{fname}: 'cards' for player or dealer is not a list: {parsed}")
                    time.sleep(1)
                    continue

                # Normalize ranks to strings
                normalized_player = [str(c).strip() for c in player_cards]
                normalized_dealer = [str(c).strip() for c in dealer_cards]

                # Compute newly observed cards (multiset difference)
                new_player_diff = Counter(normalized_player) - Counter(prev_player)
                new_dealer_diff = Counter(normalized_dealer) - Counter(prev_dealer)

                # Combine diffs and update single total counter
                combined_new = new_player_diff + new_dealer_diff
                if combined_new:
                    total_counter.update(combined_new)

                # Report state change or no change
                if normalized_player != prev_player or normalized_dealer != prev_dealer:
                    print(
                        f"{fname}: state changed -> player count={len(normalized_player)}, "
                        f"player_cards={normalized_player}; dealer count={len(normalized_dealer)}, "
                        f"dealer_cards={normalized_dealer}"
                    )
                else:
                    print(
                        f"{fname}: no state change (player count={len(normalized_player)}, "
                        f"player_cards={normalized_player}; dealer count={len(normalized_dealer)}, "
                        f"dealer_cards={normalized_dealer})"
                    )

                # Print cumulative total counter
                print(f"total_counter={dict(total_counter)}")

                # Update previous states
                prev_player = normalized_player
                prev_dealer = normalized_dealer

                # on successful parse and counting, delete the image
                try:
                    os.remove(path)
                except OSError as e:
                    print(f"Failed to delete {fname}: {e}")

            except Exception as e:
                # log and keep the file for retry later
                print(f"Error processing {fname}: {e}")
                # small backoff before next attempt
                time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted, exiting.")
