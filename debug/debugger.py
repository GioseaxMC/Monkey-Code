import subprocess as sb
import shlex
import os
from webbrowser import get
import json
import shutil
import globals as g

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

def call(command, error: str = -1, _cwd=os.getcwd()):
    try:
        print("running:",command)
        sb.call(command, cwd=_cwd)
        return True
    except Exception as e:
        if error == -1:
            print(f"Error: {e}")
        else:
            print("no code", error)
        return False

def debug(file_name):
    global commands_file
    file_name = file_name.replace("\"","")
    _, extention = os.path.splitext(file_name)
    if extention[0] == ".":
        extention = extention[1:]
    name = os.path.basename(file_name)
    name, _ = os.path.splitext(name)
    print(f"Debugging: {name}.{extention}")
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
                call(f".\\{name}.exe", error="Compilation failed.", _cwd=os.getcwd())
        case "py":
            py = commands["py"]
            call(py, _cwd=os.getcwd())
        case "html":
            html = commands["html"]
            print(f"opening {html} in default browser.")
            get().open_new_tab(html)

def set_settings(args):
    if len(args) < 2:
        print("Invalid Syntax, expected 2 arguments, got 1")
        return
    with open(f"{g.themes_path}/settings.json", "r") as fp:
        s = json.load(fp)
        if s.get(args[0]) != None:
            try:
                evaluated = eval(args[1])
            except (NameError, SyntaxError):
                evaluated = args[1].replace("\\n", "\n")
            print(f"Error: cannot set {args[0]} of {type(s[args[0]])}: {s[args[0]]} to {type(evaluated)}: {evaluated}")
            if type(s.get(args[0])) == type(evaluated):
                if type(evaluated) == list:
                    evaluated = [max(min(255, i), 0) for i in evaluated]
                print(f"Setting {args[0]} to {type(evaluated)}: {evaluated}")
                with open(f"{g.themes_path}/settings.json", "w") as _fp:
                    s[args[0]] = evaluated
                    json.dump(s, _fp, indent=4)
            else:
                print(f"Error: cannot set {args[0]} of {type(s[args[0]])}: {s[args[0]]} to {type(evaluated)}: {evaluated}")
        else:
            print("Expected 2 arguments, got 0.")

def run(command):
    cmd, args = parse_command(command)
    match cmd:
        case "open"|".":
            try:
                open_file(args[0])
            except IndexError:
                open_file("file.txt")
        case "exit":
            exit(0)
        case "set":
            match args[0]:
                case "reset":
                    shutil.copy(f"{g.themes_path}/reset.json", f"{g.themes_path}/settings.json")
                    load_settings()
                    open_file("console")
                case "load":
                    if len(args) < 2:
                        print("Invalid Syntax, expected 2 arguments, got 1")
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
                    
                    load_settings()
                    open_file("console")            
                case _:
                    set_settings(args)
                    load_settings()
                    open_file("console")
        case _:
            open_file("console")


