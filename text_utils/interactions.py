import pygame_canvas as c
import regex as re
from pprint import pprint as pp
from pygame_canvas import pg
import debug.console as cons

default_color = [200, 200, 200]

def highlight_word(text, regex_pattern):
    first_part = list(text)
    second_part = [' '] * len(text)

    for match in re.finditer(regex_pattern, text):
        start, end = match.span()
        first_part[start:end] = [' '] * (end - start)
        second_part[start:end] = list(text[start:end])
    return ''.join(first_part), ''.join(second_part)

def handle_interactions(FILE_CONTENT: list, inters, strong = 0):
    display = FILE_CONTENT.copy()
    for inter in inters:
        for idx in range(len(display)):
            if inter.get("active"):
                FILE_CONTENT[idx] = re.sub(inter["keyword"], inter["word"], FILE_CONTENT[idx])
            else:
                display[idx] = re.sub(inter["keyword"], inter["word"], display[idx])
    return display
    
def handle_interactions_at_row(row, FILE_CONTENT: list, display: list, inters, action):
    try:
        display_row = FILE_CONTENT[row]
        if action == "pop":
            display.insert(row, "")
        for inter in inters:
            match action:
                case "set":
                    if inter.get("active"):
                        FILE_CONTENT[row] = re.sub(inter["keyword"], inter["word"], FILE_CONTENT[row])
                    else:
                        display_row = re.sub(inter["keyword"], inter["word"], display_row)
                case "pop":
                    if inter.get("active"):
                        FILE_CONTENT[row] = re.sub(inter["keyword"], inter["word"], FILE_CONTENT[row])
                    else:
                        display_row = re.sub(inter["keyword"], inter["word"], display_row)
        display[row] = display_row
    except IndexError:
        print("index error")
    return display

def handle_colors_at_row(row, display: list, colors, colored_surfaces_list, display_surfaces, font: pg.Font, action):
    temp_colored = 0
    try:
        original_line = display[row]
        for color_id, color_json in enumerate(colors):
            word = color_json["keyword"]
            color = color_json.get("color") if color_json.get("color") else default_color
            original_line, highlighted_line = highlight_word(original_line, word)
            if not temp_colored:
                temp_colored = font.render(highlighted_line, 1, color)
            else:
                temp_colored.blit(font.render(highlighted_line, 1, color))
        match action:
            case "pop":
                colored_surfaces_list.insert(row, temp_colored)
            case "set":
                colored_surfaces_list[row] = temp_colored
        match action:
            case "pop":
                display_surfaces.insert(row, font.render(original_line, 1, default_color))
            case "set":
                display_surfaces[row] = font.render(original_line, 1, default_color)
    except IndexError:
        print("Handle at row index fail")

def handle_colors(display: list, colors):
    colored_files = []
    for color_json in colors:
        c_file = {
            "color" : color_json.get("color") if color_json.get("color") else default_color,
            "file" : []
        }
        word = color_json["keyword"]
        for idx in range(len(display)):
            display[idx], highlighted_line = highlight_word(display[idx], word)
            c_file["file"].append(
                highlighted_line
            )
        colored_files.append(c_file)

    return display, colored_files

def draw_text(display, colored_lines, MARGINS, DISPLAY_POS, font_height, S, font, bg, cursor):
    _margin_y = -100
    _cond: bool = 0
    _fontx, _ = font.size("-")
    for idx, line in enumerate(display):
        height = MARGINS[1]-DISPLAY_POS[1]+(idx*font_height)
        if _cond or abs(height-S[1]//2) < S[1]//2-_margin_y and height < cons.bar.pos_Y-font_height-10:
            c.blit(
                line,
                (MARGINS[0]-DISPLAY_POS[0], height)
            )

            nabs = abs(idx - cursor[1])
            number = nabs if nabs else idx

            number_offset = len(str(number))

            c.text(
                number,
                (MARGINS[0]-DISPLAY_POS[0]-number_offset*_fontx-_fontx, height),
                0,
                cons.get_color(bg) if nabs else cons.get_color(cons.get_color(bg)),
                font,
            )
    for idx, line in enumerate(colored_lines):
        height = MARGINS[1]-DISPLAY_POS[1]+(idx*font_height)
        if _cond or abs(height-S[1]//2) < S[1]//2-_margin_y and height < cons.bar.pos_Y-font_height-10:
            c.blit(
                line,
                (MARGINS[0]-DISPLAY_POS[0], height)
            )