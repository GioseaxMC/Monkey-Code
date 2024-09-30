import pygame_canvas as c
from pygame_canvas import pygame as pg
import text_utils.writing as w
import text_utils.utils as u
import text_utils.interactions as cl
import json
from pprint import pprint as pp
import debug.debugger as db
import sys
import os

VERSION = "Alpha 1.0.0"

print(__file__)

try:
    FILE = sys.argv[1:][0]
except:
    FILE = ".\\file.txt"
cwd = os.getcwd()
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
ctrl_zing = 0
markups_path = f"{os.path.dirname(__file__)}/assets/config/markups"
config_path = f"{os.path.dirname(__file__)}/assets/config"
assets_path = f"{os.path.dirname(__file__)}/assets"


c.window(1290, 720, title = f"Text editor - {VERSION}", smallest_window_sizes=(1290, 720))

pg.key.set_repeat(500, 30)

def update_sizes():
    global WIDTH, HEIGHT, CENTER, MARGINS
    WIDTH, HEIGHT = c.screen_size()
    CENTER = WIDTH//2, HEIGHT/2
    MARGINS = WIDTH*.15, 100
update_sizes()

def handle_cursor_movement():
    global ACTUAL_POSITION, CURSOR_POSITION, CURSOR_DISPLAY_POSITION, SELECTION, selecting
    #handle selection logic
    if c.key_clicked(pg.K_ESCAPE):
        selecting = 0
    offset = c.key_clicked(pg.K_RIGHT) - c.key_clicked(pg.K_LEFT) - (c.get_wheel() * c.shift())
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
            CURSOR_POSITION[0] += offset
            try:
                _is_space_start = FILE_CONTENT[CURSOR_POSITION[1]][CURSOR_POSITION[0]].isspace()
            except IndexError:
                _is_space_start = 0
            while True:
                CURSOR_POSITION[0] += offset
                if CURSOR_POSITION[0] < 0 or CURSOR_POSITION[0] >= len(display[CURSOR_POSITION[1]]) or FILE_CONTENT[CURSOR_POSITION[1]][CURSOR_POSITION[0]].isspace() != _is_space_start or FILE_CONTENT[CURSOR_POSITION[1]][CURSOR_POSITION[0]] in "()[]{}.,-+/*<>":
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
        CURSOR_POSITION[1] += c.key_clicked(pg.K_DOWN) - c.key_clicked(pg.K_UP) - (c.get_wheel() * (not c.shift()))
        if CURSOR_POSITION[1] >= len(display):
            CURSOR_POSITION[0] = len(display[-1])
        if CURSOR_POSITION[1] < 0:
            CURSOR_POSITION[0] = 0
        CURSOR_POSITION[1] = min(max(CURSOR_POSITION[1], 0), len(display)-1)
        CURSOR_POSITION[0] = min(max(CURSOR_POSITION[0], 0), len(display[CURSOR_POSITION[1]]))

    #smooth movement
    ACTUAL_POSITION = [i*j for i, j in zip(CURSOR_POSITION, [FONT_WIDTH, font.get_linesize()])]
    CURSOR_DISPLAY_POSITION[0] += (ACTUAL_POSITION[0] - CURSOR_DISPLAY_POSITION[0]) / 3
    CURSOR_DISPLAY_POSITION[1] += (ACTUAL_POSITION[1] - CURSOR_DISPLAY_POSITION[1]) / 3
    if c.shift() and selecting:
        SELECTION[1] = CURSOR_POSITION.copy()
    handle_cursor_position()

