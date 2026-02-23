@echo off
echo ============================================
echo     GIT PUSH TO NEW REMOTE REPOSITORY
echo ============================================

REM ====== SET YOUR PROJECT DIRECTORY ======
cd /d C:\PATH\TO\YOUR\PROJECT

echo.
echo Current Directory:
cd
echo.

REM ====== CHECK IF GIT IS INITIALIZED ======
if not exist ".git" (
    echo Initializing Git Repository...
    git init
)

echo.
echo Adding all files...
git add .

echo.
echo Creating commit...
git commit -m "Initial commit - Feb 23 Version 1"

echo.
echo Removing old remote (if exists)...
git remote remove origin 2>nul

echo.
echo Adding new remote...
git remote add origin https://github.com/vsrepalle/youtube_Feb_23_ver1.git

echo.
echo Setting main branch...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ============================================
echo            PUSH COMPLETE
echo ============================================

pause