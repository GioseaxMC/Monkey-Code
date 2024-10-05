import pygame_canvas as c
from pygame_canvas import pygame as pg
import text_utils.writing as w
import text_utils.utils as u
import text_utils.interactions as cl
import json
from pprint import pprint as pp
import debug.debugger as db
import debug.console as cons
import sys
import os
import globals as g

NAME = "Monkey Code"

try:
    FILE = sys.argv[1:][0]
except:
    FILE = "console"
FILE_CONTENT = []
ACTUAL_POSITION = [0,0]
CURSOR_POSITION = [0,0]
CURSOR_DISPLAY_POSITION = [0,0]
history = w.history
previous_file = ["",]
DEBUG = 0
CAMERA_POSITION = [0,0]
DISPLAY_CAMERA_POSITION = [0,0]
SELECTION = [[0,0], [0,0]]
selecting = 0
display_edits: list = []
edits = w.edits
font: pg.Font

with open(f"{g.config_path}/info.txt", "r") as fp:
    info = fp.read().split("\n")
    VERSION = info[0]

c.window(1290, 720, title = f"{NAME} - loading", smallest_window_sizes=(480, 270), icon=f"{g.assets_path}/icon.png")
cons.bar = c.sprite([c.rectangle(1,1,"white"),], top_left=0)

pg.key.set_repeat(500, 30)

def update_sizes():
    global WIDTH, HEIGHT, CENTER, MARGINS
    WIDTH, HEIGHT = c.screen_size()
    CENTER = WIDTH//2, HEIGHT/2
    MARGINS = WIDTH*.15, 100

