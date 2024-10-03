from pprint import pprint as pp
import os
import subprocess as sb
import winreg

def check_tokens(file, file2):
    condition = 0
    for c, p in zip(file, file2):
        for x, y in zip(c.split(), p.split()):
            condition = condition or len(x) != len(y)
    return condition

def check_bounds(list, idx):
    return (0 <= idx < len(list))

def save(file, file_content):
    if file == "console":
        return
    with open(file, "w") as fp:
        fp.write("\n".join(file_content)) # .replace("\r", "")

def get(list: list, idx):
    try:
        return list[idx]
    except IndexError:
        return None

def get_user_path():
    # Open the registry key for the current user's environment variables
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
            user_path, _ = winreg.QueryValueEx(key, 'Path')
            print(user_path)
            return user_path
    except FileNotFoundError:
        return None

def add_to_path(directory): 
    if current_path := get_user_path():
        if directory.lower() not in current_path.lower().split(";") or 0:
            command = f"setx PATH \"{current_path};{directory}\"".replace("/","\\")
            print(command)
            sb.call(command)
            print(f"{directory} added to PATH.")
        else:
            print(f"{directory} is already in the PATH.")
    else:
        print("not doing")

def bool_to_sign(value: bool):
    if value:
        return 1
    else:
        return -1

def sign(value: int):
    return bool_to_sign(value >= 0)