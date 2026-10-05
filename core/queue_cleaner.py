#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 传输队列清理与救砖模块 (Queue Cleaner)
彻底根治卡死下载、1.42GB 无限弹窗、无法关闭重试的顽疾
"""

import os
import sqlite3
import shutil
import time
from .logger import log, log_error

DB_PATH = os.path.expandvars(r"%APPDATA%\com.cameronamer.telegramdrive\transfers.db")

def get_db_path():
    return DB_PATH

def inspect_transfers():
    """检测当前传输数据库状态"""
    if not os.path.exists(DB_PATH):
        return {
            "exists": False,
            "jobs_count": 0,
            "tombstones_count": 0,
            "jobs": []
        }

    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        c = conn.cursor()
        
        # 检查表是否存在
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transfer_jobs'")
        has_jobs_table = c.fetchone() is not None
        
        if not has_jobs_table:
            conn.close()
            return {"exists": True, "jobs_count": 0, "tombstones_count": 0, "jobs": []}

        c.execute("SELECT id, direction, status, payload_json FROM transfer_jobs")
        raw_jobs = c.fetchall()
        jobs = []
        for r in raw_jobs:
            jid, jdir, jstatus, jpayload = r
            save_path = ""
            total_bytes = 0
            if jpayload:
                try:
                    p = json.loads(jpayload)
                    save_path = p.get("savePath") or p.get("local_path") or ""
                    total_bytes = p.get("file_size") or p.get("total_bytes") or 0
                except Exception:
                    pass
            jobs.append({
                "id": jid,
                "direction": jdir,
                "status": jstatus,
                "path": save_path,
                "total_bytes": total_bytes
            })

        c.execute("SELECT count(*) FROM transfer_tombstones")
        tombstones_count = c.fetchone()[0]
        conn.close()

        return {
            "exists": True,
            "jobs_count": len(jobs),
            "tombstones_count": tombstones_count,
            "jobs": jobs
        }
    except Exception as e:
        log_error(f"检测 transfers.db 失败: {e}")
        return {
            "exists": True,
            "jobs_count": -1,
            "tombstones_count": -1,
            "error": str(e),
            "jobs": []
        }

def clean_stuck_transfers(force_all=True):
    """
    一键清理卡死下载与僵尸任务：
    1. 备份 transfers.db -> transfers.db.bak
    2. 将 transfer_jobs 任务转入 transfer_tombstones (标记已取消)
    3. 清空 transfer_jobs 表
    4. 压缩整理数据库
    """
    if not os.path.exists(DB_PATH):
        log("未检测到 transfers.db 文件，队列已是纯净状态。", "INFO")
        return True, 0, "数据库不存在，队列纯净。"

    # 备份数据库
    bak_path = DB_PATH + ".bak"
    try:
        shutil.copy2(DB_PATH, bak_path)
        log(f"已备份 transfers.db 至: {bak_path}", "INFO")
    except Exception as e:
        log_error(f"备份数据库失败: {e}")

    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        c = conn.cursor()

        c.execute("SELECT id, direction, status, payload_json FROM transfer_jobs")
        stuck_jobs = c.fetchall()
        count = len(stuck_jobs)

        if count == 0:
            conn.close()
            log("[SUCCESS] 当前传输队列中无任何卡死任务，队列状态完美健康！", "SUCCESS")
            return True, 0, "当前无卡死任务，队列纯净健康。"

        for job in stuck_jobs:
            jid = job[0]
            jdir = job[1]
            jpayload = job[3]
            save_path = ""
            total_bytes = 0
            if jpayload:
                try:
                    p = json.loads(jpayload)
                    save_path = p.get("savePath") or ""
                    total_bytes = p.get("file_size") or 0
                except Exception:
                    pass
            size_mb = f"{total_bytes / (1024*1024):.2f} MB" if total_bytes else "未知大小"
            log(f"[CLEAN] 正在清理卡死任务: ID={jid}, 方向={jdir}, 路径={save_path}, 大小={size_mb}", "CLEAN")
            
            # 插入墓碑表防止电报客户端反复重试唤醒
            try:
                c.execute("INSERT OR IGNORE INTO transfer_tombstones (id) VALUES (?)", (jid,))
            except Exception:
                pass

        # 彻底清空 active 任务表
        c.execute("DELETE FROM transfer_jobs")
        conn.commit()
        
        # 执行整理
        try:
            c.execute("VACUUM")
        except Exception:
            pass

        conn.close()
        log(f"[SUCCESS] 成功清理 {count} 个卡死传输任务，已解除开机弹窗与无限重试锁定！", "SUCCESS")
        return True, count, f"成功清除 {count} 个卡死任务！"
    except Exception as e:
        log_error(f"清理传输队列失败: {e}", e)
        return False, 0, f"清理失败: {e}"
