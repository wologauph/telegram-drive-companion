#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 神行管家 · 全链路工业级日志模块
"""

import os
import sys
import datetime
import traceback

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LATEST_LOG = os.path.join(LOGS_DIR, "latest_run.log")
ERROR_LOG = os.path.join(LOGS_DIR, "error.log")

def get_monthly_log():
    month_str = datetime.datetime.now().strftime("%Y-%m")
    return os.path.join(LOGS_DIR, f"app_{month_str}.log")

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {msg}"
    print(formatted)
    
    # 写入 latest_run.log (追加)
    try:
        with open(LATEST_LOG, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

    # 写入月度日志
    try:
        with open(get_monthly_log(), "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

    # 若为错误则写入 error.log
    if level == "ERROR":
        try:
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception:
            pass

def log_error(err_msg, exc=None):
    if exc:
        tb = traceback.format_exc()
        log(f"{err_msg} | 异常堆栈: {tb}", level="ERROR")
    else:
        log(err_msg, level="ERROR")

def reset_latest_log(session_title="Telegram Drive Companion Session"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"=================================================================\n" \
             f" {session_title} - {timestamp}\n" \
             f" 银月独立开发工坊 · Telegram Drive 工业级神行管家\n" \
             f"=================================================================\n"
    try:
        with open(LATEST_LOG, "w", encoding="utf-8") as f:
            f.write(header)
    except Exception:
        pass
