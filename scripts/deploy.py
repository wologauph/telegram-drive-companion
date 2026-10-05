#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 神行管家 · 自动化部署与快捷方式创建
"""

import os
import shutil
import win32com.client

WORKSHOP_DIR = r"D:\银月独立开发工坊\telegram-drive-companion"
TOOL_LIB_DIR = r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN"
COMPANION_DEST = os.path.join(TOOL_LIB_DIR, "companion")

def deploy():
    print(">>> [1/3] 同步文件至工具库...")
    os.makedirs(COMPANION_DEST, exist_ok=True)

    # 复制文件
    for f in ["companion_gui.pyw", "run.bat"]:
        src = os.path.join(WORKSHOP_DIR, f)
        dst = os.path.join(COMPANION_DEST, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  已复制: {f}")

    for folder in ["core", "config"]:
        src_folder = os.path.join(WORKSHOP_DIR, folder)
        dst_folder = os.path.join(COMPANION_DEST, folder)
        if os.path.exists(src_folder):
            if os.path.exists(dst_folder):
                shutil.rmtree(dst_folder)
            shutil.copytree(src_folder, dst_folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"  已复制模块: {folder}")

    # 创建根目录启动脚本
    root_launcher = os.path.join(TOOL_LIB_DIR, "Telegram-Drive-神行管家.bat")
    with open(root_launcher, "w", encoding="utf-8") as f:
        f.write('@echo off\nchcp 65001 >nul\nstart "" pythonw.exe "%~dp0companion\\companion_gui.pyw"\nexit\n')
    print(f"  已生成启动脚本: {root_launcher}")

    print(">>> [2/3] 创建桌面快捷方式...")
    desktop_short = r"C:\Users\1\Desktop\常用电~1"
    if os.path.exists(desktop_short):
        shell = win32com.client.Dispatch("WScript.Shell")
        lnk_path = os.path.join(desktop_short, "Telegram Drive 神行管家.lnk")
        shortcut = shell.CreateShortcut(lnk_path)
        shortcut.TargetPath = "pythonw.exe"
        shortcut.Arguments = f'"{os.path.join(COMPANION_DEST, "companion_gui.pyw")}"'
        shortcut.WorkingDirectory = COMPANION_DEST
        shortcut.Description = "Telegram Drive 全景汉化、免弹窗与网络保活神行管家"
        # 尝试使用 Telegram Drive 图标
        icon_source = r"D:\app\Telegram Drive\app.exe"
        if os.path.exists(icon_source):
            shortcut.IconLocation = f"{icon_source},0"
        shortcut.Save()
        print(f"  [SUCCESS] 桌面快捷方式已建立: {lnk_path}")

    print(">>> [3/3] 部署完成！")

if __name__ == "__main__":
    deploy()
