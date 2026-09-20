@echo off
setlocal
cd /d "%~dp0"
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=%~dp0"
REM If a dragged file (not folder), use its directory
if exist "%TARGET%\*" ( set "DIR2=%TARGET%" ) else ( set "DIR2=%~dp1" )
if "%DIR2%"=="" set "DIR2=%TARGET%"
echo ============================================
echo  ABC -^> HTML one-page sheet (abcjs v6)
echo  Scan folder: "%DIR2%"
echo  Usage: double-click here (scans this folder)
echo         or drop a folder / .abc files onto this bat
echo ============================================
set N=0
for %%f in ("%DIR2%\*.abc") do (
  set /a N+=1
  echo  [%%f]
  node "%~dp0render_sheet.mjs" "%%f" "%%~dpnf.html" "%%~nf"
  if errorlevel 1 echo    FAILED: %%f
)
echo.
echo  Done: %N% abc file(s). Open the .html in a browser.
pause
