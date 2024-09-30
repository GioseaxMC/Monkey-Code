import subprocess as sb
import shlex
import os

open_file = lambda x: x
cwd = os.getcwd()
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

def call(*arguments, error: str = -1, _cwd=cwd):
    # try:
        print(" ".join(arguments), "cwd:", f'"{_cwd}"')
        sb.call(" ".join(arguments), cwd=_cwd)
        return True
    # except Exception as e:
    #     if error == -1:
    #         print(f"Error: {e}")
    #     else:
    #         print(error)
    #     return False

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
            if call("g++", "\""+file_name+"\"", "-o", name, _cwd=os.getcwd()):
                call(f".\\{name}.exe", error="Compilation failed.", _cwd=os.getcwd())
        case ".py":
            call("python", "\""+file_name+"\"", _cwd=os.getcwd())
        case "undefined":
            call("\""+file_name+"\"")

def run(command):
    cmd, args = parse_command(command)

    match cmd:
        case "open"|"o":
            try:
                open_file(args[0])
            except IndexError:
                open_file("file.txt")
        case "exit":
            exit(0)
        case _:
            debug(cmd)