def handle_cursor_movement():
    global ACTUAL_POSITION, CURSOR_POSITION, CURSOR_DISPLAY_POSITION, SELECTION, selecting
    #handle selection logic
    wheel = 0
    if c.mouse_position()[1] < cons.bar.pos_Y:
        wheel = c.get_wheel()
    if c.key_clicked(pg.K_ESCAPE):
        selecting = 0
    offset = c.key_clicked(pg.K_RIGHT) - c.key_clicked(pg.K_LEFT) - (wheel * c.shift())
    moved = 0
    if c.get_clicked_key() in w.MOVEMENT+(pg.K_END, pg.K_HOME):
        if SELECTION[0] == SELECTION[1]:
            selecting = 0
        if selecting:
            if c.shift() or c.key_pressed(pg.K_LALT):
                ...
            else:
                if SELECTION[1][1] - SELECTION[0][1]:
                    sorted_sel = sorted(SELECTION, key=lambda x: x[1])
                elif SELECTION[0][0] - SELECTION[1][0]:
                    sorted_sel = sorted(SELECTION, key=lambda x: x[0])
                else:
                    sorted_sel = SELECTION
                CURSOR_POSITION = sorted_sel[max(0, offset)].copy()
                selecting = 0
                moved = 1
        else:
            if c.shift():
                selecting = 1
                SELECTION[0] = CURSOR_POSITION.copy()

    if offset and not moved:
        if c.ctrl():
            is_at_start = CURSOR_POSITION[0] <= 0
            CURSOR_POSITION[0] += offset
            try:
                _is_space_start = FILE_CONTENT[CURSOR_POSITION[1]][CURSOR_POSITION[0]].isspace()
            except IndexError:
                _is_space_start = 0
            if not CURSOR_POSITION[0]:
                CURSOR_POSITION[0] -= 1
            else:
                while True:
                    CURSOR_POSITION[0] += offset
                    try:
                        if CURSOR_POSITION[0] < 0 or CURSOR_POSITION[0] >= len(display[CURSOR_POSITION[1]]) or FILE_CONTENT[CURSOR_POSITION[1]][CURSOR_POSITION[0]+min(0,offset)].isspace() != _is_space_start or FILE_CONTENT[CURSOR_POSITION[1]][CURSOR_POSITION[0]] in "()[]{}.,-+/*<>":
                            if not is_at_start:
                                CURSOR_POSITION[0] = max(0, CURSOR_POSITION[0])
                            break
                    except IndexError:
                        break
        else:
            CURSOR_POSITION[0] += offset

    if c.ctrl() and c.key_clicked("a"):
        selecting = 1
        SELECTION[0] = [0,0]
        SELECTION[1] = [len(FILE_CONTENT[-1]), len(FILE_CONTENT)-1]

    # move cursor x
    CURSOR_POSITION[1] = max(min(CURSOR_POSITION[1], len(display)-1), 0)

    # handle row movement thru x movement
    if CURSOR_POSITION[0] > len(display[CURSOR_POSITION[1]]) and not display[CURSOR_POSITION[1]] is display[-1]:
        CURSOR_POSITION[1] += 1
        CURSOR_POSITION[0] = 0
    if CURSOR_POSITION[0] < 0 and not display[CURSOR_POSITION[1]] is display[0]:
        CURSOR_POSITION[1] -= 1
        CURSOR_POSITION[0] = len(display[CURSOR_POSITION[1]])

    # move cursor y
    if c.key_pressed(pg.K_LALT):
        w.move(FILE_CONTENT, CURSOR_POSITION, selecting, SELECTION, (c.key_clicked(pg.K_DOWN) - c.key_clicked(pg.K_UP)))
    else:
        CURSOR_POSITION[1] += c.key_clicked(pg.K_DOWN) - c.key_clicked(pg.K_UP) - (wheel * wheel_speed * (not c.shift()))
        if CURSOR_POSITION[1] >= len(display):
            CURSOR_POSITION[0] = len(display[-1])
        if CURSOR_POSITION[1] < 0:
            CURSOR_POSITION[0] = 0
        CURSOR_POSITION[1] = min(max(CURSOR_POSITION[1], 0), len(display)-1)
        CURSOR_POSITION[0] = min(max(CURSOR_POSITION[0], 0), len(display[CURSOR_POSITION[1]]))

    #smooth movement
    ACTUAL_POSITION = [i*j for i, j in zip(CURSOR_POSITION, [FONT_WIDTH, font.get_linesize()])]
    CURSOR_DISPLAY_POSITION[0] += (ACTUAL_POSITION[0] - CURSOR_DISPLAY_POSITION[0]) / CARET_INTERPOLATION
    CURSOR_DISPLAY_POSITION[1] += (ACTUAL_POSITION[1] - CURSOR_DISPLAY_POSITION[1]) / CARET_INTERPOLATION
    if c.shift() and selecting:
        SELECTION[1] = CURSOR_POSITION.copy()
    handle_cursor_position()

def draw_selection():
    if selecting:
        _color = [40,40,40]
        _size = font.get_linesize()+12
        _offsetY = (FONT_SIZE/30)*4 - 8
        try:
            if SELECTION[1][1] - SELECTION[0][1]:
                sorted_sel = sorted(SELECTION, key=lambda x: x[1])
                for global_line, local_line in enumerate(range(sorted_sel[1][1]-sorted_sel[0][1]+1), sorted_sel[0][1]):
                    if local_line == 0:
                        posx = (1+len(display[global_line]) - sorted_sel[0][0])
                        surface = c.rounded_rectangle(posx*FONT_WIDTH, _size, 14, _color)
                        position = (sorted_sel[0][0]*FONT_WIDTH+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], global_line*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1])
                    elif global_line == sorted_sel[1][1]:
                        posx = (sorted_sel[1][0])
                        surface = c.rounded_rectangle(posx*FONT_WIDTH, _size, 14, _color)
                        position = (MARGINS[0]-DISPLAY_CAMERA_POSITION[0], global_line*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1])
                    else:
                        posx = (1+len(display[global_line]))
                        surface = c.rounded_rectangle(posx*FONT_WIDTH, _size, 14, _color)
                        position = (MARGINS[0]-DISPLAY_CAMERA_POSITION[0], global_line*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1])
                    if position[1] < HEIGHT - (HEIGHT - cons.bar.pos_Y)-_size:
                        c.blit(surface, position)
            elif SELECTION[0][0] - SELECTION[1][0]:
                sorted_sel = sorted(SELECTION, key=lambda x: x[0])
                surface = c.rounded_rectangle((sorted_sel[1][0] - sorted_sel[0][0]) * FONT_WIDTH, _size, 14, _color)
                position = ((sorted_sel[0][0])*FONT_WIDTH+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], SELECTION[0][1]*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1])
                if position[1] < HEIGHT - (HEIGHT - cons.bar.pos_Y)-_size:
                    c.blit(surface, position)
        except IndexError:
            cons.push("waiting for threads...")

