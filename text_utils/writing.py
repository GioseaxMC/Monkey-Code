import pygame_canvas as c
from pygame_canvas import pygame as pg
import text_utils.utils as s
import text_utils.closings as close
from copy import copy
import clipboard as cb
from pprint import pprint as pp
from datetime import datetime as dt
import debug.debugger as debug


MOVEMENT = pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT
edits: list[dict] = []
history = []
action_id = 0
update_display = lambda x: x
popped_lines = 0

def append(_append, content):
    global history, edits, popped_lines, selection
    if (not len(history) or history[-1] != content) and _append:
        content.update(
            {
                "id" : action_id
            }
        )
        history.append(content)
    edits.append(
        {
        "line" : content["line"]+popped_lines,
        "type" : content["action"]
        }
    )

def pop_line(file, line, cursor, _append = 1):
    append(_append,
        {
            "action" : "insert",
            "line" : line,
            "content" : file[line],
            "cursor" : cursor.copy()
        }
    )
    return file.pop(line)

def insert_line(file, line, content, cursor, _append = 1):
    append(_append,
        {
            "action" : "pop",
            "line" : line,
            "cursor" : cursor.copy()
        }
    )
    file.insert(line, content)

def set_line(file, line, content, cursor, _append = 1):
    append(_append,
        {
            "action" : "set",
            "line" : line,
            "content" : file[line],
            "cursor" : cursor.copy()
        }
    )
    file[line] = content

def add_to_line(file, line, content, cursor, _append = 1):
    set_line(file, line, file[line]+content, cursor, _append)

def remove_selection(file: list, sele, cursor):
    if sele[1][1] - sele[0][1]:
        sorted_sel = sorted(sele, key=lambda x: x[1])
        removed_lines = 0
        for global_line, local_line in enumerate(range(sorted_sel[1][1]-sorted_sel[0][1]+1), sorted_sel[0][1]):
            if local_line == 0:
                set_line(file, global_line-removed_lines, file[global_line-removed_lines][:sorted_sel[0][0]], cursor)
            elif global_line == sorted_sel[1][1]:
                set_line(file, global_line-removed_lines, file[global_line-removed_lines][sorted_sel[1][0]:], cursor)
            else:
                pop_line(file, global_line-removed_lines, cursor)
                removed_lines += 1
        cursor[:] = sorted_sel[0]
        add_to_line(file, sorted_sel[0][1], file[sorted_sel[0][1]+1], cursor)
        pop_line(file, sorted_sel[0][1]+1, cursor)
    elif sele[0][0] - sele[1][0]:
        global_line = sele[0][1]
        sorted_sel = sorted(sele, key=lambda x: x[0])
        set_line(file, global_line, file[global_line][:sorted_sel[0][0]] + file[global_line][sorted_sel[1][0]:], cursor)
        cursor[:] = sorted_sel[0]

def copy_selection(file: list, sele):
    copy_string = ""
    if sele[1][1] - sele[0][1]:
        sorted_sel = sorted(sele.copy(), key=lambda x: x[1])
        for global_line, local_line in enumerate(range(sorted_sel[1][1]-sorted_sel[0][1]+1), sorted_sel[0][1]):
            if local_line == 0:
                copy_string += file[global_line][sorted_sel[0][0]:]+"\n"
            elif global_line == sorted_sel[1][1]:
                copy_string += file[global_line][:sorted_sel[1][0]]
            else:
                copy_string += file[global_line]+"\n"
    elif sele[0][0] - sele[1][0]:
        global_line = sele[0][1]
        sorted_sel = sorted(sele.copy(), key=lambda x: x[0])
        copy_string += file[global_line][sorted_sel[0][0]:sorted_sel[1][0]]
    cb.copy(copy_string)

