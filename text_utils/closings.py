def get_closing_char(opening_char):
    # Define a mapping of opening characters to their corresponding closing characters
    closing_chars = {
        '{': '{}',
        '[': '[]',
        '(': '()',
        '"': '""',
        "'": "''"
    }
    
    # Return the corresponding closing character or None if the character is not recognized
    if string := closing_chars.get(opening_char, None):
        return string
    else:
        return opening_char