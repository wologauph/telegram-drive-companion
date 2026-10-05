@echo off
chcp 65001 >nul
title Telegram Drive 神行管家
start "" pythonw.exe "%~dp0companion_gui.pyw"
exit
