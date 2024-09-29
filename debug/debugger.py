import subprocess as sb

def debug(file_name):
    name = file_name.split(".")
    extention = "".join(name[-1:])
    name = "".join(name[:-1])
    print(f"Debugging: {name}.{extention}")
    if extention == "cpp":
        sb.call(["g++", file_name, "-o", name])
        sb.call(f".\\{name}.exe")