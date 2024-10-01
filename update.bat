set source=".\assets\config\default_settings.json"
set destination=".\assets\config\settings.json"

echo Copying settings file...
copy %source% %destination%

xcopy "./assets" "dist/assets" /E /I /Y
xcopy "./dist" "%userprofile%/custom-tools/monkeyeditor" /E /I /Y

mkdir ".\distribution"

if errorlevel 1 (
    echo Failed to copy the file.
) else (
    echo File copied successfully.
)

setlocal

rem Set the source directory and the destination ZIP file
set "source_dir=.\dist"
set "destination_zip=.\distribution\Monkey Editor.zip"

rem Compress the directory to a ZIP file
powershell -command "Compress-Archive -Update -Path '%source_dir%\*' -DestinationPath '%destination_zip%'"

echo Directory compressed to %destination_zip%
endlocal