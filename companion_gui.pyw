#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 神行管家 (Telegram Drive Companion) v5.0
银月独立开发工坊 · 工业级六轨守护与全生命周期助手
"""

import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# 导入核心模块
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.logger import log, log_error, reset_latest_log, LATEST_LOG
from core.process_mgr import is_app_running, kill_app, launch_app, find_installed_app
from core.queue_cleaner import inspect_transfers, clean_stuck_transfers
from core.network_tuner import inspect_network_config, apply_optimal_network
from core.patcher import check_patch_status, run_patch

# 颜色与现代主题配色 (Catppuccin Mocha / Deep Modern Dark)
BG_MAIN = "#1e1e2e"
BG_CARD = "#28293d"
BG_CARD_HOVER = "#31324c"
BORDER_COLOR = "#3c3e5a"
TEXT_PRIMARY = "#cdd6f4"
TEXT_MUTED = "#9399b2"
ACCENT_BLUE = "#89b4fa"
ACCENT_CYAN = "#74c7ec"
SUCCESS_GREEN = "#a6e3a1"
WARNING_YELLOW = "#f9e2af"
DANGER_RED = "#f38ba8"
BUTTON_BG = "#353752"
BUTTON_HOVER = "#45476a"

class TelegramDriveCompanionGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        reset_latest_log("Telegram Drive Companion GUI Session")
        log("Telegram Drive 神行管家启动...", "INFO")

        self.title("Telegram Drive 神行管家 v5.0 · 银月开发工坊")
        self.geometry("820x720")
        self.minsize(760, 680)
        self.configure(bg=BG_MAIN)

        # 尝试设置窗口图标
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self.setup_ui()
        self.refresh_status_async()
        self.start_heartbeat()

    def setup_ui(self):
        # 顶部 Header
        header_frame = tk.Frame(self, bg=BG_MAIN, pady=12, padx=20)
        header_frame.pack(fill="x")

        title_lbl = tk.Label(
            header_frame,
            text="⚡ Telegram Drive 神行管家",
            font=("Microsoft YaHei UI", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_MAIN
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            header_frame,
            text="全量深度汉化 · 彻底切除赞助弹窗 · 1.42GB卡死队列秒救砖 · 30秒保活黄金网络调优",
            font=("Microsoft YaHei UI", 9),
            fg=ACCENT_CYAN,
            bg=BG_MAIN
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # 状态面板 (4 宫格卡片)
        status_container = tk.Frame(self, bg=BG_MAIN, padx=20)
        status_container.pack(fill="x", pady=6)
        status_container.columnconfigure(0, weight=1)
        status_container.columnconfigure(1, weight=1)

        # 卡片 1: 客户端运行状态
        self.card_proc = self.create_status_card(status_container, 0, 0, "💻 客户端运行状态", "检测中...")
        # 卡片 2: 汉化与去赞助
        self.card_patch = self.create_status_card(status_container, 0, 1, "💎 汉化与免弹窗补丁", "检测中...")
        # 卡片 3: 网络与长连接保活
        self.card_net = self.create_status_card(status_container, 1, 0, "⚡ 网络长连接与参数", "检测中...")
        # 卡片 4: 传输队列健康度
        self.card_queue = self.create_status_card(status_container, 1, 1, "🛡️ 传输队列与救砖", "检测中...")

        # 核心功能按钮区
        btn_container = tk.Frame(self, bg=BG_MAIN, padx=20, pady=10)
        btn_container.pack(fill="x")

        # 按钮 1: 一键全量深度汉化与免弹窗
        self.create_action_button(
            btn_container,
            text="💎 一键全量深度汉化与免弹窗 (深度热修复)",
            subtext="自动关闭进程并注入 313 个中文键位与硬编码说明，彻底封杀开机赞助弹窗与横幅",
            accent=ACCENT_BLUE,
            command=self.action_patch_all
        )

        # 按钮 2: 一键清理卡死下载与僵尸队列
        self.create_action_button(
            btn_container,
            text="🧹 一键清理卡死下载与僵尸队列 (彻底救砖)",
            subtext="秒清 transfers.db 中 1.42GB 视频卡死任务与无限重试循环，根治开机下载弹窗",
            accent=SUCCESS_GREEN,
            command=self.action_clean_queue
        )

        # 按钮 3: 一键网络极速调优与长连接保活
        self.create_action_button(
            btn_container,
            text="⚡ 一键网络极速调优与长连接保活 (黄金参数)",
            subtext="对齐 30s 心跳防掐断、单并发上传防限速丢包、4倍超时容限、512KB 分片、关闭自更",
            accent=WARNING_YELLOW,
            command=self.action_tune_network
        )

        # 按钮 4: 启动 / 重启客户端 与 新版本修复 双列布局
        twin_frame = tk.Frame(btn_container, bg=BG_MAIN)
        twin_frame.pack(fill="x", pady=4)
        twin_frame.columnconfigure(0, weight=1)
        twin_frame.columnconfigure(1, weight=1)

        b_launch = tk.Button(
            twin_frame,
            text="🚀 启动 / 平稳重启 Telegram Drive",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#2a3b5c",
            fg=TEXT_PRIMARY,
            activebackground="#3b5280",
            activeforeground="#ffffff",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.action_restart_app
        )
        b_launch.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        b_upgrade = tk.Button(
            twin_frame,
            text="🔄 新版本升级一键热修复",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg="#3b2d54",
            fg=TEXT_PRIMARY,
            activebackground="#543e78",
            activeforeground="#ffffff",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.action_patch_all
        )
        b_upgrade.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # 底部控制区与日志输出
        bottom_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=8)
        bottom_frame.pack(fill="both", expand=True)

        bar_frame = tk.Frame(bottom_frame, bg=BG_MAIN)
        bar_frame.pack(fill="x", pady=(0, 6))

        lbl_log_title = tk.Label(
            bar_frame,
            text="📋 实时操作流水日志 (Auto-Synced)：",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_MAIN
        )
        lbl_log_title.pack(side="left")

        btn_open_log = tk.Button(
            bar_frame,
            text="📂 打开详细日志 (Notepad)",
            font=("Microsoft YaHei UI", 9),
            bg=BUTTON_BG,
            fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER,
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.action_open_log_file
        )
        btn_open_log.pack(side="right")

        btn_explain = tk.Button(
            bar_frame,
            text="📖 参数调优大白话指南",
            font=("Microsoft YaHei UI", 9),
            bg=BUTTON_BG,
            fg=ACCENT_CYAN,
            activebackground=BUTTON_HOVER,
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.action_show_explainer
        )
        btn_explain.pack(side="right", padx=8)

        # 滚动日志文本框
        self.txt_log = tk.Text(
            bottom_frame,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            bd=0,
            font=("Consolas", 9),
            padx=10,
            pady=8,
            wrap="word"
        )
        self.txt_log.pack(fill="both", expand=True)
        self.txt_log.insert("end", "[INFO] 神行管家初始化完成。准备就绪。\n")
        self.txt_log.see("end")

    def create_status_card(self, parent, r, c, title, initial_val):
        frame = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid", padx=12, pady=8)
        frame.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

        t_lbl = tk.Label(
            frame,
            text=title,
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD
        )
        t_lbl.pack(anchor="w")

        v_lbl = tk.Label(
            frame,
            text=initial_val,
            font=("Microsoft YaHei UI", 10),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=340,
            justify="left"
        )
        v_lbl.pack(anchor="w", pady=(3, 0))
        return v_lbl

    def create_action_button(self, parent, text, subtext, accent, command):
        btn_frame = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid", pady=6, padx=12)
        btn_frame.pack(fill="x", pady=4)

        top_row = tk.Frame(btn_frame, bg=BG_CARD)
        top_row.pack(fill="x")

        title_lbl = tk.Label(
            top_row,
            text=text,
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=accent,
            bg=BG_CARD
        )
        title_lbl.pack(side="left")

        act_btn = tk.Button(
            top_row,
            text="立即执行",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_PRIMARY,
            activebackground=BUTTON_HOVER,
            activeforeground="#ffffff",
            bd=0,
            padx=12,
            pady=3,
            cursor="hand2",
            command=command
        )
        act_btn.pack(side="right")

        desc_lbl = tk.Label(
            btn_frame,
            text=subtext,
            font=("Microsoft YaHei UI", 8),
            fg=TEXT_MUTED,
            bg=BG_CARD
        )
        desc_lbl.pack(anchor="w", pady=(2, 0))

    def append_log(self, text, level="INFO"):
        prefix = {
            "SUCCESS": "🟢 [SUCCESS] ",
            "CLEAN": "🧹 [CLEAN] ",
            "WARNING": "⚠️ [WARNING] ",
            "ERROR": "❌ [ERROR] ",
            "INFO": "ℹ️ [INFO] "
        }.get(level, f"[{level}] ")
        
        self.txt_log.insert("end", prefix + text + "\n")
        self.txt_log.see("end")

    # =========================================================================
    # 状态监控与心跳
    # =========================================================================
    def start_heartbeat(self):
        def loop():
            while True:
                time.sleep(3)
                self.after(0, self.refresh_status_async)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def refresh_status_async(self):
        def worker():
            running, pids = is_app_running()
            proc_text = f"🟢 运行中 (PID: {', '.join(map(str, pids))})" if running else "⚪ 未运行 (已停止)"
            proc_color = SUCCESS_GREEN if running else TEXT_MUTED

            app_path = find_installed_app()
            is_patched, patch_msg = check_patch_status(app_path) if app_path else (False, "未安装")
            patch_color = SUCCESS_GREEN if is_patched else WARNING_YELLOW

            net_status = inspect_network_config()
            if net_status["is_golden"]:
                net_text = f"⚡ 30s心跳 · 4倍超时 · 单上传 (SOCKS5 {net_status['proxy_port']})"
                net_color = SUCCESS_GREEN
            else:
                net_text = f"⚠️ 未达黄金状态 (保活:{net_status['keep_alive']}s, 上传:{net_status['max_uploads']})"
                net_color = WARNING_YELLOW

            queue_info = inspect_transfers()
            if queue_info["jobs_count"] == 0:
                queue_text = "🛡️ 队列纯净健康 (0 活跃卡死任务)"
                queue_color = SUCCESS_GREEN
            elif queue_info["jobs_count"] > 0:
                queue_text = f"⚠️ 发现 {queue_info['jobs_count']} 个任务在列 (含可能卡死)"
                queue_color = DANGER_RED
            else:
                queue_text = "❓ 状态未就绪"
                queue_color = TEXT_MUTED

            def update_ui():
                self.card_proc.config(text=proc_text, fg=proc_color)
                self.card_patch.config(text=patch_msg, fg=patch_color)
                self.card_net.config(text=net_text, fg=net_color)
                self.card_queue.config(text=queue_text, fg=queue_color)

            self.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================================
    # 核心动作响应
    # =========================================================================
    def action_patch_all(self):
        def worker():
            self.append_log("正在执行全量深度汉化与免弹窗补丁注入...", "INFO")
            app_path = find_installed_app()
            if not app_path:
                self.append_log("未找到 Telegram Drive 安装路径！", "ERROR")
                messagebox.showerror("错误", "未找到 Telegram Drive 安装文件！")
                return

            self.append_log("1. 正在平稳终止运行中的客户端...", "INFO")
            kill_app()
            time.sleep(1)

            self.append_log("2. 正在无损注入 7 大核心切片...", "INFO")
            try:
                ok = run_patch(target_app_path=app_path)
                if ok:
                    self.append_log("补丁注入与配置对齐 100% 成功！", "SUCCESS")
                    self.append_log("WebView2 缓存已清空，赞助弹窗已彻底切除！", "CLEAN")
                    self.refresh_status_async()
                    messagebox.showinfo("完成", "全量深度汉化与免弹窗补丁注入成功！\n\n已切除启动赞助弹窗，已汉化所有硬编码说明！")
                else:
                    self.append_log("补丁注入遇到异常！", "ERROR")
                    messagebox.showerror("失败", "补丁注入未完全成功，请查看详细日志。")
            except Exception as e:
                log_error(f"补丁过程崩溃: {e}", e)
                self.append_log(f"补丁失败: {e}", "ERROR")
                messagebox.showerror("错误", f"补丁失败: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def action_clean_queue(self):
        def worker():
            self.append_log("正在检测并清理卡死下载队列...", "INFO")
            running, _ = is_app_running()
            if running:
                self.append_log("提示：为彻底清除 SQLite 锁，正在暂时平稳重启客户端...", "INFO")
                kill_app()
                time.sleep(1)

            ok, count, msg = clean_stuck_transfers(force_all=True)
            if ok:
                self.append_log(f"队列救砖成功：{msg}", "SUCCESS")
                self.refresh_status_async()
                messagebox.showinfo("队列清理完成", f"已成功清除 {count} 个卡死/未完成的任务！\n\n以后启动应用将绝不再弹出 1.42GB 视频下载窗口！")
            else:
                self.append_log(f"队列清理失败: {msg}", "ERROR")
                messagebox.showerror("错误", f"清理失败: {msg}")

        threading.Thread(target=worker, daemon=True).start()

    def action_tune_network(self):
        def worker():
            self.append_log("正在调优黄金网络参数与长连接保活...", "INFO")
            ok, msg = apply_optimal_network()
            if ok:
                self.append_log(msg, "SUCCESS")
                self.refresh_status_async()
                messagebox.showinfo("网络调优完成", "黄金网络参数已成功写入！\n\n• 长连接保活心跳：30 秒 (防掐断)\n• 上传并发数：1 (单通道独占稳定)\n• 请求超时倍率：4 倍\n• 自动重试次数：5 次\n• 分片大小：512 KB\n• 性能模式：已开启\n• 自动更新：已关闭 (防覆盖补丁)")
            else:
                self.append_log(f"网络调优失败: {msg}", "ERROR")
                messagebox.showerror("错误", f"调优失败: {msg}")

        threading.Thread(target=worker, daemon=True).start()

    def action_restart_app(self):
        def worker():
            self.append_log("正在平稳重启 Telegram Drive...", "INFO")
            kill_app()
            time.sleep(1.2)
            app_path = find_installed_app()
            ok = launch_app(app_path)
            if ok:
                self.append_log("Telegram Drive 已成功启动！", "SUCCESS")
                self.refresh_status_async()
            else:
                self.append_log("启动客户端失败！", "ERROR")

        threading.Thread(target=worker, daemon=True).start()

    def action_open_log_file(self):
        try:
            if not os.path.exists(LATEST_LOG):
                with open(LATEST_LOG, "w", encoding="utf-8") as f:
                    f.write("Telegram Drive Companion Log\n")
            subprocess.Popen(["notepad.exe", LATEST_LOG])
            self.append_log("已为您在记事本中打开详细运行日志。", "INFO")
        except Exception as e:
            self.append_log(f"打开日志失败: {e}", "ERROR")

    def action_show_explainer(self):
        top = tk.Toplevel(self)
        top.title("📖 Telegram Drive 核心参数与黄金调优深度解析")
        top.geometry("640x520")
        top.configure(bg=BG_MAIN)
        top.transient(self)

        txt = tk.Text(
            top,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10),
            padx=16,
            pady=16,
            wrap="word",
            bd=0
        )
        txt.pack(fill="both", expand=True, padx=12, pady=12)

        content = """【为什么这样调？黄金参数大白话深度剖析】