def handle_cursor_position():
    display_height = HEIGHT - (HEIGHT - cons.bar.pos_Y)
    x = CURSOR_DISPLAY_POSITION[0] - CAMERA_POSITION[0] - WIDTH*.5 + WIDTH*.2 # adding moves to the left
    if abs(x) > WIDTH*.4:
        new_x = WIDTH*.4*u.sign(x)
        CAMERA_POSITION[0] = CURSOR_DISPLAY_POSITION[0] - new_x - WIDTH*.5 + WIDTH*.2
    DISPLAY_CAMERA_POSITION[0] += (CAMERA_POSITION[0] - DISPLAY_CAMERA_POSITION[0]) / SCROLL_INTERPOLATION

    y = CURSOR_DISPLAY_POSITION[1] - CAMERA_POSITION[1] - display_height*.5 + 120 #arbitrary (removing the initial margin)
    if abs(y) > display_height*.35:
        new_y = display_height * 0.35*u.sign(y)
        CAMERA_POSITION[1] = CURSOR_DISPLAY_POSITION[1] - new_y - display_height * 0.5 + 120
    DISPLAY_CAMERA_POSITION[1] += (CAMERA_POSITION[1] - DISPLAY_CAMERA_POSITION[1]) / SCROLL_INTERPOLATION

def handle_writing():
    global history, FILE_CONTENT, CURSOR_POSITION, previous_file, SELECTION, selecting
    mutable = [selecting,]
    # ctrlz
    if c.ctrl() and c.key_clicked("z") and len(history):
        while 1:
            item = history.pop()
            match item["action"]:
                case "set":
                    w.set_line(FILE_CONTENT, item["line"], item["content"], CURSOR_POSITION, 0)
                case "pop":
                    w.pop_line(FILE_CONTENT, item["line"], CURSOR_POSITION, 0)
                case "insert":
                    w.insert_line(FILE_CONTENT, item["line"], item["content"], CURSOR_POSITION, 0)
            update_display()
            CURSOR_POSITION = item["cursor"]


            if (not len(history)) or history[-1].get("id") != item.get("id"):
                break
    else:
        w.write(FILE_CONTENT, display, CURSOR_POSITION, SELECTION, mutable, FILE)
        selecting = mutable[0]

def init_interactions():
    global colored, display, color_surfaces, text_display_surfaces
    display = cl.handle_interactions(FILE_CONTENT, interactions)
    display, colored = cl.handle_colors(display, colors)
    text_display_surfaces = [font.render(row, 1, cl.default_color) for row in display]
    color_surfaces = []
    for row in range(len(display)):
        _colored_render = 0
        for cfile in colored:
            color = cfile["color"]
            if not _colored_render:
                _colored_render = font.render(cfile["file"][row], 1, color)
            else:
                _colored_render.blit(font.render(cfile["file"][row], 1, color))
        color_surfaces.append(_colored_render)