def draw_selection():
    if selecting:
        _color = [40,40,40]
        _size_boost = 22
        _offsetY = -4
        try:
            if SELECTION[1][1] - SELECTION[0][1]:
                sorted_sel = sorted(SELECTION, key=lambda x: x[1])
                for global_line, local_line in enumerate(range(sorted_sel[1][1]-sorted_sel[0][1]+1), sorted_sel[0][1]):
                    if local_line == 0:
                        x = (1+len(display[global_line]) - sorted_sel[0][0])
                        surface = c.rounded_rectangle(x*FONT_WIDTH, FONT_SIZE+_size_boost, 14, _color)
                        c.blit(surface, (sorted_sel[0][0]*FONT_WIDTH+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], global_line*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1]))
                    elif global_line == sorted_sel[1][1]:
                        x = (sorted_sel[1][0])
                        surface = c.rounded_rectangle(x*FONT_WIDTH, FONT_SIZE+_size_boost, 14, _color)
                        c.blit(surface, (MARGINS[0]-DISPLAY_CAMERA_POSITION[0], global_line*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1]))
                    else:
                        x = (1+len(display[global_line]))
                        surface = c.rounded_rectangle(x*FONT_WIDTH, FONT_SIZE+_size_boost, 14, _color)
                        c.blit(surface, (MARGINS[0]-DISPLAY_CAMERA_POSITION[0], global_line*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1]))
            elif SELECTION[0][0] - SELECTION[1][0]:
                sorted_sel = sorted(SELECTION, key=lambda x: x[0])
                surface = c.rounded_rectangle((sorted_sel[1][0] - sorted_sel[0][0]) * FONT_WIDTH, FONT_SIZE+_size_boost, 14, _color)
                c.blit(surface, ((sorted_sel[0][0])*FONT_WIDTH+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], SELECTION[0][1]*font.get_linesize()+_offsetY+MARGINS[1]-DISPLAY_CAMERA_POSITION[1]))
        except IndexError:
            print("waiting for threads...")

def handle_cursor_position():
    x = CURSOR_DISPLAY_POSITION[0] - CAMERA_POSITION[0] - WIDTH*.5 + WIDTH*.2 # adding moves to the left
    if abs(x) > WIDTH*.4:
        CAMERA_POSITION[0] += x / 10
        # CAMERA_POSITION[0] = max(CAMERA_POSITION[0], 0)
    DISPLAY_CAMERA_POSITION[0] += (CAMERA_POSITION[0] - DISPLAY_CAMERA_POSITION[0]) / 5

    y = CURSOR_DISPLAY_POSITION[1] - CAMERA_POSITION[1] - HEIGHT*.5 + 120 #arbitrary (removing the initial margin)
    if abs(y) > HEIGHT*.35:
        CAMERA_POSITION[1] += y / 10
    DISPLAY_CAMERA_POSITION[1] += (CAMERA_POSITION[1] - DISPLAY_CAMERA_POSITION[1]) / 5

def handle_writing():
    global history, FILE_CONTENT, CURSOR_POSITION, previous_file, SELECTION, selecting, ctrl_zing, FPS
    mutable = [selecting,]
    # ctrlz
    if (ctrl_zing or (c.ctrl() and c.key_clicked("z"))) and len(history):
        ctrl_zing = 1
        FPS = 0
        item = history.pop()
        match item["action"]:
            case "set":
                w.set_line(FILE_CONTENT, item["line"], item["content"], CURSOR_POSITION, 0)
            case "pop":
                w.pop_line(FILE_CONTENT, item["line"], CURSOR_POSITION, 0)
            case "insert":
                w.insert_line(FILE_CONTENT, item["line"], item["content"], CURSOR_POSITION, 0)
        CURSOR_POSITION = item["cursor"]

        if (not len(history)) or history[-1].get("id") != item.get("id"):
            ctrl_zing = 0
            FPS = 60
            # history.pop()
    else:
        w.write(FILE_CONTENT, display, CURSOR_POSITION, SELECTION, mutable)
        selecting = mutable[0]

def init_colors():
    global colored, display, color_surfaces_list, text_display_surfaces
    display = cl.handle_interactions(FILE_CONTENT, interactions)
    display, colored = cl.handle_colors(display, colors)
    text_display_surfaces = [font.render(row, 1, cl.default_color) for row in display]
    color_surfaces_list = []
    for cfile in colored:
        colored_file_list = []
        color = cfile["color"]
        for row in cfile["file"]:
            colored_file_list.append(
                font.render(row, 1, color)
            )
        color_surfaces_list.append(colored_file_list)

