#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 目录同步实时监测后台模块 (Sync Live Monitor)
银月独立开发工坊 · 工业级多维同步进度、实时网速与剩余时间计算引擎
"""

import os
import time
import sqlite3
import psutil
from .logger import log, log_error
from .process_mgr import is_app_running

SHARES_DB = os.path.expandvars(r"%APPDATA%\com.cameronamer.telegramdrive\shares.db")

class SyncMonitor:
    def __init__(self):
        self.last_check_time = time.time()
        self.last_io_read = 0
        self.last_io_write = 0
        self.current_speed_bps = 0.0
        self._last_pid = None

    def get_sync_pairs(self):
        """获取所有已配置的同步映射对"""
        if not os.path.exists(SHARES_DB):
            return []

        pairs = []
        try:
            conn = sqlite3.connect(SHARES_DB, timeout=3.0)
            c = conn.cursor()
            c.execute("""
                SELECT id, local_path, channel_id, label, sync_direction, is_active, created_at
                FROM sync_pairs
            """)
            for row in c.fetchall():
                # 去除 Windows 扩展路径前缀 \\?\
                raw_path = row[1] or ""
                clean_path = raw_path.replace(r"\\?\/", "").replace(r"\\?\\", "")
                pairs.append({
                    "id": row[0],
                    "local_path": clean_path,
                    "channel_id": row[2],
                    "label": row[3] or "未命名频道",
                    "direction": row[4] or "two_way",
                    "is_active": bool(row[5]),
                    "created_at": row[6]
                })
            conn.close()
        except Exception as e:
            log_error(f"读取 sync_pairs 失败: {e}")
        return pairs

    def is_sync_enabled(self):
        """检测目录同步总开关是否开启"""
        if not os.path.exists(SHARES_DB):
            return False
        try:
            conn = sqlite3.connect(SHARES_DB, timeout=3.0)
            c = conn.cursor()
            c.execute("SELECT value FROM sync_settings WHERE key = 'sync_enabled'")
            row = c.fetchone()
            conn.close()
            return row is not None and row[0].lower() == "true"
        except Exception:
            return False

    def get_recent_logs(self, limit=20):
        """获取最近同步历史流水"""
        if not os.path.exists(SHARES_DB):
            return []
        logs = []
        try:
            conn = sqlite3.connect(SHARES_DB, timeout=3.0)
            c = conn.cursor()
            c.execute("""
                SELECT id, pair_id, action, relative_path, detail, datetime(created_at, 'unixepoch', 'localtime')
                FROM sync_log
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            for r in c.fetchall():
                logs.append({
                    "id": r[0],
                    "pair_id": r[1],
                    "action": r[2],
                    "path": r[3] or "",
                    "detail": r[4] or "",
                    "time": r[5] or ""
                })
            conn.close()
        except Exception as e:
            log_error(f"读取 sync_log 失败: {e}")
        return logs

    def update_speed(self):
        """计算客户端进程当前的实时读写/网络 I/O 速度"""
        now = time.time()
        dt = now - self.last_check_time
        if dt <= 0.2:
            return self.current_speed_bps

        running, pids = is_app_running()
        if not running or not pids:
            self.current_speed_bps = 0.0
            self.last_check_time = now
            return 0.0

        pid = pids[0]
        try:
            proc = psutil.Process(pid)
            io = proc.io_counters()
            current_bytes = io.read_bytes + io.write_bytes

            if self._last_pid != pid:
                self._last_pid = pid
                self.last_io_read = io.read_bytes
                self.last_io_write = io.write_bytes
                self.current_speed_bps = 0.0
            else:
                total_delta = current_bytes - (self.last_io_read + self.last_io_write)
                self.current_speed_bps = max(0.0, total_delta / dt)
                self.last_io_read = io.read_bytes
                self.last_io_write = io.write_bytes

            self.last_check_time = now
        except Exception:
            self.current_speed_bps = 0.0

        return self.current_speed_bps

    def get_progress_snapshot(self):
        """
        获取当前同步进度的全景快照：
        - 激活的同步对与本地文件夹
        - 本地文件总数与总体积
        - 数据库已同步文件数与体积
        - 正在活动的临时传输文件
        - 实时速度与预计剩余时间 (ETA)
        """
        enabled = self.is_sync_enabled()
        pairs = self.get_sync_pairs()
        speed_bps = self.update_speed()

        if not pairs:
            return {
                "enabled": enabled,
                "has_pair": False,
                "status_text": "未配置同步目录",
                "total_files": 0,
                "synced_files": 0,
                "total_bytes": 0,
                "synced_bytes": 0,
                "remaining_bytes": 0,
                "percent": 0.0,
                "speed_bps": speed_bps,
                "speed_text": "0 KB/s",
                "eta_text": "--",
                "active_file": "无活动任务",
                "recent_logs": self.get_recent_logs(10)
            }

        active_pair = pairs[0]  # 当前主同步对
        local_dir = active_pair["local_path"]

        # 扫描本地文件列表
        local_files = []
        total_bytes = 0
        active_tmp_file = None

        if os.path.exists(local_dir):
            try:
                for root, dirs, files in os.walk(local_dir):
                    # 忽略临时文件和系统隐藏项
                    for f in files:
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, local_dir).replace("\\", "/")
                        if f.endswith(".td-sync-tmp"):
                            active_tmp_file = f.replace(".td-sync-tmp", "")
                            continue
                        if f in (".DS_Store", "desktop.ini", "Thumbs.db"):
                            continue
                        try:
                            sz = os.path.getsize(full_p)
                        except Exception:
                            sz = 0
                        local_files.append((rel_p, sz))
                        total_bytes += sz
            except Exception as e:
                log_error(f"扫描本地同步目录失败: {e}")

        # 查询数据库已记录的同步状态
        synced_count = 0
        synced_bytes = 0
        synced_paths = set()

        if os.path.exists(SHARES_DB):
            try:
                conn = sqlite3.connect(SHARES_DB, timeout=3.0)
                c = conn.cursor()
                c.execute("""
                    SELECT relative_path, file_size
                    FROM sync_state
                    WHERE pair_id = ? AND sync_status = 'synced'
                """, (active_pair["id"],))
                for r in c.fetchall():
                    synced_paths.add(r[0])
                    synced_count += 1
                    synced_bytes += (r[1] or 0)
                conn.close()
            except Exception:
                pass

        total_files = len(local_files)
        # 如果 sync_state 记录为空，但 sync_log 有完成记录，按 sync_log 估算
        if synced_count == 0 and total_files > 0:
            recent_logs = self.get_recent_logs(100)
            success_uploads = {l["path"] for l in recent_logs if l["action"] == "upload" and "success" in l["detail"].lower()}
            synced_count = len(success_uploads)
            for rel_p, sz in local_files:
                if rel_p in success_uploads:
                    synced_bytes += sz

        remaining_bytes = max(0, total_bytes - synced_bytes)
        percent = (synced_bytes / total_bytes * 100.0) if total_bytes > 0 else 0.0

        # 计算 ETA 预计剩余时间
        if speed_bps > 1024 and remaining_bytes > 0:
            secs = int(remaining_bytes / speed_bps)
            if secs < 60:
                eta_text = f"{secs} 秒"
            elif secs < 3600:
                eta_text = f"{secs // 60} 分 {secs % 60} 秒"
            else:
                eta_text = f"{secs // 3600} 小时 {(secs % 3600) // 60} 分"
        else:
            eta_text = "--"

        # 格式化网速
        if speed_bps >= 1024 * 1024:
            speed_text = f"{speed_bps / (1024 * 1024):.2f} MB/s"
        elif speed_bps >= 1024:
            speed_text = f"{speed_bps / 1024:.1f} KB/s"
        else:
            speed_text = "0 KB/s"

        # 活动文件判定
        if active_tmp_file:
            active_file = f"[下载中] {active_tmp_file}"
        else:
            # 找到下一个待同步的文件
            pending = [f[0] for f in local_files if f[0] not in synced_paths]
            if pending:
                active_file = f"[同步队列] {os.path.basename(pending[0])}"
            else:
                active_file = "所有文件已同步就绪"

        running, _ = is_app_running()
        if not running:
            status_text = "⚪ 客户端已停止"
        elif not enabled:
            status_text = "⏸️ 目录同步已停用"
        elif speed_bps > 50000:
            status_text = "🟢 正在高速同步传输中..."
        else:
            status_text = "🟢 正在监听变更 (待命中)"

        return {
            "enabled": enabled,
            "has_pair": True,
            "pair": active_pair,
            "status_text": status_text,
            "total_files": total_files,
            "synced_files": synced_count,
            "total_bytes": total_bytes,
            "synced_bytes": synced_bytes,
            "remaining_bytes": remaining_bytes,
            "percent": percent,
            "speed_bps": speed_bps,
            "speed_text": speed_text,
            "eta_text": eta_text,
            "active_file": active_file,
            "recent_logs": self.get_recent_logs(15)
        }

# 全局单例
sync_monitor = SyncMonitor()
