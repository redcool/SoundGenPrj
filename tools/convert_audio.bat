@echo off
rem 音频格式批量转换工具（调用 convert_audio.ps1）
rem 用法: convert_audio.bat [输入目录] [源格式] [目标格式] [输出目录] [码率]
rem 示例: convert_audio.bat "D:\Music\260916" m4a mp3
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0convert_audio.ps1" %*
exit /b %ERRORLEVEL%