def _return(file, cursor, selecting, sele):
    before = file[cursor[1]][:cursor[0]]
    tabs = 0
    temp_before = before
    while temp_before[:4].isspace():
        tabs += 1
        temp_before = temp_before[4:]
    del temp_before
    if before:
        insert_line(file, cursor[1]+1, (("    "*(tabs+1)) if before[-1] == ":" else "    "*tabs)+file[cursor[1]][cursor[0]:], cursor)
        cursor[0] = 4*(tabs+1) if before[-1] == ":" else 4*tabs
    else:
        insert_line(file, cursor[1]+1, file[cursor[1]][cursor[0]:], cursor)
    set_line(file, cursor[1], before, cursor)
    cursor[1] += 1

def move(file, cursor, selecting, sele: list, offset):
    sele = sorted(sele, key=lambda x: x[1])
    if selecting:
        if not (s.check_bounds(file, sele[max(0, offset)][1]+offset) and s.check_bounds(file, sele[max(0, -offset)][1])):
            return
        to_swap = pop_line(file, sele[max(0, offset)][1]+offset, cursor)
        cursor[1] += offset
        for selection in sele:
            selection[1] += offset
        insert_line(file, sele[max(0, -offset)][1]-offset, to_swap, cursor)
    else:
        if not (s.check_bounds(file, cursor[1]+offset) and s.check_bounds(file, cursor[1])):
            return
        to_swap = pop_line(file, cursor[1]+offset, cursor)
        cursor[1] += offset
        insert_line(file, cursor[1]-offset, to_swap, cursor)

def _del(file, cursor, selecting, sele):
    if selecting[0]:
        selecting[0] = 1
        remove_selection(file, sele, cursor)
    else:
        if cursor[0] == len(file[cursor[1]]) and cursor[1] < len(file)-1:
            removed_row = pop_line(file, cursor[1]+1, cursor)
            add_to_line(file, cursor[1], removed_row, cursor)
        else:
            set_line(file, cursor[1], file[cursor[1]][:cursor[0]] + file[cursor[1]][min(cursor[0]+1, len(file[cursor[1]])):], cursor)

def _tab(file, cursor, selecting, sele):
    set_line(file, cursor[1], file[cursor[1]][:cursor[0]] + "    " + file[cursor[1]][cursor[0]:], cursor)
    cursor[0] += 4

def add_tab_line(file, line, cursor):
    set_line(file, line, "    " + file[line], cursor)

def rem_tab_line(file, line, cursor):
    if file[line][:4].isspace():
        set_line(file, line, file[line][4:], cursor)
        return 1
    return 0

def add_tab_for(file, cursor, selecing, sele: list):
    ssort = sorted(sele, key=lambda x: x[1])
    for line in range(ssort[1][1] - ssort[0][1] + 1):
        line += ssort[0][1]
        add_tab_line(file, line, cursor)
    sele[0][0] += 4
    sele[1][0] += 4
    cursor[0] += 4

def rem_tab_for(file, cursor, selecing, sele: list):
    ssort = sorted(sele, key=lambda x: x[1])
    moved_any = 0
    for line in range(ssort[1][1] - ssort[0][1] + 1):
        line += ssort[0][1]
        if file[line][:4].isspace():
            moved_any = rem_tab_line(file, line, cursor)
    if moved_any:
        sele[0][0] -= 4
        sele[1][0] -= 4
        cursor[0] -= 4

def _paste(file, cursor, selecting, sele):
    if selecting[0]:
        remove_selection(file, sele, cursor)
        selecting[0] = 0
    lines = cb.paste().split("\n")
    for idx, line in enumerate(lines):
        set_line(file, cursor[1], file[cursor[1]][:cursor[0]] + line + file[cursor[1]][cursor[0]:], cursor)
        cursor[0] += len(line)
        if idx != len(lines)-1:
            before = file[cursor[1]][:cursor[0]]
            insert_line(file, cursor[1]+1, file[cursor[1]][cursor[0]:], cursor)
            set_line(file, cursor[1], before, cursor)
            cursor[0] = 0
            cursor[1] += 1
    add_to_line(file, cursor[1], "", cursor)

def _cut(file, cursor, selecting, sele):
    if selecting[0]:
        selecting[0] = 0
        copy_selection(file, sele)
        remove_selection(file, sele, cursor)

