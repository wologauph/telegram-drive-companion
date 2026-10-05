# Telegram Drive 神行管家 · 安装部署入口
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python (Join-Path $ScriptDir "scripts\deploy.py")