def update_display():
    global display, colors, color_surfaces, text_display_surfaces, display_edits
    for ed_idx in range(len(w.edits)):
        edit = w.edits.pop(0)
        idx = edit["line"]
        match type := edit["type"]:
            case "pop" | "set":
                display = cl.handle_interactions_at_row(idx, FILE_CONTENT, display, interactions, edit["type"])
                cl.handle_colors_at_row(idx, display, colors, color_surfaces, text_display_surfaces, font, edit["type"])
            case "insert":
                display.pop(idx)
                color_surfaces.pop(idx)
                text_display_surfaces.pop(idx)
    if any(w.edits):
        display_edits.append(str(w.edits))
    w.edits.clear()
w.update_display = update_display

def handle_interactions():
    update_display()
    draw_selection()
    cl.draw_text(text_display_surfaces, color_surfaces, MARGINS, DISPLAY_CAMERA_POSITION, font.get_linesize(), (WIDTH, HEIGHT))

def load_settings():
    global FONT_SIZE, FONT_WIDTH, font, bg, CARET, wheel_speed, CARET_COLOR, CARET_INTERPOLATION, SCROLL_INTERPOLATION, DO_HIGHLIGHTING
    with open(f"{g.themes_path}/reset.json", "r") as fp:
        s = json.load(fp)
    with open(f"{g.themes_path}/settings.json", "r") as fp:
        s.update(json.load(fp))
    FONT_SIZE = max(5, (s["font size"] // 5) * 5)
    CARET = s["caret"]
    CARET_COLOR = s["caret color"]
    CARET_INTERPOLATION = max(1, s["caret interpolation"])
    SCROLL_INTERPOLATION = max(1, s["scroll interpolation"])
    DO_HIGHLIGHTING = s["highlight"]
    FONT_WIDTH = (FONT_SIZE * 3) / 5
    font = pg.Font(f"{g.assets_path}/font.ttf", FONT_SIZE)
    bg = s["bg color"]
    cl.default_color = s["font color"]
    wheel_speed = s["scroll speed"]
    cons.MAX_LENGHT = s["consoleLen"]
    cons.MAX_LINES = s["consoleLines"]
    cons.init(CENTER, WIDTH, HEIGHT, bg)

font_small = pg.Font(f"{g.assets_path}/font.ttf", 20)
db.load_settings = load_settings

update_sizes()
load_settings()

CURSOR_POSITION = (0,0)

def open_file(file):
    history.clear()
    global FILE_CONTENT, CURSOR_POSITION, FILE, file_extention, interactions, colors
    with open(f"{g.markups_path}/_base.json", "r") as fp:
        colors = json.load(fp)
        _base_colors = colors.copy()
    if file != "console":
        FILE = file
        file_extention = FILE.split(".")[-1].lower()
        if os.path.exists(file):
            with open(file, "r") as fp:
                FILE_CONTENT = [line.replace("\n","") for line in fp.readlines()]
                if not FILE_CONTENT:
                    FILE_CONTENT = ["",]
                CURSOR_POSITION = [len(FILE_CONTENT[-1]),len(FILE_CONTENT)]
        else:
            if dir_name := os.path.dirname(file):
                os.mkdir(dir_name)
            with open(file, "w") as fp:
                FILE_CONTENT = ["",]
                CURSOR_POSITION = [0,0]

        markup_json = f"{g.markups_path}/{file_extention}.json"

        if os.path.exists(markup_json):
            with open(f"{g.markups_path}/_any.json", "r") as fp:
                [colors.append(color) for color in json.load(fp)]
            with open(markup_json, "r") as fp:
                [colors.append(color) for color in json.load(fp)]

        with open(f"{g.config_path}/interactions.json", "r") as fp:
            interactions = json.load(fp)
        try:
            os.chdir(os.path.dirname(file))
            FILE = os.path.basename(file)
            cons.push("CWD has been changed")
        except OSError:
            FILE = os.path.basename(file)
            cons.push("CWD is already set")
        if not DO_HIGHLIGHTING:
            colors[:] = _base_colors
            del _base_colors
    else:
        with open(f"{g.config_path}/interactions.json", "r") as fp:
            interactions = json.load(fp)
        CURSOR_POSITION = [7,0]
        u.save(FILE, FILE_CONTENT)
        FILE = "console"
        FILE_CONTENT = ["..cmd:>",]
    init_interactions()
db.open_file = open_file
open_file(FILE)

FPS = 60
error = ""
while c.loop(FPS, bg):
    try:
        c.set_title(f"{NAME} - {VERSION} - {FILE}")
        if c.is_updating_sizes():
            update_sizes()
            cons.init(CENTER, WIDTH, HEIGHT, bg)
        if c.ctrl():
            if c.key_clicked("s"):
                u.save(FILE, FILE_CONTENT)
                cons.push("File saved.")
            if (offset := c.key_clicked(pg.K_PLUS) - c.key_clicked(pg.K_MINUS)):
                _old_size = font.get_linesize()
                FONT_SIZE += offset * 5
                FONT_SIZE = max(5, (FONT_SIZE // 5) * 5)
                FONT_WIDTH = (FONT_SIZE * 3) / 5
                font = pg.Font(f"{g.assets_path}/font.ttf", FONT_SIZE)
                _new_size = font.get_linesize()
                w.edits = [{ "type" : "set", "line" : line} for line in range(len(display))]

        handle_cursor_movement()
        handle_writing()
        handle_interactions()
        cons.update(cl.default_color, (WIDTH, HEIGHT))

        height = CURSOR_DISPLAY_POSITION[1]+MARGINS[1]+FONT_SIZE/3-DISPLAY_CAMERA_POSITION[1]
        if height < cons.bar.pos_Y-font.get_linesize()-12:
            c.text(
                CARET,
                (CURSOR_DISPLAY_POSITION[0]+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], height),
                color = CARET_COLOR,
                font = font,
            )

        DEBUG += c.key_clicked(pg.K_F3)
        DEBUG = DEBUG % 3
        if DEBUG:
            c.debug_list(
                f"Mouse Position: {c.mouse_position()}",
                f"Fps: {c.get_FPS()}",
                f"Perfomance: {1/c.get_delta() * 100}%",
                f"Color buffers: {len(colored)}",
                f"Cursor X,Y : {CURSOR_POSITION}",
                f"Selection : {SELECTION} - {selecting}",
                f"Font Size : {FONT_SIZE}",
                # f"history:",
                # *history[-32:],
                font = font_small,
            )
            c.text(
                CARET,
                (ACTUAL_POSITION[0]+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], ACTUAL_POSITION[1]+MARGINS[1]+FONT_SIZE/3-DISPLAY_CAMERA_POSITION[1]),
                color = "white",
                font = font,
            )

        if DEBUG == 2:
            c.debug_list(
                "        - FILE",
                *["\""+line.replace(" ", ".")+"\"" for line in FILE_CONTENT],
                font = font_small,
                position=(WIDTH*.5, 0),
                color="cyan"
            )
            c.debug_list(
                "DISPLAY",
                *["\""+line.replace(" ", ".")+"\"" for line in display],
                font = font_small,
                position=(WIDTH*.5, 0)
            )
        
        if c.ctrl() and c.key_clicked("o"):
            CURSOR_POSITION = [7,0]
            u.save(FILE, FILE_CONTENT)
            FILE = "console"
            FILE_CONTENT = ["..cmd:>",]
            init_interactions()
        if FILE == "console" and not "..cmd:>" in FILE_CONTENT[0]:
            CURSOR_POSITION = [7,0]
            FILE_CONTENT = ["..cmd:>",]
            init_interactions()
        if not (c.get_frames() % (1*30*60)):
            u.save(FILE, FILE_CONTENT)

        if c.key_clicked(pg.K_F5) and c.key_pressed(pg.K_F5) and not FILE == "console":
            u.save(FILE, FILE_CONTENT)
            db.debug(FILE)
    except Exception as e:
        if e == error:
            print("Closing to avoid catch looping.")
            break
        else:
            error = e
            print(f"An error occurred: {e}")
u.save(FILE, FILE_CONTENT)
print("Closing succesfully.")