import os
import sys
from text_utils import utils as u
import string

# Get all possible drive letters (A-Z)
available_drives = [f"{d}:" for d in string.ascii_uppercase if os.path.exists(f"{d}:")]

print("Available drives:", available_drives)

if getattr(sys, 'frozen', False):
    app_path = sys.executable
    if os.getcwd() == os.path.dirname(app_path):
        u.add_to_path(os.getcwd())
        print("CURRENT WD:", os.path.dirname(app_path))
        print(f"Added command \"monkey\" <file-name> to path")
        os.system("pause")
        sys.exit()
    # sys.stdout = open(os.devnull, 'w')
else:
    app_path = os.path.abspath(__file__)
    print("CURRENT WD:", os.path.dirname(app_path))
    
markups_path = f"{os.path.dirname(app_path)}/assets/config/markups"
themes_path = f"{os.path.dirname(app_path)}/assets/config/themes"
config_path = f"{os.path.dirname(app_path)}/assets/config"
assets_path = f"{os.path.dirname(app_path)}/assets"