#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 深度全景汉化与免赞助补丁引擎 (Patch Engine v6.0 - 兼容 v3.9.8 与 v4.0.0 双版本)
银月独立开发工坊 · 工业级多轨资产无损切片热修复
"""

import os
import sys
import json
import struct
import shutil
import datetime
import traceback
import brotli

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LATEST_LOG = os.path.join(LOGS_DIR, "latest_run.log")

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {msg}"
    print(formatted)
    try:
        with open(LATEST_LOG, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

# =========================================================================
# 1. 341 个官方英文及损坏键位的 100% 纯正简体中文映射字典
# =========================================================================
TRANSLATIONS = {
    "common.app_title": "Telegram Drive",
    "common.start": "开始使用",
    "common.settings": "偏好设置",
    "common.light_mode": "浅色模式",
    "common.dark_mode": "深色模式",
    "common.switch_light": "切换浅色模式",
    "common.switch_dark": "切换深色模式",
    "common.expand_sidebar": "展开侧边栏",
    "common.collapse_sidebar": "折叠侧边栏",
    "common.groups": "文件夹分组",
    "common.all": "全部",
    "common.unassigned": "未分组",
    "common.hide_groups": "隐藏分组",
    "common.show_groups": "显示分组",
    "common.save": "保存",
    "common.create_group": "创建分组",
    "common.edit_group_name": "编辑分组名称",
    "common.new_group_name": "新分组名称",
    "common.theme_color": "主题颜色",
    "common.delete_group": "删除分组",
    "common.enter_group_name": "输入分组名称...",
    "common.hide_groups_desc": "在侧边栏中切换是否显示文件夹分组",

    # 设置分组导航大类 (彻底修复左侧栏英文标题)
    "settings.group_essentials": "基础设置",
    "settings.group_security_privacy": "安全与隐私",
    "settings.group_connections": "连接与同步",
    "settings.group_advanced": "高级网络",
    "settings.group_support": "关于与支持",

    # 选项卡标题修复
    "settings.tab_general": "通用设置",
    "settings.tab_themes": "个性主题",
    "settings.tab_privacy": "安全与隐私",
    "settings.tab_encryption": "端到端加密",
    "settings.tab_sharing": "分享管理",
    "settings.tab_advanced": "高级网络与系统集成",
    "settings.tab_vpn": "网络与 VPN 调优",
    "settings.tab_proxy": "网络代理",
    "settings.tab_webdav": "WebDAV 本地磁盘挂载",
    "settings.tab_about": "关于软件",

    # 赞助者全景翻译 (彻底清除官方损坏乱码)
    "supporter_license.title": "终身免广告支持者授权",
    "supporter_license.nav_title": "赞助与授权",
    "supporter_license.purchased_title": "已激活免广告",
    "supporter_license.manage_license": "恢复或管理授权",
    "supporter_license.active": "终身免广告已生效",
    "supporter_license.inactive": "未激活赞助者授权",
    "supporter_license.checking": "正在检测授权状态...",
    "supporter_license.description": "所有功能在免费版均可完整使用。赞助支持可为已激活设备永久移除所有赞助提示。",
    "supporter_license.ad_free_life": "终身免广告",
    "supporter_license.free_forever": "永久免费版",
    "supporter_license.all_features": "解锁所有核心功能",
    "supporter_license.no_account_subscription": "无需注册第三方账户，零订阅收费",
    "supporter_license.sponsors_labeled": "带标签的赞助内容",
    "supporter_license.sponsors_removed": "永久移除赞助内容",
    "supporter_license.payment_verified": "赞助验证成功，已为您永久移除赞助提示！",
    "supporter_license.purchase_restored": "已成功在此设备上恢复已购授权！",

    # 目录自动同步核心
    "settings.tab_sync": "目录自动同步",
    "settings.sync.title": "目录自动同步",
    "settings.sync.description": "自动将本地文件夹与指定的 Telegram 频道保持单向或双向同步。",
    "settings.sync.toggle": "启用目录自动同步",
    "settings.sync.select_folder": "选择本地文件夹",
    "settings.sync.folder_added": "已成功添加同步文件夹",
    "settings.sync.off_by_default": "目录同步默认处于关闭状态",
    "settings.sync.onboarding": "在您主动开启前不会同步任何数据。超过 2GB 的文件将自动跳过，当突发大量文件被删除时将自动暂停同步以保护云端资产。",
    "settings.sync.folder_mapper": "目录映射关系",
    "settings.sync.mapper_description": "将本地文件夹映射到已有的 Telegram 频道。",
    "settings.sync.remove": "移除同步文件夹",
    "settings.sync.add_folder": "添加同步文件夹",
    "settings.sync.select_channel": "选择 Telegram 频道",
    "settings.sync.no_channels": "在创建同步映射之前，请先刷新您的 Telegram 文件夹列表。",

    # 设置视窗各面板
    "settings.rest_api": "REST 本地接口",
    "settings.transfers": "传输设置",
    "settings.max_uploads_desc": "最大并行上传任务数 (建议设为 1 以确保大文件稳定不丢包)",
    "settings.max_downloads_desc": "最大并行下载任务数",
    "settings.zip_folders_desc": "上传前将整个文件夹打包压缩为 .zip",
    "settings.performance_compatibility": "性能与兼容性",
    "settings.performance_mode_desc": "关闭磨砂毛玻璃与高开销动画，大幅降低 CPU 与显卡占用",
    "settings.language_region": "语言与区域",
    "settings.app_language": "界面语言",
    "settings.choose_language": "选择您的首选界面语言",
    "settings.enable_api_server_desc": "启动后台轻量 API 接口，便于通过脚本或第三方程序管理文件",
    "settings.api_running": "服务正在运行于端口 {{port}}",
    "settings.api_stopped": "仅限本机访问 (127.0.0.1)",
    "settings.api_key_configured": "访问密钥已配置",
    "settings.api_key_unset": "尚未设置访问密钥",
    "settings.regenerate": "重新生成",
    "settings.generate": "生成密钥",
    "settings.api_copy_alert": "请立即复制并妥善保管 — 此密钥关闭后将不再显示",
    "settings.storage": "本地存储与缓存",
    "settings.transcode_cache_desc": "在线播放 HLS 流媒体切片所允许占用的最大磁盘空间",
    "settings.proxy_config": "网络代理配置",
    "settings.enable_proxy_desc": "通过本地代理服务器路由软件网络流量",
    "settings.socks5_desc": "SOCKS5 代理协议 (推荐，性能更优)",
    "settings.host_desc": "本地代理监听地址 (通常为 127.0.0.1)",
    "settings.port_desc": "有效端口范围：1–65535 (如 Clash 默认 7897 或 7890)",
    "settings.optional": "可选",
    "settings.proxy_reconnect_note": "⚠️ 代理设置修改后需要重新连接才能生效。",
    "settings.reconnecting": "正在重新连接代理...",
    "settings.reconnect_now": "立即重新连接",
    "settings.vpn_optimizer": "网络优化器",
    "settings.vpn_mode": "网络长连接优化模式",
    "settings.vpn_mode_desc": "针对高延迟或代理连接深度优化，防止大文件传输途中被掐断",
    "settings.timeout_multiplier": "超时等待倍率",
    "settings.timeout_multiplier_desc": "成倍增加网络请求等待超时时间，显著降低网络抖动报错",
    "settings.retry_attempts": "失败重试次数",
    "settings.retry_attempts_desc": "网络请求中断或失败时的自动重试次数",
    "settings.retry_backoff": "重试退避间隔",
    "settings.base_delay": "基础退避等待",
    "settings.max_delay": "最大退避等待",
    "settings.adaptive_polling": "自适应网络轮询",
    "settings.adaptive_polling_desc": "根据网络状态自动动态调整会话保活与更新轮询间隔",
    "settings.min_interval": "最小轮询间隔",
    "settings.max_interval": "最大轮询间隔",
    "settings.preferred_dc": "首选 Telegram 数据中心",
    "settings.preferred_dc_desc": "优先连接的 Telegram 官方接入点 (自动或固定 DC)",
    "settings.dc_fallback_attempts": "数据中心切换重试",
    "settings.dc_fallback_desc": "当前节点连接失败时尝试备用数据中心的次数",
    "settings.respect_flood": "遵循官方频控等待 (Flood Wait)",
    "settings.respect_flood_desc": "遭遇 Telegram 官方限频时自动休眠等待，绝不强行并发导致封禁",
    "settings.peer_cache_size": "节点缓存容量",
    "settings.peer_cache_desc": "本地缓存的频道与对等实体解析条数",
    "settings.bandwidth_throttle": "传输带宽限制",
    "settings.upload_limit": "上传速度上限",
    "settings.download_limit": "下载速度上限",
    "settings.unlimited": "不限速 (极致全速)",
    "settings.transfer_chunk_size": "传输分片切片大小",
    "settings.chunk_size_desc": "分片大小 (推荐 512 KB，兼具速度与稳定性)",
    "settings.keep_alive": "长连接保活心跳 (Keep-Alive)",
    "settings.keep_alive_desc": "定时发送保活心跳包，彻底防止代理节点在长传长下中因空闲切断连接",
    "settings.off": "关闭",
    "settings.bulk_archive_limit": "批量打包内存上限",
    "settings.bulk_archive_desc": "API 文件批量打包下载时允许占用的最大内存空间",
    "settings.auto_detect_vpn": "自动检测代理状态",
    "settings.vpn_detected": "已检测到网络代理接口",
    "settings.no_vpn_detected": "未检测到代理接口",
    "settings.checking": "正在检测中...",
    "settings.shared_links": "已分享链接 ({{count}})",
    "settings.refresh_links": "刷新链接列表",
    "settings.ip_override": "Tailscale / 局域网 IP 覆盖",
    "settings.ip_override_desc": "复制分享链接时自动将 '127.0.0.1:14201' 替换为此 IP 或域名。",
    "settings.no_active_links": "暂无生效中的分享链接",
    "settings.no_active_links_desc": "在任意文件上右键点击并选择“创建分享链接”即可添加。",
    "settings.protected": "密码保护",
    "settings.public": "公开访问",
    "settings.expired": "已过期",
    "settings.expires_at": "有效期至：{{date}}",
    "settings.never_expires": "永久有效",
    "settings.copy_share_link": "复制分享链接",
    "settings.revoke_link": "撤销此链接",
    "settings.copy_diagnostics": "复制网络诊断信息",
    "settings.reset_defaults": "恢复默认设置",
    "settings.done": "完成保存",
    "settings.auto": "自动",
    "settings.clear_local_cache": "清理本地缓存",
    "settings.clear_local_cache_desc": "清除本地缓存的缩略图、预览文件和临时传输分片",
    "settings.clear_cache_title": "确认清理本地缓存",
    "settings.clear_cache_desc": "此操作将清除所有已缓存的本地预览和临时文件。您在 Telegram 云端的文件绝不会受到任何影响。",
    "settings.clear": "立即清理",
    "settings.cache_cleared": "本地缓存已成功清理",
    "settings.cache_clear_failed": "清理本地缓存失败",
    "settings.clearing": "正在清理中...",
    "settings.transcode_cache": "视频转码缓存",
    "settings.clear_transcode_title": "清除所有转码缓存",
    "settings.clear_transcode_message": "这将删除所有已转码的 HLS 视频变体及缓存的原件。后续若需播放 HLS 将重新转码。",
    "settings.clear_all": "清除全部",
    "settings.failed_prefix": "失败：{{error}}",
    "settings.clear_variants_for": "清除 {{key}} 的所有转码版本",
    "settings.original": "原始文件",
    "settings.no_transcoded_cached": "暂无已缓存的转码视频",
    "settings.updates": "版本更新",
    "settings.check_for_updates": "检查最新版本",
    "settings.check_updates_desc": "检查是否有新的版本可用",
    "settings.update_restart": "更新并重启软件",
    "settings.check_now": "立即检查",
    "settings.update_available_toast": "发现新版本 v{{version}} 可用！",
    "settings.latest_version_toast": "当前已是最新版本",
    "settings.update_prod_only_toast": "检查更新仅在正式版中可用",
    "settings.update_check_failed_toast": "检查更新失败：{{error}}",
    "settings.update_failed_toast": "版本更新失败：{{error}}",
    "settings.load_shares_failed": "加载分享列表失败：{{error}}",
    "settings.revoke_link_title": "撤销分享链接",
    "settings.revoke_link_desc": "确定要撤销此链接吗？撤销后任何人都无法再通过此链接下载该文件。",
    "settings.link_revoked": "分享链接已成功撤销",
    "settings.link_revoke_failed": "撤销分享链接失败：{{error}}",
    "settings.port_range_error": "端口必须在 1024 到 65535 之间",
    "settings.api_server_started": "API 本地服务已启动",
    "settings.api_server_stopped": "API 本地服务已停止",
    "settings.api_update_failed": "更新 API 配置失败：{{error}}",
    "settings.api_port_updated": "API 端口已修改为 {{port}}",
    "settings.api_port_update_failed": "修改端口失败：{{error}}",
    "settings.generate_api_key_title": "生成 API 密钥",
    "settings.regenerate_api_key_desc": "这将作废您当前的 API 密钥并生成新密钥。所有现有自动化集成将立即失效。",
    "settings.generate_api_key_desc": "生成用于 REST API 接口调用的安全认证密钥。",
    "settings.api_key_generated": "API 密钥生成成功",
    "settings.api_key_generate_failed": "生成密钥失败：{{error}}",
    "settings.copy_clipboard_failed": "复制到剪贴板失败",
    "settings.restart_app_toast": "重启软件后此更改将正式生效",
    "settings.offline": "离线",
    "settings.reconnect_success_toast": "已通过新代理设置成功重新连接",
    "settings.reconnect_failed_toast": "重新连接失败 — 请检查代理参数",
    "settings.reconnect_failed_err_toast": "重新连接失败：{{error}}",
    "settings.diagnostics_copied": "诊断报告已成功复制到剪贴板",
    "settings.diagnostics_copy_failed": "复制诊断报告失败：{{error}}",
    "settings.connection_diagnostics": "网络连接诊断",
    "settings.not_tested": "未测试",
    "settings.testing": "正在测试中...",
    "settings.check_ping": "测延迟 (Ping)",
    "settings.excellent": "极佳",
    "settings.good": "良好",
    "settings.fair": "一般",
    "settings.poor": "较差",
    "settings.unreachable": "无法连接",
    "settings.error": "错误",
    "settings.ms": "{{ms}} 毫秒",
    "settings.video_upload_mode": "默认视频上传方式",
    "settings.video_upload_mode_desc": "选择视频文件上传到 Telegram 时的呈现模式 (文件或流媒体模式)",
    "settings.video_mode_file": "以文件形式上传 (原汁原味文件格式，零转码，最高私密性)",
    "settings.video_mode_media": "以媒体形式上传 (支持 Telegram 内置在线流式播放与视频封面预览)",
    "settings.video_mode_streamable": "以流媒体形式上传 (带流媒体属性，支持在线播放)",
    "settings.zip_folders": "上传前打包压缩文件夹",
    "settings.bulk_archive_memory_limit": "批量打包内存限制",
    "settings.bulk_archive_memory_limit_desc": "REST API 批量下载时允许打包 zip 使用的最大内存空间",
    "settings.dc_fallback_attempts_desc": "当前数据中心连接异常时尝试备用数据中心的次数",
    "settings.exponential_backoff": "指数退避重试",
    "settings.exponential_backoff_desc": "网络错误时逐级递增重试等待间隔，有效平抑偶发断连",
    "settings.base_backoff_sec": "基础退避等待 (秒)",
    "settings.max_backoff_sec": "最大退避等待 (秒)",
    "settings.auth.api_id": "API ID (应用程序编号)",
    "settings.auth.api_hash": "API Hash (密钥散列值)",
    "settings.auth.phone_number": "电报绑定手机号",
    "settings.auth.verification_code": "电报登录验证码",
    "settings.auth.two_step_password": "两步验证安全密码",
    "settings.auth.session_status": "登录会话状态",
    "settings.auth.logged_in_as": "已登录账号：{{user}}",
    "settings.auth.logout": "退出当前登录",
    "settings.auth.login": "登录 Telegram",
}

FULL_OVERRIDES = dict(TRANSLATIONS)

# v4.0.0 额外增强键位
FULL_OVERRIDES.update({
    "runtime.startup_initial_label": "正在启动 Telegram Drive",
    "runtime.startup_initial_detail": "正在准备本地运行环境…",
    "runtime.startup_local_label": "检查本地服务环境",
    "runtime.startup_local_detail": "正在校验本地数据库与流媒体运行库…",
    "runtime.startup_session_label": "正在恢复登录会话",
    "runtime.startup_session_detail": "正在读取已保存的 Telegram 账户凭证…",
    "runtime.startup_connect_label": "正在启动 Telegram 核心服务",
    "runtime.startup_connect_detail": "正在初始化安全桌面客户端…",
    "runtime.startup_account_label": "正在验证电报账户",
    "runtime.startup_account_detail": "正在与 Telegram 官方服务器确认会话…",
    "runtime.startup_sponsor_label": "正在完成安全自检",
    "runtime.startup_sponsor_detail": "正在完成本地环境与权限检测…",
    "runtime.startup_empty_label": "准备就绪，请登录",
    "runtime.startup_empty_detail": "未检测到已保存的会话，请先登录电报账号。",
    "runtime.startup_invalid_label": "登录凭据需要重新验证",
    "runtime.startup_invalid_detail": "保存的登录凭据已过期或失效，请重新登录。",

    "help_topics.storage_question": "我的文件存储在哪里？",
    "help_topics.storage_answer": "文件作为消息保存在您的 Telegram 我的云盘 (收藏夹) 或私密频道中。本软件不设任何第三方云存储服务器，完全安全私密。",
    "help_topics.limits_question": "实际使用有什么限制？",
    "help_topics.limits_answer": "Telegram 单文件上限为 2 GB（大会员支持更高）。超大文件夹初次索引需要少量时间，界面会实时显示同步进度。",
    "help_topics.protection_question": "“端到端加密存储”有什么用？",
    "help_topics.protection_answer": "在上传前在本地加密文件内容。请务必牢记您的密钥与恢复包，Telegram 官方也无法解密被保护的文件。",
    "help_topics.sharing_question": "分享功能是如何工作的？",
    "help_topics.sharing_answer": "支持 Telegram 频道链接、本地密码保护分享直链或 WebDAV/REST 挂载，本地直链需保持电脑开机。",
    "help_topics.guest_question": "为什么访客模式连接 WebDAV 显示为空？",
    "help_topics.guest_answer": "WebDAV 挂载必须使用包含完整 Token 的 URL 路径，匿名或访客登录无权访问。",
    "help_topics.more": "需要更多技术支持？",
    "help_topics.support": "访问 GitHub 反馈问题",

    "ui_copy.help_faq": "使用帮助与常见问题",
    "ui_copy.close_help": "关闭帮助",
    "ui_copy.keyboard_shortcuts": "快捷键指南",
    "ui_copy.close_shortcuts": "关闭快捷键指南",
    "ui_copy.global_scope": "所有云盘文件夹",
    "ui_copy.current_scope": "当前文件夹 / 视图",
    "ui_copy.understood": "我已知晓",
    "ui_copy.nav_essentials": "基础设置",
    "ui_copy.nav_connections": "连接与同步",
    "ui_copy.nav_security": "安全与隐私",
    "ui_copy.nav_support": "关于与支持",
    "ui_copy.security_center": "安全中心",
    "ui_copy.how_it_works": "工作原理说明",
    "ui_copy.dark": "深色模式",
    "ui_copy.light": "浅色模式",
    "ui_copy.vault": "加密保险库",
    "ui_copy.recovery": "灾难恢复",
    "ui_copy.recovery_verified": "恢复演练已验证通过",
    "ui_copy.unlocked_session": "当前会话已解锁",

    "advanced_copy.proxy_description": "通过 SOCKS5 或 HTTP 代理路由网络流量",
    "advanced_copy.rest_description": "本地 RESTful API 自动化控制接口与密钥管理",
    "advanced_copy.vpn_description": "网络长连接保持与高延迟环境优化",
    "advanced_copy.vpn_title": "网络优化器",
    "advanced_copy.webdav_description": "WebDAV 本地磁盘挂载与网络驱动器映射",

    "upload_choice_copy.question": "请选择这 {{count}} 个文件的存储模式：",
    "upload_choice_copy.description": "您可以直接原样上传，或在上传前使用专属加密保护。",
    "upload_choice_copy.store": "普通极速存储",
    "upload_choice_copy.plain_description": "正常上传，兼具最高兼容性与极速分享。",
    "upload_choice_copy.protect": "端到端加密存储",
    "upload_choice_copy.protect_description": "上传前通过端到端密钥加密，云端无人能偷窥。",
})

MODAL_REPLACEMENTS_400 = [
    ('children:"Where your data goes"', 'children:"您的数据流向说明"'),
    ('children:"Telegram Drive has no account server of its own. Each destination below is separated by purpose."', 'children:"Telegram Drive 没有任何自建账户服务器。以下每个目的地均按用途严格隔离。"'),
    ('children:"Power-user connections are grouped here so everyday settings stay calm and focused. Use the settings search to find any option by name."', 'children:"高级用户连接选项已汇总于此，使日常设置保持简洁专注。您可通过搜索快速定位任意选项。"'),
    ('children:"REST API, WebDAV, proxy, VPN, and network tuning"', 'children:"REST API、WebDAV、网络代理、VPN 与底层传输调优"'),
    ('children:"Privacy policy summary:"', 'children:"隐私政策摘要："'),
    ('children:"Crash-only reporting"', 'children:"仅限崩溃日志上报"'),
    ('children:"Send anonymous crash reports"', 'children:"发送匿名崩溃报告"'),
    ('children:"Optional reports help diagnose unexpected app crashes. Normal usage, analytics, advertising activity, and file operations are never reported."', 'children:"可选报告有助于诊断应用意外崩溃。日常使用、统计分析、广告活动和文件操作绝不会被上报。"'),
    ('children:"Never sends file names, paths, contents, Telegram messages, credentials, or personal identifiers. Turning this off also clears reports waiting to be sent."', 'children:"绝不会发送文件名、路径、内容、Telegram 消息、凭据或个人身份信息。关闭此项还会清空待发送的报告。"'),
    ('children:"Use WebDAV, not SMB."', 'children:"请使用 WebDAV，而非 SMB。"'),
    ('Default restores the Quiet Utility theme. System follows your device, while presets and custom themes override these standard modes.', '默认模式将恢复极简主题。跟随系统将匹配设备外观，预设与自定义主题将覆盖这些标准模式。'),
    ('Connect with the complete generated', '请使用生成的完整'),
    ("URL. Finder's Guest/anonymous login has no token and will show an empty location; no guest account is created.", 'URL 连接。访客/匿名登录无 Token，将显示为空目录；软件不设访客账户。'),
]

DD_REPLACEMENTS_400 = [
    ('children:"This folder is empty"', 'children:"此文件夹为空"'),
    ('children:"Drag and drop files here, or click the button below to upload from your computer."', 'children:"将文件拖拽至此处，或点击下方按钮从电脑上传。"'),
    ('children:"Used this week:"', 'children:"本周已用流量:"'),
    ('children:"All transfers complete"', 'children:"所有传输任务已完成"'),
    ('children:"Cancel all"', 'children:"全部取消"'),
    ('children:"Clear finished"', 'children:"清除已完成任务"'),
    ('children:"Error loading files"', 'children:"文件列表加载失败"'),
    ('children:"Your files are ready. Finished items can be cleared whenever you like."', 'children:"您的文件已就绪。已完成的项目可随时清除。"'),
    ('children:"This creates a private Telegram channel that Telegram Drive presents as a folder. Its files remain in your Telegram account."', 'children:"此操作将在您的 Telegram 账户中创建一个私密频道，并在本软件中作为文件夹呈现。文件将完整保存在您的电报账户中。"'),
]

def purge_webview_cache():
    try:
        cache_dirs = [
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\Cache"),
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\Code Cache"),
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\DawnGraphiteCache"),
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\GPUCache"),
        ]
        for c in cache_dirs:
            if os.path.exists(c):
                shutil.rmtree(c, ignore_errors=True)
                log(f"Purged stale WebView2 cache: {c}", "CLEAN")
    except Exception as e:
        log(f"Notice while purging cache: {e}", "WARNING")

def align_configurations():
    """彻底锁死用户配置：极致网络、长连接保活心跳、单队列防止丢包、锁定 zh-CN、关闭自动更新"""
    appdata = os.path.expandvars(r"%APPDATA%\com.cameronamer.telegramdrive")
    os.makedirs(appdata, exist_ok=True)

    settings_file = os.path.join(appdata, "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            s = data.setdefault("settings", {})
            s["language"] = "zh-CN"
            s["autoUpdate"] = False
            s["keepAliveIntervalSec"] = 15     # 15秒长连接心跳，彻底防代理节点掐断
            s["maxConcurrentUploads"] = 1       # 单并发，大文件独占稳定通道
            s["maxConcurrentDownloads"] = 2
            s["retryAttempts"] = 5              # 失败自动重试5次
            s["performanceMode"] = True         # 开启低功耗性能模式
            s["floodWaitRespect"] = True
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log("Aligned settings.json: language='zh-CN', autoUpdate=False, keepAlive=15s, maxUploads=1", "SUCCESS")
        except Exception as e:
            log(f"Failed to align settings.json: {e}", "WARNING")

    net_file = os.path.join(appdata, "network_settings.json")
    try:
        net_cfg = {
            "proxy": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 7897,
                "proxy_type": "socks5",
                "username": None,
                "password": None
            },
            "vpn": {
                "enabled": True,
                "preferred_dc": "auto",
                "timeout_multiplier": 4,
                "retry_attempts": 5,
                "retry_base_backoff_sec": 1.0,
                "retry_max_backoff_sec": 30,
                "bandwidth_limit_up_kbs": 0,
                "bandwidth_limit_down_kbs": 0,
                "chunk_size_kb": 512,
                "keep_alive_interval_sec": 15,
                "bulk_archive_max_mb": 0,
                "adaptive_polling": True
            }
        }
        with open(net_file, "w", encoding="utf-8") as f:
            json.dump(net_cfg, f, indent=2, ensure_ascii=False)
        log("Aligned network_settings.json: SOCKS5 127.0.0.1:7897, keep_alive=15s, chunk=512KB", "SUCCESS")
    except Exception as e:
        log(f"Failed to align network_settings.json: {e}", "WARNING")

def patch_v400(target_app_path, bak):
    """v4.0.0 专属切片补丁引擎"""
    log(f"Applying v4.0.0 patch pipeline on: {target_app_path}", "INFO")
    with open(bak, "rb") as f:
        data = bytearray(f.read())

    # 1. zh-CN-CkbYkfWF.json
    zh_marker = b"/assets/zh-CN-CkbYkfWF.json"
    zh_pos = data.find(zh_marker)
    if zh_pos == -1:
        raise RuntimeError("v4.0.0 zh-CN marker not found in binary!")
    zh_slot_len = 16291
    zh_table_entry = 42480520
    zh_start = zh_pos + len(zh_marker)

    tkeys_marker = b"/assets/translation-keys-DEga68nQ.json"
    tkeys_pos = data.find(tkeys_marker)
    tkeys = json.loads(brotli.decompress(bytes(data[tkeys_pos + len(tkeys_marker) : tkeys_pos + len(tkeys_marker) + 7950])).decode('utf-8'))['keys']

    raw_zh_bytes = brotli.decompress(bytes(data[zh_start:zh_start + zh_slot_len]))
    zh_dict = json.loads(raw_zh_bytes.decode('utf-8'))
    zh_vals = list(zh_dict['values'])

    for idx, key in enumerate(tkeys):
        if key in FULL_OVERRIDES:
            zh_vals[idx] = FULL_OVERRIDES[key]

    zh_dict['values'] = zh_vals
    zh_encoded = json.dumps(zh_dict, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    comp_zh = brotli.compress(zh_encoded, quality=11)
    if len(comp_zh) > zh_slot_len:
        raise ValueError(f"zh-CN exceeds slot: {len(comp_zh)} > {zh_slot_len}")

    data[zh_start:zh_start + len(comp_zh)] = comp_zh
    data[zh_start + len(comp_zh):zh_start + zh_slot_len] = b'\x00' * (zh_slot_len - len(comp_zh))
    data[zh_table_entry:zh_table_entry + 8] = struct.pack('<Q', len(comp_zh))
    log(f"[1/5] zh-CN table entry updated at {zh_table_entry}: len={len(comp_zh)}", "SUCCESS")

    # 2. SettingsModal-43sao1kq.js
    modal_marker = b"/assets/SettingsModal-43sao1kq.js"
    modal_pos = data.find(modal_marker)
    if modal_pos == -1:
        raise RuntimeError("v4.0.0 SettingsModal marker not found!")
    modal_slot_len = 27919
    modal_table_entry = 42482632
    modal_start = modal_pos + len(modal_marker)

    raw_modal_js = brotli.decompress(bytes(data[modal_start:modal_start + modal_slot_len])).decode('utf-8')
    mod_modal = raw_modal_js
    for old, new in MODAL_REPLACEMENTS_400:
        if old in mod_modal:
            mod_modal = mod_modal.replace(old, new)

    comp_modal = brotli.compress(mod_modal.encode('utf-8'), quality=11)
    if len(comp_modal) > modal_slot_len:
        raise ValueError(f"SettingsModal exceeds slot: {len(comp_modal)} > {modal_slot_len}")

    data[modal_start:modal_start + len(comp_modal)] = comp_modal
    data[modal_start + len(comp_modal):modal_start + modal_slot_len] = b'\x00' * (modal_slot_len - len(comp_modal))
    data[modal_table_entry:modal_table_entry + 8] = struct.pack('<Q', len(comp_modal))
    log(f"[2/5] SettingsModal table entry updated at {modal_table_entry}: len={len(comp_modal)}", "SUCCESS")

    # 3. DesktopDashboard-mGTjIwIz.js
    dd_marker = b"/assets/DesktopDashboard-mGTjIwIz.js"
    dd_pos = data.find(dd_marker)
    if dd_pos == -1:
        raise RuntimeError("v4.0.0 DesktopDashboard marker not found!")
    dd_slot_len = 76845
    dd_table_entry = 42480488
    dd_start = dd_pos + len(dd_marker)

    raw_dd_js = brotli.decompress(bytes(data[dd_start:dd_start + dd_slot_len])).decode('utf-8')
    mod_dd = raw_dd_js
    for old, new in DD_REPLACEMENTS_400:
        if old in mod_dd:
            mod_dd = mod_dd.replace(old, new)

    target_qf = 'function qf({suppressed:e=!1,onSupport:t,onManualDismiss:n,previewContent:r}){'
    if target_qf in mod_dd:
        mod_dd = mod_dd.replace(target_qf, target_qf + 'return null;')
        log("[KILL] Neutralized qf Ad Banner component with 'return null'", "CLEAN")

    target_th = 'b&&s.jsx(mt,{children:s.jsx(Th,{trigger:b,'
    if target_th in mod_dd:
        mod_dd = mod_dd.replace(target_th, '!1&&s.jsx(mt,{children:s.jsx(Th,{trigger:b,')
        log("[KILL] Neutralized Th SupporterOfferDialog mount with '!1&&...'", "CLEAN")

    comp_dd = brotli.compress(mod_dd.encode('utf-8'), quality=11)
    if len(comp_dd) > dd_slot_len:
        raise ValueError(f"DesktopDashboard exceeds slot: {len(comp_dd)} > {dd_slot_len}")

    data[dd_start:dd_start + len(comp_dd)] = comp_dd
    data[dd_start + len(comp_dd):dd_start + dd_slot_len] = b'\x00' * (dd_slot_len - len(comp_dd))
    data[dd_table_entry:dd_table_entry + 8] = struct.pack('<Q', len(comp_dd))
    log(f"[3/5] DesktopDashboard table entry updated at {dd_table_entry}: len={len(comp_dd)}", "SUCCESS")

    # 4. SupporterOfferDialog-pvEusOCY.js
    supp_marker = b"/assets/SupporterOfferDialog-pvEusOCY.js"
    supp_pos = data.find(supp_marker)
    if supp_pos != -1:
        supp_slot_len = 1679
        supp_table_entry = 42481320
        supp_start = supp_pos + len(supp_marker)
        raw_supp_js = brotli.decompress(bytes(data[supp_start:supp_start + supp_slot_len])).decode('utf-8')
        mod_supp = raw_supp_js
        target_fn = 'function v({trigger:r,presentation:n="dialog",onClose:s,onOpenSupporter:p}){'
        if target_fn in mod_supp:
            mod_supp = mod_supp.replace(target_fn, target_fn + 'return null;')
            log("[KILL] Neutralized SupporterOfferDialog v component with 'return null'", "CLEAN")

        comp_supp = brotli.compress(mod_supp.encode('utf-8'), quality=11)
        if len(comp_supp) <= supp_slot_len:
            data[supp_start:supp_start + len(comp_supp)] = comp_supp
            data[supp_start + len(comp_supp):supp_start + supp_slot_len] = b'\x00' * (supp_slot_len - len(comp_supp))
            data[supp_table_entry:supp_table_entry + 8] = struct.pack('<Q', len(comp_supp))
            log(f"[4/5] SupporterOfferDialog table entry updated at {supp_table_entry}: len={len(comp_supp)}", "SUCCESS")

    # 5. index-Bo5-zB0o.js
    idx_marker = b"/assets/index-Bo5-zB0o.js"
    idx_pos = data.find(idx_marker)
    if idx_pos == -1:
        raise RuntimeError("v4.0.0 index marker not found!")
    idx_slot_len = 150588
    idx_table_entry = 42481576
    idx_start = idx_pos + len(idx_marker)

    raw_idx_js = brotli.decompress(bytes(data[idx_start:idx_start + idx_slot_len])).decode('utf-8')
    mod_idx = raw_idx_js

    target_gd = 'function gD(n){return n.state!=="loading"&&!n.ad_free}'
    if target_gd in mod_idx:
        mod_idx = mod_idx.replace(target_gd, 'function gD(n){return!1/*====================*/&&!n.ad_free}')
        log("[KILL] Disabled gD sponsor check in index-Bo5-zB0o.js", "CLEAN")

    target_yd = 'function yD(n){return n.state==="inactive"&&!n.ad_free&&!n.recovery_code_saved}'
    if target_yd in mod_idx:
        mod_idx = mod_idx.replace(target_yd, 'function yD(n){return!1/*==========================================*/&&!n.ad_free}')
        log("[KILL] Disabled yD sponsor check in index-Bo5-zB0o.js", "CLEAN")

    comp_idx = brotli.compress(mod_idx.encode('utf-8'), quality=11)
    if len(comp_idx) > idx_slot_len:
        raise ValueError(f"index exceeds slot: {len(comp_idx)} > {idx_slot_len}")

    data[idx_start:idx_start + len(comp_idx)] = comp_idx
    data[idx_start + len(comp_idx):idx_start + idx_slot_len] = b'\x00' * (idx_slot_len - len(comp_idx))
    data[idx_table_entry:idx_table_entry + 8] = struct.pack('<Q', len(comp_idx))
    log(f"[5/5] index table entry updated at {idx_table_entry}: len={len(comp_idx)}", "SUCCESS")

    # 边界断言自检
    assert data[zh_start + zh_slot_len] == 0x2f, "zh boundary corrupted!"
    assert data[modal_start + modal_slot_len] == 0x2f, "modal boundary corrupted!"
    assert data[dd_start + dd_slot_len] == 0x2f, "dd boundary corrupted!"
    assert data[supp_start + supp_slot_len] == 0x2f, "supp boundary corrupted!"
    assert data[idx_start + idx_slot_len] == 0x2f, "idx boundary corrupted!"

    with open(target_app_path, "wb") as f:
        f.write(data)
    log(f"Successfully injected all patches into: {target_app_path}", "SUCCESS")

    tool_lib_target = r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\Telegram-Drive-CN.exe"
    if os.path.exists(os.path.dirname(tool_lib_target)):
        shutil.copyfile(target_app_path, tool_lib_target)
        log(f"Synchronized patched v4.0.0 binary to Tool Library: {tool_lib_target}", "SUCCESS")

    align_configurations()
    purge_webview_cache()
    log("Configurations aligned and WebView2 cache purged. Ready to launch!", "SUCCESS")
    return True

def run_patch():
    target_app_path = r"D:\app\Telegram Drive\app.exe"
    if not os.path.exists(target_app_path):
        log(f"Target executable not found at: {target_app_path}", "ERROR")
        return False

    with open(target_app_path, "rb") as f:
        head = f.read(58500000)

    # 检测是否为 v4.0.0
    if b"/assets/zh-CN-CkbYkfWF.json" in head:
        bak400 = target_app_path + ".v400.bak"
        if not os.path.exists(bak400):
            shutil.copyfile(target_app_path, bak400)
            log(f"Created pristine v4.0.0 backup: {bak400}", "CLEAN")
        return patch_v400(target_app_path, bak400)

    # 检测是否为 v3.9.8
    elif b"/assets/zh-CN-Cp_y0Z7o.json" in head:
        bak398 = target_app_path + ".v398.bak"
        if not os.path.exists(bak398):
            shutil.copyfile(target_app_path, bak398)
            log(f"Created pristine v3.9.8 backup: {bak398}", "CLEAN")
        # 兼容调用 v3.9.8 补丁
        from .patcher_398_impl import patch_v398
        return patch_v398(target_app_path, bak398)
    else:
        log("Target executable version marker unrecognized!", "ERROR")
        return False

def check_patch_status(target_app_path=r"D:\app\Telegram Drive\app.exe"):
    """检测目标二进制文件的汉化与去赞助补丁生效状态 (自适应 v4.0.0 与 v3.9.8)"""
    if not os.path.exists(target_app_path):
        return False, "未找到目标文件"

    try:
        with open(target_app_path, "rb") as f:
            data = f.read()

        # 检测 v4.0.0
        zh_marker_400 = b"/assets/zh-CN-CkbYkfWF.json"
        zh_pos_400 = data.find(zh_marker_400)
        if zh_pos_400 != -1:
            zh_table_entry = 42480520
            zh_actual_len = struct.unpack('<Q', data[zh_table_entry:zh_table_entry + 8])[0]
            zh_start = zh_pos_400 + len(zh_marker_400)
            raw_zh = brotli.decompress(bytes(data[zh_start:zh_start + zh_actual_len])).decode('utf-8')
            has_vpn_cn = "网络与 VPN 调优" in raw_zh
            has_rest_cn = "REST 本地接口" in raw_zh

            supp_marker = b"/assets/SupporterOfferDialog-pvEusOCY.js"
            supp_pos = data.find(supp_marker)
            supp_killed = False
            if supp_pos != -1:
                supp_table_entry = 42481320
                supp_actual_len = struct.unpack('<Q', data[supp_table_entry:supp_table_entry + 8])[0]
                supp_start = supp_pos + len(supp_marker)
                raw_supp = brotli.decompress(bytes(data[supp_start:supp_start + supp_actual_len])).decode('utf-8')
                supp_killed = "return null;" in raw_supp

            if has_vpn_cn and supp_killed:
                return True, "v4.0.0 全量汉化与免弹窗已就绪"
            elif has_vpn_cn:
                return True, "v4.0.0 基础汉化已生效"
            else:
                return False, "v4.0.0 官方原版 (未打补丁)"

        # 检测 v3.9.8
        zh_marker_398 = b"/assets/zh-CN-Cp_y0Z7o.json"
        zh_pos_398 = data.find(zh_marker_398)
        if zh_pos_398 != -1:
            zh_table_entry = 38518680
            zh_actual_len = struct.unpack('<Q', data[zh_table_entry:zh_table_entry + 8])[0]
            zh_start = zh_pos_398 + len(zh_marker_398)
            raw_zh = brotli.decompress(bytes(data[zh_start:zh_start + zh_actual_len])).decode('utf-8')
            has_sync = "目录自动同步" in raw_zh

            supp_marker = b"/assets/SupporterOfferDialog-BhSlxpEY.js"
            supp_pos = data.find(supp_marker)
            supp_killed = False
            if supp_pos != -1:
                supp_table_entry = 38518872
                supp_actual_len = struct.unpack('<Q', data[supp_table_entry:supp_table_entry + 8])[0]
                supp_start = supp_pos + len(supp_marker)
                raw_supp = brotli.decompress(bytes(data[supp_start:supp_start + supp_actual_len])).decode('utf-8')
                supp_killed = "return null;" in raw_supp

            if has_sync and supp_killed:
                return True, "v3.9.8 全量汉化与免弹窗已就绪"
            elif has_sync:
                return True, "v3.9.8 基础汉化已生效"
            else:
                return False, "v3.9.8 官方原版 (未打补丁)"

        return False, "未识别版本特征"
    except Exception as e:
        return False, f"检测异常: {e}"

def execute_patch_workflow():
    """安全流程：终止进程 -> 注入补丁 -> 同步工具库 -> 清理缓存"""
    from .process_mgr import kill_app
    kill_app()
    return run_patch()

if __name__ == "__main__":
    try:
        ok = run_patch()
        sys.exit(0 if ok else 1)
    except Exception as e:
        log(f"Fatal error: {e}\n{traceback.format_exc()}", "ERROR")
        sys.exit(1)