def _backspace(file, cursor, selecting, sele):
    if selecting[0]:
        selecting[0] = 0
        remove_selection(file, sele, cursor)
    else:
        if c.ctrl():
            before, after = file[cursor[1]][:max(0, cursor[0])], file[cursor[1]][cursor[0]:]
            if before:
                cursor0 = cursor[0]
                if before.isspace():
                    before = ""
                    cursor0 = 0
                while True:
                    if before:
                        before = before[:-1]
                        cursor0 -= 1
                        if before and before[-1] in " \"()[]{}.,-+/*<>":
                            break
                        else:
                            ...
                    else:
                        break
                set_line(file, cursor[1], before+after, cursor)
                cursor[0] = cursor0
            else:
                cursor[0] -= 1
        else:
            before, after = file[cursor[1]][:max(0, cursor[0])], file[cursor[1]][cursor[0]:]
            if before[-4:].isspace() and len(before[-4:]) == 4:
                before = before[:-4]
                offset = 4
            else:
                before = before[:-1]
                offset = 1
            set_line(file, cursor[1], before+after, cursor)
            cursor[0] -= offset
        if cursor[0] < 0 and cursor[1] > 0:
            removed_row = pop_line(file, cursor[1], cursor)
            cursor[1] -= 1
            cursor[0] = len(file[cursor[1]])
            add_to_line(file, cursor[1], removed_row, cursor)

def write(file: list[str], display: list[str], cursor: tuple[int, int], sele, selecting, current_file):
    global action_id, popped_lines
    popped_lines = 0
    action_id = dt.timestamp(dt.now())
    key = c.get_clicked_key()
    if key and not key in MOVEMENT:
        if key == pg.K_BACKSPACE:
            _backspace(file, cursor, selecting, sele)
        
        elif key == pg.K_DELETE:
            _del(file, cursor, selecting, sele)
        
        elif key == pg.K_RETURN and c.key_pressed(pg.K_RETURN):
            if selecting[0]:
                remove_selection(file, sele, cursor)
                selecting[0] = 0
            if "..cmd:>" in file[cursor[1]]:
                debug.run(file[cursor[1]].replace("..cmd:>",""))
            else:
                _return(file, cursor, selecting, sele)

        elif key == pg.K_HOME:
            if c.ctrl():
                cursor[1] = 0
            cursor[0] = 0

        elif key == pg.K_END:
            if c.ctrl():
                cursor[1] = len(display)-1
            cursor[0] = len(display[cursor[1]])

        elif not c.ctrl() and key == pg.K_TAB:
            if selecting[0]:
                if c.shift():
                    rem_tab_for(file, cursor, selecting, sele)
                else:
                    add_tab_for(file, cursor, selecting, sele)
            else:
                if c.shift():
                    rem_tab_line(file, cursor[1], cursor)
                    cursor[0] -= 4
                else:
                    _tab(file, cursor, selecting, sele)

        elif c.ctrl() and key == pg.K_v:
            _paste(file, cursor, selecting, sele)
            # tab tab removal fix
            # _tab(file, cursor, selecting, sele)
            # set_line(file, cursor[1], file[cursor[1]][:-4], cursor)

        elif c.ctrl() and key == pg.K_x:
            _cut(file, cursor, selecting, sele)

        elif c.ctrl() and key == pg.K_c:
            copy_selection(file, sele)

        elif (key_unicode := c.get_clicked_unicode()) and not c.ctrl():
            # print(f"uncaught key {key}" + (f" : {key_unicode}" if key_unicode else "-"))
            if key_unicode and key_unicode.isprintable():
                # print("writing")
                if selecting[0]:
                    selecting[0] = 0
                    remove_selection(file, sele, cursor)
                after = file[cursor[1]][cursor[0]:]
                if not (len(after) and after[0] in "])}\"'" and key_unicode == after[0]):
                    set_line(file, cursor[1], file[cursor[1]][:cursor[0]] + close.get_closing_char(key_unicode) + after, cursor)
                cursor[0] += 1
                