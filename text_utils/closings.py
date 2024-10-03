import globals as g
import json

def get_closing_char(opening_char):
    with open(f"{g.config_path}/closings/closers.json", "r") as fp:
        closing_chars = json.load(fp)
    
    # Return the corresponding closing character or None if the character is not recognized
    if string := closing_chars.get(opening_char, None):
        return string
    else:
        return opening_char