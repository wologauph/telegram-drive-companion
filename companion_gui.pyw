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
from core.sync_monitor import sync_monitor

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

        # 按钮 4: 目录同步实时监测后台
        self.create_action_button(
            btn_container,
            text="📡 目录同步实时监测后台 (进度/网速/ETA看板)",
            subtext="实时显示目录同步百分比、瞬时网速 (MB/s)、预计剩余时间、正在处理文件与历史流水",
            accent=ACCENT_CYAN,
            command=self.action_show_sync_monitor
        )

        # 按钮 5: 启动 / 重启客户端 与 新版本修复 双列布局
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
            sync_snap = sync_monitor.get_progress_snapshot()

            if queue_info["jobs_count"] == 0:
                if sync_snap["has_pair"] and sync_snap["speed_bps"] > 1024:
                    queue_text = f"🛡️ 纯净 | 📡 同步中: {sync_snap['speed_text']} ({sync_snap['percent']:.1f}%)"
                    queue_color = SUCCESS_GREEN
                elif sync_snap["has_pair"] and sync_snap["enabled"]:
                    queue_text = f"🛡️ 纯净 | 📡 同步待命 ({sync_snap['synced_files']}/{sync_snap['total_files']} 文件)"
                    queue_color = SUCCESS_GREEN
                else:
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

            self.append_log("2. 正在无损注入核心切片 (含设置弹窗与保护机制说明)...", "INFO")
            try:
                ok = run_patch(target_app_path=app_path)
                if ok:
                    self.append_log("补丁注入与配置对齐 100% 成功！", "SUCCESS")
                    self.append_log("WebView2 缓存已清空，赞助弹窗已彻底切除！", "CLEAN")
                    self.refresh_status_async()
                    messagebox.showinfo("完成", "全量深度汉化与免弹窗补丁注入成功！\n\n已切除启动赞助弹窗，所有说明弹窗与按钮已全部汉化！")
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

    def action_show_sync_monitor(self):
        SyncMonitorWindow(self)

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
        top.title("📖 Telegram Drive 核心参数与官方报告深度解析")
        top.geometry("740x620")
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

        content = """【Telegram Drive 核心网络与设置官方权威解析】

一、网络优化与长连接核心参数
1. 重试退避间隔 (Retry Base Backoff) 与最大退避等待 (Retry Max Backoff)：
   • 原理：当网络请求遇到错误时，客户端采用指数退避机制（Exponential Backoff with Jitter）来避免重试风暴。
   • 建议调整：基础退避设为 1000ms (1秒)，最大退避设为 30000ms (30秒) 至 60000ms (60秒)。遇到偶发网络闪断时，软件会从1秒、2秒、4秒逐步拉长等待，既不会在网络波动瞬间频繁重试造成雪崩，也能在断网恢复后自愈，完全可以设得比较长！

2. Telegram 数据中心选择 (Preferred DC - 自动 vs 指定 DC)：
   • 官方源码真相：每个 Telegram 账户在注册时，其核心数据（User Entity、会话、消息）就永久绑定了固定的 Home DC（中国大陆手机号注册通常分配在 DC4 荷兰或 DC5 新加坡）。
   • 强烈建议：必须选择【auto (自动)】！如果强行指定其他 DC（如 DC1 迈阿密），电报服务器会返回 MIGRATE_DC 错误，或者在底层通过跨国骨干网跨机房转发，不仅不会加速，反而严重增加握手延迟与断流风险！

3. 数据中心切换重试次数 (DC Fallback Attempts)：
   • 默认 2~4 次。当连接主数据中心失败时，客户端尝试自动切换备选路由的重试次数。保持 2~4 次即可。

4. 遵循官方限频等待 (Flood Wait Respect)：
   • 为什么必须开启？电报官方对 API 频率有极其严苛的限流保护（FLOOD_WAIT_X）。如果开启，遇到限流时程序会乖乖休眠 X 秒后自动重试；如果关闭并强行高并发请求，电报官方防火墙会判定为恶意自动化攻击，极易导致账号被封禁（Banned）或长期禁言！

5. 传输带宽上限 (Bandwidth Limit) 与切片大小 (Chunk Size)：
   • 带宽上限设为 0 (不限速) 最佳，独占利用您的代理全部速度。
   • 切片大小 512 KB 最佳：契合 MTProto 底层传输的最佳 MTU 规格，兼顾吞吐量与抗抖动。

6. 长时连接保活心跳 (Keep-Alive Interval: 15s / 30s / 120s / 关闭)：
   • 官方实现：代码每隔设定秒数在后台向 api.telegram.org:443 发送轻量 TCP 连接探测，用于维持翻墙代理路由活跃。
   • 15 秒最好吗？如果您使用的翻墙节点或本地 Clash 客户端闲置规则非常激进（比如闲置 15~20秒就掐断 TCP），那么设为 15秒 是最稳妥激进的防掐断选择；国际标准通常 30秒 是兼顾低握手开销与保活的最佳平衡点。在经常中断的网络环境下，设为 15 秒完全没问题！

二、本地接口与批量打包
7. 批量打包内存上限 (Bulk Archive Max Memory - 默认 256 MiB)：
   • 源码真相：这是当通过 REST API 批量调用 /files/bulk 将多个文件打包为 .zip 下载流时，在内存中构建流媒体切片所允许占用的最大内存空间。若文件超出此限制，API 会拒绝打包，防止内存溢出导致程序崩溃。

8. REST API 本地接口有什么用？它有密钥：
   • 用途：允许本地第三方脚本、自动化程序（例如 Python/Node.js 或银月）通过 HTTP 接口全自动化管理电报网盘！支持自动化列出、搜索、上传、下载、删除文件及统计存储。
   • 密钥安全：密钥仅保存在本机内存并监听在 127.0.0.1 本地回环，不接入外网，非常安全。

三、上传与视频模式
9. 上传前压缩文件夹 (Zip folders before upload)：
   • 官方源码真相 (fs.rs / useFileUpload.ts)：由于 Telegram 原生没有“文件夹消息”概念，如果关闭此项，当您手动点击“上传文件夹”时，界面会直接弹窗报错拒绝上传！因此如果想手动上传整个文件夹，必须开启此项，它会自动打成单个 .zip。
   • 补充：如果是【目录自动同步 (Folder Sync)】，则不受此限制，同步引擎会自动遍历内部所有单文件分别上传。

10. 默认视频上传方式（文件模式 File vs 媒体模式 Media）：
   • 官方源码真相 (fs.rs 第 127~210 行)：
     ① 画质与完整性：无论选哪种模式，上传的文件字节流 100% 原汁原味原盘上传，绝不重新编码、绝不压缩画质！
     ② 区别在于是否附加 Attribute::Video：
        - 文件模式 (File)：作为普通文件（Document）上传，无法在线流播，客户端必须下载完整文件后才能观看。
        - 媒体模式 (Media)：上传前本地读取时长与分辨率，附加在线播放属性。在电报手机端与电脑端支持直接在线点播、带缩略图预览、显示视频时长！
        - 注意：媒体模式要求视频必须是 MP4/MOV 且头部完好；若格式不兼容可切换回文件模式。
"""
        txt.insert("end", content)
        txt.config(state="disabled")

