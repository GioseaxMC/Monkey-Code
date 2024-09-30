pyinstaller main.py --onefile --icon="assets/icon.ico" --name="monkey"
xcopy "./assets" "dist/assets" /E /I /Y
xcopy "./dist" "%userprofile%/custom-tools/monkeyeditor" /E /I /Y

mkdir ".\distribution"
setlocal

rem Set the source directory and the destination ZIP file
set "source_dir=.\dist"
set "destination_zip=.\distribution\Monkey Editor.zip"

rem Compress the directory to a ZIP file
powershell -command "Compress-Archive -Path '%source_dir%\*' -DestinationPath '%destination_zip%'"

echo Directory compressed to %destination_zip%
endlocal