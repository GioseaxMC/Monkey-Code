# Monkey Editor

A Monkeytype inspired file and code editor

## Usage

### Open

To open the program (after following the download instructions) you just need to run the command "monkey <file-path>" to open the desired file you want to edit
> similar to how you do "code ." to open vscode in a directory, except it's file

### Download

Click the button below to download the file:

[![Download File](https://img.shields.io/badge/Download-Monkey%20Editor-brightgreen)](https://github.com/GioseaxMC/Monkey-Editor/raw/refs/heads/main/distribution/Monkey%20Editor.zip)

### Instructions:
Don't extract the zip file, instead:
- Place the zip in the desired installation directory
- open the zip and run the Monkey.exe file
- You will be prompted to extract in the directory
- once you extract the file will run and the directory will add itself to the path
- - this will give you the "monkey \<file path>" command

### Suggestions:
- You can have custom commands run when F5 is pressed, based on the file extention, they can be changed or added in: "assets/compilers/commands.json"
- 

## Commands (..cmd:>)

By pressing ctrl+o the file will be saved and a console will open.

### commands:

- open / . \<file-path>
    - will open the file specified and will move to it's directory
- set \<setting> \<value> / reset / load \<preset>
    - will set the \<setting> to the \<value>
    - will reset to the default settings
    - will load a setting preset from the assets/config/themes folder from the file \<preset>.json if the file exists. 
- exit
    - will bake you a cake