1. 为什么设置 30 秒心跳保活 (Keep-Alive Interval = 30s)？
   Telegram 官方服务器对翻墙代理的闲置连接极其敏感。国内翻墙连接大文件时，只要稍微有几秒钟没有数据往来，代理节点或 Telegram 网关就会静默掐断连接（Socket Drop）。设为 30 秒心跳后，软件每 30 秒向电报发一次轻量 Ping，保持通道始终处于活跃状态，杜绝网络假死断流！

2. 为什么将最大上传并发设为 1 (Max Concurrent Uploads = 1)？
   很多主人误以为并发数越高越好，但 Telegram 官方针对中国大陆 IP 和代理有非常严苛的防刷机制（FLOOD_WAIT）。当 2 个或 3 个大视频同时上传时，多个连接会互相抢占代理带宽，导致极高概率触发丢包或电报服务端主动中断连接！
   调为 1（单任务逐个上传）是大文件稳定传输的黄金准则，速度最平稳、绝不丢包断流！

3. 为什么分片大小调为 512 KB (Chunk Size = 512 KB)？
   这是契合 Telegram MTProto 底层传输协议的最佳尺寸。如果分片设为 1MB 或更大，遇到网络稍有抖动就要重传整个 1MB；若设为 128KB，又会有太高频的握手延迟。512KB 是兼顾抗抖动与满速吞吐的最优平衡点。

4. 为什么请求超时设为 4 倍 (Timeout Multiplier = 4)？
   默认 1 倍超时往往只有十几秒，只要代理节点出现瞬间波动，软件就会立即判死判定为失败。调为 4 倍后，软件会给网络长达一两分钟的宽限期，即使网络卡顿也会耐心等待数据回包。

5. 为什么失败重试设为 5 次 (Retry Attempts = 5)？
   遇到偶尔的闪断，软件会在后台自动进行 5 次指数退避重试，直接自愈恢复，绝不再需要您手动重新点上传！

6. 为什么关闭自动更新 (Auto-Update = False)？
   官方一旦自动静默升级，就会用未汉化的官方英文原版直接覆盖掉我们的汉化执行体，导致弹窗和英文复发。关闭后，日常使用安稳省心；需要升级时，直接在管家里点一次升级热修复即可！
"""
        txt.insert("end", content)
        txt.config(state="disabled")

def main():
    app = TelegramDriveCompanionGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
