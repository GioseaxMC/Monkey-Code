import subprocess as sb
import shlex
import os
from webbrowser import get
import json
import shutil
import globals as g
from . import console
import threading as t

open_file = lambda file: bool
load_settings = lambda: None
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'

def parse_command(command_string):
    command_string = command_string + " fixer "
    # Use shlex.split to handle quoted arguments and spaces
    tokens = shlex.split(command_string, posix=False)

    if not tokens:
        return None, []
    
    # The first token is the command
    loc_command = tokens[0]
    
    # The rest are arguments
    arguments = [arg.strip('"') for arg in tokens[1:] if arg != 'fixer']

    return loc_command, arguments

with open(f"{g.assets_path}/compilers/commands.json", "r") as fp:
    commands_file = json.load(fp)

def call(command, error: str = -1, _cwd=os.getcwd(), _shell=0):
    try:
        console.push("running:",command)
        result = sb.run(command, cwd=_cwd, capture_output=1, text=1, check=0, shell=_shell)
        console.push(as_list=result.stdout.splitlines())
        if len(result.stderr.splitlines()):
            console.push(as_list=result.stderr.splitlines())
            return False
        return True
    except Exception as e:
        console.push("Error:", str(e))
        return False

def t_call(*args, **kwargs):
    thread = t.Thread(target=call,
                      args=args,
                      kwargs=kwargs)
    thread.start()


def debug(file_name):
    global commands_file
    file_name = file_name.replace("\"","")
    _, extention = os.path.splitext(file_name)
    if extention[0] == ".":
        extention = extention[1:]
    name = os.path.basename(file_name)
    name, _ = os.path.splitext(name)
    console.push(f"Debugging: {name}.{extention}")
    commands = dict()
    for key in commands_file:
        commands[key] = commands_file[key].replace(r"%filename%", name).replace(r"%filename_ext%", f"{name}.{extention}").replace(r"%cwd%", os.getcwd())
    match extention:
        case "cpp":
            try:
                os.remove(name+".exe")
            except FileNotFoundError:
                ...
            cpp = commands["cpp"]
            if call(cpp, _cwd=os.getcwd()):
                console.push(f"Compilation successful... running {name}.exe")
                t_call(f"start .\\{name}", _cwd=os.getcwd(), _shell=1)
        case "py":
            py = commands["py"]
            t_call(py, _cwd=os.getcwd(), _shell=1)
        case "html":
            html = commands["html"]
            console.push(f"opening {html} in default browser.")
            get().open_new_tab(html)

def set_settings(args):
    if len(args) < 2:
        console.push("Invalid Syntax, expected 2 arguments, got 1")
        return
    with open(f"{g.themes_path}/settings.json", "r") as fp:
        s = json.load(fp)
        if s.get(args[0]) != None:
            try:
                evaluated = eval(args[1])
            except (NameError, SyntaxError):
                evaluated = args[1].replace("\\n", "\n")
            if type(s.get(args[0])) == type(evaluated):
                if type(evaluated) == list:
                    evaluated = [max(min(255, i), 0) for i in evaluated]
                console.push(f"Setting {args[0]} to {type(evaluated)}: {evaluated}")
                with open(f"{g.themes_path}/settings.json", "w") as _fp:
                    s[args[0]] = evaluated
                    json.dump(s, _fp, indent=4)
            else:
                console.push(f"Error: cannot set {args[0]} of {type(s[args[0]])}: {s[args[0]]} to {type(evaluated)}: {evaluated}")
        else:
            console.push("Expected 2 arguments, got 0.")

def run(command):
    cmd, args = parse_command(command)
    match cmd:
        case "open"|".":
            if not len(args):
                return console.push("open <file_path>")
            else:
                open_file(args[0])
                return console.push(f"Loading: {args[0]}")
        case "set":
            if not len(args):
                open_file("console")            
                return console.push("set <setting|load> <value|theme>")
            match args[0]:
                case "reset":
                    shutil.copy(f"{g.themes_path}/reset.json", f"{g.themes_path}/settings.json")
                case "load":
                    if len(args) < 2:
                        console.push("Invalid Syntax, expected 2 arguments, got 1")
                        return
                    if not os.path.exists(f"{g.themes_path}/{args[1]}.json"):
                        return
                    with open(f"{g.themes_path}/settings.json", "r") as fpa:
                        default = json.load(fpa)
                    with open(f"{g.themes_path}/{args[1]}.json", "r") as fpa:
                        new = json.load(fpa)
                        default.update(new)
                    with open(f"{g.themes_path}/settings.json", "w") as fpa:
                        json.dump(default, fpa, indent=4)
                    
                case _:
                    set_settings(args)
            load_settings()
            open_file("console")
        case _:
            open_file("console")


