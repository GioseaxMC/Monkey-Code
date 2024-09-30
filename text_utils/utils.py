from pprint import pprint as pp
import os

def check_tokens(file, file2):
    condition = 0
    for c, p in zip(file, file2):
        for x, y in zip(c.split(), p.split()):
            condition = condition or len(x) != len(y)
    return condition

def check_bounds(list, idx):
    return (0 <= idx < len(list))

def save(file, file_content):
    print(os.getcwd())
    if file == "console":
        return
    with open(file, "w") as fp:
        fp.write("\n".join(file_content)) # .replace("\r", "")
    print("Saved suffessfully.")

def get(list: list, idx):
    try:
        return list[idx]
    except IndexError:
        return None
