import subprocess as sb
import shlex
import os
from webbrowser import open as open_html
import json
import shutil

open_file = lambda file: bool
load_settings = lambda: None  
cwd = os.getcwd()
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
markups_path: str
config_path: str
assets_path: str

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

def call(*arguments, error: str = -1, _cwd=cwd):
    try:
        sb.call(arguments, cwd=_cwd)
        return True
    except Exception as e:
        if error == -1:
            print(f"Error: {e}")
        else:
            print("no code", error)
        return False

def debug(file_name):
    file_name = file_name.replace("\"","")
    _, extention = os.path.splitext(file_name)
    name = os.path.basename(file_name)
    name, _ = os.path.splitext(name)
    print(f"Debugging: {name}{extention}")
    match extention:
        case ".cpp":
            try:
                os.remove(name+".exe")
            except FileNotFoundError:
                ...
            if call("g++", file_name, "-o", name, _cwd=os.getcwd()):
                call(f".\\{name}.exe", error="Compilation failed.", _cwd=os.getcwd())
        case ".py":
            call("python", file_name, _cwd=os.getcwd())
        case ".html":
            open_html(f"file://{os.getcwd()+"/"+file_name}")
        case "undefined":
            call("\""+file_name+"\"")

def set_settings(args):
    with open(f"{config_path}/settings.json", "r") as fp:
        s = json.load(fp)
        if s.get(args[0]):
            try:
                evaluated = eval(args[1])
            except NameError:
                evaluated = args[1]
            if type(s.get(args[0])) == type(evaluated):
                print("Updating setting")
                with open(f"{config_path}/settings.json", "w") as _fp:
                    s[args[0]] = evaluated
                    json.dump(s, _fp, indent=4)

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
            if args[0] == "reset":
                shutil.copy(f"{config_path}/default_settings.json", f"{config_path}/settings.json")
                load_settings()
                open_file("console")
            else:
                set_settings(args)
                load_settings()
                open_file("console")
        case _:
            open_file("console")


