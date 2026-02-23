@echo off
setlocal EnableDelayedExpansion

echo.
echo ================================================
echo   BACKUP + BUILD EXE + GIT COMMIT & PUSH
echo   Remote: https://github.com/vsrepalle/youtube_Feb_23_ver1
echo ================================================
echo.

set "PROJECT_FOLDER=%CD%"
set "BACKUP_PREFIX=YouTubeShortsProject_stable"
set "DATE_STAMP=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%"
set "DATE_STAMP=!DATE_STAMP: =0!"   :: replace space with 0 for hour
set "BACKUP_NAME=%BACKUP_PREFIX%_!DATE_STAMP!"
set "EXE_NAME=ShortsCreator_!DATE_STAMP!.exe"

echo Current project folder: %PROJECT_FOLDER%
echo.

:: 1. Create dated backup copy (exclude temp/output to save space)
echo 1. Creating dated backup folder...
echo    → ..\%BACKUP_NAME%
echo.
xcopy "%PROJECT_FOLDER%" "..\%BACKUP_NAME%" /E /I /H /Y /EXCLUDE:exclude.txt >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Backup created successfully
) else (
    echo [ERROR] Backup failed. Check permissions or disk space.
    pause
    exit /b 1
)

:: 2. Build standalone EXE with PyInstaller (FIXED with hidden imports)
echo.
echo 2. Building new EXE...
pyinstaller --onefile --windowed --name "%EXE_NAME%" ^
    --hidden-import=imageio ^
    --hidden-import=imageio_ffmpeg ^
    --hidden-import=imageio.core ^
    --hidden-import=imageio.plugins ^
    --hidden-import=moviepy ^
    --hidden-import=moviepy.editor ^
    --hidden-import=moviepy.video ^
    --hidden-import=moviepy.audio ^
    --hidden-import=moviepy.video.tools ^
    --hidden-import=moviepy.video.fx ^
    --hidden-import=moviepy.video.tools.subtitles ^
    --hidden-import=moviepy.audio.io ^
    --hidden-import=moviepy.video.io ^
    --hidden-import=moviepy.video.io.ffmpeg_reader ^
    --hidden-import=moviepy.video.io.ffmpeg_writer ^
    --hidden-import=moviepy.audio.io.ffmpeg_audiowriter ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageDraw ^
    --hidden-import=PIL.ImageFont ^
    --hidden-import=pkg_resources ^
    --hidden-import=importlib.metadata ^
    --hidden-import=importlib.resources ^
    --collect-all=imageio ^
    --collect-all=imageio_ffmpeg ^
    --collect-all=moviepy ^
    main.py

if %ERRORLEVEL% equ 0 (
    echo [OK] EXE built: dist\%EXE_NAME%
) else (
    echo [ERROR] PyInstaller failed. Make sure pyinstaller is installed (pip install pyinstaller).
    pause
    exit /b 1
)

:: Copy latest EXE to project root for easy access
copy "dist\%EXE_NAME%" "ShortsCreator_latest.exe" >nul
echo [OK] Latest EXE copied as ShortsCreator_latest.exe

:: 3. Git operations – with your specific remote
echo.
echo 3. Git operations...
echo    Remote: https://github.com/vsrepalle/youtube_Feb_23_ver1

:: Make sure remote is set
git remote | findstr /i "origin" >nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Adding remote origin...
    git remote add origin https://github.com/vsrepalle/youtube_Feb_23_ver1.git
)

git add .
git commit -m "Stable version backup + new EXE build - !DATE_STAMP!"
if %ERRORLEVEL% equ 0 (
    echo [OK] Commit successful
) else (
    echo [INFO] Nothing new to commit or commit skipped
)

echo Pushing to https://github.com/vsrepalle/youtube_Feb_23_ver1 ...
git push origin main
if %ERRORLEVEL% equ 0 (
    echo [OK] Successfully pushed to GitHub
) else (
    echo [ERROR] Push failed.
    echo Possible reasons:
    echo   - No write access (need personal access token or SSH key)
    echo   - Branch name not 'main' (try git push origin master if old repo)
    echo   - Remote not added correctly
    pause
    exit /b 1
)

echo.
echo ================================================
echo               ALL TASKS COMPLETED
echo ================================================
echo.
echo Backup folder:   ..\%BACKUP_NAME%
echo New EXE:         dist\%EXE_NAME%
echo Latest EXE:      ShortsCreator_latest.exe (double-click to run)
echo GitHub:          https://github.com/vsrepalle/youtube_Feb_23_ver1
echo.
pause