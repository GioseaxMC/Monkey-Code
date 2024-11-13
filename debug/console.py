import pygame_canvas as c
import globals as g
from random import randint
import os

MAX_LENGHT = 150
MAX_LINES = 32

c.pg.font.init()

font = c.pg.Font(f"{g.assets_path}\\font.ttf",14)
line_size = font.get_linesize()
bar: c.sprite
do_update = 0
index = 0
log = ["" for _ in range(300)]
moving_bar = 0

render = font.render("\n".join(log[-MAX_LINES:]), 1, "white")

def get_color(bg):
    if sum(bg)//3 > 128:
        return [min(max(0,x+y), 255) for x,y in zip(bg, [-20,-20,-20])]
    return [min(max(0,x+y), 255) for x,y in zip(bg, [20,20,20])]

def init(center, width, height, bg):
    global HEIGHT
    bar.sprite_images[0] = c.rectangle(width, 20, get_color(bg))
    bar.set_position(center[0], height-(line_size*MAX_LINES//line_size+1)*line_size)
    bar.update(1)
    HEIGHT = height

def push(*prompts, as_list: list[str] = []):
    global log, do_update
    print(prompts)
    if len(prompts):
        prompt = " ".join(prompts).split("\n")
        print(prompt)
        for string in prompt:
            log.append(string)
    for string in as_list:
        push(string)
    for idx, line in enumerate(log):
        if len(line) > MAX_LENGHT:
            log.insert(idx+1, line[MAX_LENGHT:])
            log[idx] = line[:MAX_LENGHT]
    log = log[-300:]
    do_update = 1

def update(font_color, SCREEN):
    global do_update, render, moving_bar, MAX_LINES, index, log
    if c.mouse_position()[1] > bar.pos_Y:
        index += c.get_wheel()*2
        do_update = 1
    index = min(max(0, index), len(log)-MAX_LINES-1)
    if moving_bar or bar.touching_mouse() and c.mouse_down():
        do_update = 1
        moving_bar = 1
        bar.set_position(bar.pos_X, max(min(SCREEN[1]-line_size*3, c.mouse_position()[1]), line_size*5))
        MAX_LINES = (HEIGHT-bar.pos_Y-line_size)//line_size
        if c.get_left_released():
            moving_bar = 0
            bar.set_position(SCREEN[0]//2, SCREEN[1]-line_size*(MAX_LINES+1))
    if do_update:
        do_update = 0
        render = font.render("\n".join(log[-max(0,MAX_LINES+index-1):len(log)-index]), 1, font_color)
    c.blit(render, (20, SCREEN[1]-render.get_size()[1]-30))
    c.blit(bar.appearence, (0, SCREEN[1]-20))
    c.text(
        f"CWD: {os.getcwd()}",
        (5, SCREEN[1]-20),
        size=15,
        color=font_color,
        font=font,
    )