def update_display():
    global display, colors, color_surfaces_list, text_display_surfaces, display_edits
    for ed_idx in range(len(w.edits)):
        edit = w.edits.pop(0)
        idx = edit["line"]
        match type := edit["type"]:
            case "pop" | "set":
                display = cl.handle_interactions_at_row(idx, FILE_CONTENT, display, interactions, edit["type"])
                cl.handle_colors_at_row(idx, display, colors, color_surfaces_list, text_display_surfaces, font, edit["type"])
            case "insert":
                display.pop(idx)
                for color in color_surfaces_list:
                    color.pop(idx)
                text_display_surfaces.pop(idx)
    if any(w.edits):
        display_edits.append(str(w.edits))
    w.edits.clear()
w.update_display = update_display

def handle_interactions():
    update_display()
    draw_selection()
    cl.draw_text(text_display_surfaces, color_surfaces_list, MARGINS, DISPLAY_CAMERA_POSITION, font.get_linesize())

FONT_SIZE = 30
FONT_WIDTH = (FONT_SIZE * 3) / 5
font = pg.Font(f"{assets_path}/font.ttf", FONT_SIZE)
font_small = pg.Font(f"{assets_path}/font.ttf", 20)
CURSOR_POSITION = (0,0)

# TODO make color based on colors.json
bg = (25, 25, 25)

def open_file(file):
    global FILE_CONTENT, CURSOR_POSITION, FILE, file_extention, interactions, colors
    FILE = file
    file_extention = FILE.split(".")[-1].lower()
    if os.path.exists(file):
        with open(file, "r") as fp:
            FILE_CONTENT = [line.replace("\n","") for line in fp.readlines()]
            if not FILE_CONTENT:
                FILE_CONTENT = ["",]
            CURSOR_POSITION = [len(FILE_CONTENT[-1]),len(FILE_CONTENT)]
    else:
        try:
            os.mkdir(os.path.dirname(file))
        except (FileExistsError, FileNotFoundError) as e:
            print(f"source exists: {e}")
        with open(file, "w") as fp:
            FILE_CONTENT = ["",]
            CURSOR_POSITION = [0,0]

    markup_json = f"{markups_path}/{file_extention}.json"

    with open(f"{config_path}/default_theme.json", "r") as fp:
        colors = json.load(fp)

    if os.path.exists(markup_json):
        with open(f"{markups_path}/any.json", "r") as fp:
            [colors.append(color) for color in json.load(fp)]
        with open(markup_json, "r") as fp:
            [colors.append(color) for color in json.load(fp)]

    with open(f"{config_path}/interactions.json", "r") as fp:
        interactions = json.load(fp)
    try:
        os.chdir(os.path.dirname(file))
    except OSError:
        print("not opening")
    init_colors()
db.open_file = open_file
open_file(FILE)

FPS = 60
while c.loop(FPS, bg):
    c.set_title(f"Text editor - {VERSION} - {FILE}")
    if c.is_updating_sizes():
        update_sizes()
    if c.ctrl() and c.key_clicked("s"):
        u.save(FILE, FILE_CONTENT)

    handle_cursor_movement()
    handle_writing()
    handle_interactions()
    c.text(
        "_",
        (CURSOR_DISPLAY_POSITION[0]+MARGINS[0]-DISPLAY_CAMERA_POSITION[0], CURSOR_DISPLAY_POSITION[1]+MARGINS[1]+10-DISPLAY_CAMERA_POSITION[1]),
        color = [150, 255, 150],
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
            # f"history:",
            # *history[-32:],
            font = font_small,
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
        init_colors()
    if FILE == "console" and not "..cmd:>" in FILE_CONTENT[0]:
        CURSOR_POSITION = [7,0]
        FILE_CONTENT = ["..cmd:>",]
        init_colors()

    if c.key_clicked(pg.K_F5) and c.key_pressed(pg.K_F5) and not FILE == "console":
        print("pressed")
        u.save(FILE, FILE_CONTENT)
        db.debug(FILE)

u.save(FILE, FILE_CONTENT)
print("Closing succesfully.")