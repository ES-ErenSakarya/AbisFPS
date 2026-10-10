@echo off
chcp 65001 > nul
cd /d "%~dp0"
start /b python launcher.py
exit