class SyncMonitorWindow(tk.Toplevel):
    """目录同步实时监测独立后台窗口"""
    def __init__(self, master):
        super().__init__(master)
        self.title("📡 Telegram Drive 目录同步实时监测后台 · 银月工坊")
        self.geometry("760x600")
        self.minsize(700, 520)
        self.configure(bg=BG_MAIN)

        self.is_topmost = False
        self.setup_ui()
        self.refresh_loop()

    def setup_ui(self):
        # 顶部 Bar
        top_bar = tk.Frame(self, bg=BG_MAIN, padx=16, pady=10)
        top_bar.pack(fill="x")

        t_lbl = tk.Label(
            top_bar,
            text="📡 目录同步实时监测后台",
            font=("Microsoft YaHei UI", 14, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_MAIN
        )
        t_lbl.pack(side="left")

        self.btn_pin = tk.Button(
            top_bar,
            text="📌 窗口置顶",
            font=("Microsoft YaHei UI", 9),
            bg=BUTTON_BG,
            fg=TEXT_PRIMARY,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.toggle_topmost
        )
        self.btn_pin.pack(side="right", padx=(8, 0))

        btn_refresh = tk.Button(
            top_bar,
            text="🔄 立即刷新",
            font=("Microsoft YaHei UI", 9),
            bg=BUTTON_BG,
            fg=ACCENT_CYAN,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.update_metrics
        )
        btn_refresh.pack(side="right")

        # 映射卡片
        self.card_pair = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid", padx=14, pady=8)
        self.card_pair.pack(fill="x", padx=16, pady=4)

        self.lbl_pair_info = tk.Label(
            self.card_pair,
            text="正在检测同步映射...",
            font=("Microsoft YaHei UI", 9),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
            wraplength=700
        )
        self.lbl_pair_info.pack(anchor="w")

        # 核心指标 4 列卡片
        stats_frame = tk.Frame(self, bg=BG_MAIN, padx=16, pady=6)
        stats_frame.pack(fill="x")
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.val_speed = self.create_metric_card(stats_frame, 0, "⚡ 实时网速", "0 KB/s", SUCCESS_GREEN)
        self.val_eta = self.create_metric_card(stats_frame, 1, "⏳ 预计剩余 (ETA)", "--", ACCENT_CYAN)
        self.val_files = self.create_metric_card(stats_frame, 2, "📊 文件进度", "0 / 0", TEXT_PRIMARY)
        self.val_bytes = self.create_metric_card(stats_frame, 3, "📦 传输数据量", "0 B / 0 B", WARNING_YELLOW)

        # 进度条区
        prog_frame = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid", padx=14, pady=10)
        prog_frame.pack(fill="x", padx=16, pady=6)

        self.lbl_prog_title = tk.Label(
            prog_frame,
            text="总体同步进度：0.0%",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_CARD
        )
        self.lbl_prog_title.pack(anchor="w")

        # 现代画布进度条
        self.can_prog = tk.Canvas(prog_frame, height=18, bg="#1e1e2e", bd=0, highlightthickness=0)
        self.can_prog.pack(fill="x", pady=(6, 4))

        self.lbl_active_task = tk.Label(
            prog_frame,
            text="当前活动任务：无",
            font=("Microsoft YaHei UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            wraplength=700,
            justify="left"
        )
        self.lbl_active_task.pack(anchor="w")

        # 历史流水日志列表
        log_frame = tk.Frame(self, bg=BG_MAIN, padx=16, pady=6)
        log_frame.pack(fill="both", expand=True)

        l_title = tk.Label(
            log_frame,
            text="📋 最近同步历史流水 (Live Activity Feed)：",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_MAIN
        )
        l_title.pack(anchor="w", pady=(0, 4))

        self.txt_sync_logs = tk.Text(
            log_frame,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Consolas", 9),
            padx=10,
            pady=8,
            bd=0,
            wrap="word"
        )
        self.txt_sync_logs.pack(fill="both", expand=True)

        # 底部按钮
        bot_bar = tk.Frame(self, bg=BG_MAIN, padx=16, pady=10)
        bot_bar.pack(fill="x")

        btn_open_folder = tk.Button(
            bot_bar,
            text="📂 打开本地同步文件夹",
            font=("Microsoft YaHei UI", 9),
            bg=BUTTON_BG,
            fg=TEXT_PRIMARY,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.open_local_folder
        )
        btn_open_folder.pack(side="left")

    def create_metric_card(self, parent, col, title, initial_val, color):
        f = tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid", padx=10, pady=8)
        f.grid(row=0, column=col, sticky="nsew", padx=4)

        tk.Label(f, text=title, font=("Microsoft YaHei UI", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        lbl_val = tk.Label(f, text=initial_val, font=("Microsoft YaHei UI", 12, "bold"), fg=color, bg=BG_CARD)
        lbl_val.pack(anchor="w", pady=(2, 0))
        return lbl_val

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.wm_attributes("-topmost", self.is_topmost)
        self.btn_pin.config(
            text="📌 取消置顶" if self.is_topmost else "📌 窗口置顶",
            bg="#543e78" if self.is_topmost else BUTTON_BG
        )

    def open_local_folder(self):
        snap = sync_monitor.get_progress_snapshot()
        if snap["has_pair"]:
            p = snap["pair"]["local_path"]
            if os.path.exists(p):
                subprocess.Popen(["explorer.exe", p])

    def update_metrics(self):
        snap = sync_monitor.get_progress_snapshot()
        if not snap["has_pair"]:
            self.lbl_pair_info.config(text="⚠️ 尚未检测到任何已配置的同步目录。请在 Telegram Drive 设置 → 目录自动同步 中添加。")
            return

        pair = snap["pair"]
        dir_text = "单向上传到云端" if pair["direction"] == "upload_only" else "双向自动同步"
        info_str = f"📁 本地目录: {pair['local_path']}\n🎯 目标频道: {pair['label']} (ID: {pair['channel_id']}) | 模式: {dir_text} | 状态: {snap['status_text']}"
        self.lbl_pair_info.config(text=info_str)

        self.val_speed.config(text=snap["speed_text"])
        self.val_eta.config(text=snap["eta_text"])
        self.val_files.config(text=f"{snap['synced_files']} / {snap['total_files']}")

        sz_done = f"{snap['synced_bytes'] / (1024**3):.2f} GB" if snap['synced_bytes'] >= 1024**3 else f"{snap['synced_bytes'] / (1024**2):.1f} MB"
        sz_total = f"{snap['total_bytes'] / (1024**3):.2f} GB" if snap['total_bytes'] >= 1024**3 else f"{snap['total_bytes'] / (1024**2):.1f} MB"
        self.val_bytes.config(text=f"{sz_done} / {sz_total}")

        pct = snap["percent"]
        self.lbl_prog_title.config(text=f"总体同步进度：{pct:.1f}% ({snap['synced_files']}/{snap['total_files']} 文件)")
        self.lbl_active_task.config(text=f"当前活动任务：{snap['active_file']}")

        # 绘制进度条
        self.can_prog.delete("all")
        w = self.can_prog.winfo_width()
        if w <= 1:
            w = 700
        fill_w = int(w * (pct / 100.0))
        if fill_w > 0:
            self.can_prog.create_rectangle(0, 0, fill_w, 18, fill=ACCENT_CYAN, width=0)

        # 更新历史流水
        self.txt_sync_logs.delete("1.0", "end")
        for log_item in snap["recent_logs"]:
            line = f"[{log_item['time']}] [{log_item['action'].upper()}] {log_item['path']} - {log_item['detail']}\n"
            self.txt_sync_logs.insert("end", line)

    def refresh_loop(self):
        try:
            self.update_metrics()
        except Exception:
            pass
        self.after(1500, self.refresh_loop)

def main():
    app = TelegramDriveCompanionGUI()
    app.mainloop()

if __name__ == "__main__":
    main()

