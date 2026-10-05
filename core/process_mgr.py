#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 进程管理模块
"""

import os
import sys
import subprocess
import time
from .logger import log, log_error

POSSIBLE_APP_PATHS = [
    r"D:\app\Telegram Drive\app.exe",
    r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\Telegram-Drive-CN.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Telegram Drive\Telegram Drive.exe")
]

def find_installed_app():
    for p in POSSIBLE_APP_PATHS:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def get_running_pids():
    """获取所有运行中的 Telegram Drive 进程 PID"""
    pids = []
    try:
        # 使用 tasklist 快速检测
        out = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode('gbk', errors='ignore')
        
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip(' "') for p in line.split('","')]
            if len(parts) >= 2:
                img_name = parts[0].lower()
                pid = parts[1]
                if img_name in ("app.exe", "telegram drive.exe", "telegram-drive-cn.exe"):
                    try:
                        pids.append(int(pid))
                    except ValueError:
                        pass
    except Exception as e:
        log_error(f"查询运行进程失败: {e}")
    return pids

def is_app_running():
    pids = get_running_pids()
    return len(pids) > 0, pids

def kill_app():
    """终止 Telegram Drive 进程"""
    is_running, pids = is_app_running()
    if not is_running:
        log("Telegram Drive 当前未运行，无需关闭。", "INFO")
        return True

    log(f"正在关闭 Telegram Drive 进程 (PIDs: {pids})...", "INFO")
    for name in ["app.exe", "Telegram Drive.exe", "Telegram-Drive-CN.exe"]:
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

    time.sleep(1.2)
    is_running, remaining = is_app_running()
    if is_running:
        log(f"[WARNING] 仍有残留进程无法结束: {remaining}", "WARNING")
        return False
    else:
        log("[SUCCESS] Telegram Drive 进程已平稳关闭。", "SUCCESS")
        return True

def launch_app(target_exe=None):
    """启动 Telegram Drive"""
    if not target_exe:
        target_exe = find_installed_app()

    if not target_exe or not os.path.exists(target_exe):
        log(f"[ERROR] 无法启动应用，找不到文件: {target_exe}", "ERROR")
        return False

    is_running, pids = is_app_running()
    if is_running:
        log(f"Telegram Drive 已经在运行中 (PID: {pids[0]})", "INFO")
        return True

    log(f"正在启动 Telegram Drive: {target_exe}", "INFO")
    try:
        app_dir = os.path.dirname(target_exe)
        subprocess.Popen(
            [target_exe],
            cwd=app_dir,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        time.sleep(1.5)
        running, pids = is_app_running()
        if running:
            log(f"[SUCCESS] Telegram Drive 启动成功 (PID: {pids})", "SUCCESS")
            return True
        else:
            log("[WARNING] 进程已发起，正在后台加载...", "WARNING")
            return True
    except Exception as e:
        log_error(f"启动应用失败: {e}", e)
        return False
