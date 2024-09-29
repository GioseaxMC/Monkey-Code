import subprocess as sb

def call(*arguments, error: str = -1):
    try:
        sb.call(arguments)
    except Exception as e:
        if error == -1:
            print(f"Error: {e}")
        else:
            print(error)
        return e

def debug(file_name):
    name = file_name.split(".")
    extention = "".join(name[-1:])
    name = "".join(name[:-1])
    print(f"Debugging: {name}.{extention}")
    if extention == "cpp":
        call("g++", file_name, "-o", name)
        call(f".\\{name}.exe", error="Compilation failed.")