#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 极速网络与保活心跳调优模块 (Network Tuner)
深度调优長连接保活、分片大小、重试机制与代理配置，终结频繁中断
"""

import os
import json
import shutil
from .logger import log, log_error

APPDATA_DIR = os.path.expandvars(r"%APPDATA%\com.cameronamer.telegramdrive")
SETTINGS_JSON = os.path.join(APPDATA_DIR, "settings.json")
NETWORK_SETTINGS_JSON = os.path.join(APPDATA_DIR, "network_settings.json")

# 黄金参数配置定义
OPTIMAL_SETTINGS = {
    "language": "zh-CN",
    "autoUpdate": False,                # 禁用自动升级，防止覆盖汉化与免弹窗补丁
    "keepAliveIntervalSec": 30,         # 30秒长连接保活心跳，防止闲置TCP通道被静默掐断
    "maxConcurrentUploads": 1,          # 单任务稳步上传，杜绝电报官方限速/FLOOD_WAIT与丢包
    "maxConcurrentDownloads": 2,        # 双任务并行下载
    "performanceMode": True,            # 开启性能模式，关闭磨砂特效，大幅省CPU/显卡
    "zipFolders": False
}

OPTIMAL_NETWORK_SETTINGS = {
    "proxy_enabled": True,
    "proxy_protocol": "socks5",
    "proxy_host": "127.0.0.1",
    "proxy_port": 7897,                 # 适配本机主流代理客户端端口 (Clash/Verge)
    "keep_alive_seconds": 30,
    "timeout_multiplier": 4,            # 4倍超时容限，包容代理节点网络抖动
    "retry_attempts": 5,                # 失败自动重试5次，免去手动重新上传
    "retry_base_delay_ms": 1000,
    "chunk_size_kb": 512                # 512KB 最佳分片尺寸，契合 MTProto 传输协议
}

def inspect_network_config():
    """获取当前配置状态摘要"""
    status = {
        "configured": False,
        "keep_alive": 0,
        "max_uploads": 0,
        "proxy_port": 0,
        "timeout_multiplier": 1,
        "chunk_size_kb": 0,
        "auto_update": True,
        "language": "en"
    }
    
    if os.path.exists(SETTINGS_JSON):
        try:
            with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                s = json.load(f)
            status["keep_alive"] = s.get("keepAliveIntervalSec", 0)
            status["max_uploads"] = s.get("maxConcurrentUploads", 0)
            status["auto_update"] = s.get("autoUpdate", True)
            status["language"] = s.get("language", "en")
        except Exception:
            pass

    if os.path.exists(NETWORK_SETTINGS_JSON):
        try:
            with open(NETWORK_SETTINGS_JSON, "r", encoding="utf-8") as f:
                n = json.load(f)
            status["proxy_port"] = n.get("proxy_port", 0)
            status["timeout_multiplier"] = n.get("timeout_multiplier", 1)
            status["chunk_size_kb"] = n.get("chunk_size_kb", 0)
        except Exception:
            pass

    # 判定是否已满足黄金调优状态
    is_golden = (
        status["keep_alive"] == 30 and
        status["max_uploads"] == 1 and
        status["timeout_multiplier"] >= 4 and
        status["chunk_size_kb"] == 512 and
        status["auto_update"] is False
    )
    status["is_golden"] = is_golden
    return status

def apply_optimal_network():
    """一键应用黄金网络调优与长连接保活参数"""
    os.makedirs(APPDATA_DIR, exist_ok=True)
    changes = []

    # 1. 调优 settings.json
    try:
        cur_settings = {}
        if os.path.exists(SETTINGS_JSON):
            shutil.copy2(SETTINGS_JSON, SETTINGS_JSON + ".bak")
            try:
                with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                    cur_settings = json.load(f)
            except Exception:
                cur_settings = {}

        for k, v in OPTIMAL_SETTINGS.items():
            if cur_settings.get(k) != v:
                changes.append(f"settings.{k}: {cur_settings.get(k)} -> {v}")
                cur_settings[k] = v

        with open(SETTINGS_JSON, "w", encoding="utf-8") as f:
            json.dump(cur_settings, f, ensure_ascii=False, indent=2)
        log("[SUCCESS] settings.json 黄金调优已写入 (保活30s / 单并发上传 / 性能模式 / 关闭自更)", "SUCCESS")
    except Exception as e:
        log_error(f"写入 settings.json 失败: {e}", e)
        return False, f"写入 settings.json 失败: {e}"

    # 2. 调优 network_settings.json
    try:
        cur_network = {}
        if os.path.exists(NETWORK_SETTINGS_JSON):
            shutil.copy2(NETWORK_SETTINGS_JSON, NETWORK_SETTINGS_JSON + ".bak")
            try:
                with open(NETWORK_SETTINGS_JSON, "r", encoding="utf-8") as f:
                    cur_network = json.load(f)
            except Exception:
                cur_network = {}

        for k, v in OPTIMAL_NETWORK_SETTINGS.items():
            if cur_network.get(k) != v:
                changes.append(f"network.{k}: {cur_network.get(k)} -> {v}")
                cur_network[k] = v

        with open(NETWORK_SETTINGS_JSON, "w", encoding="utf-8") as f:
            json.dump(cur_network, f, ensure_ascii=False, indent=2)
        log("[SUCCESS] network_settings.json 黄金网络参数已写入 (SOCKS5 7897 / 4倍超时 / 5次重试 / 512KB分片)", "SUCCESS")
    except Exception as e:
        log_error(f"写入 network_settings.json 失败: {e}", e)
        return False, f"写入 network_settings.json 失败: {e}"

    log(f"[SUCCESS] 黄金网络与保活心跳参数已全量生效！变更项数: {len(changes)}", "SUCCESS")
    return True, f"成功调优！30s心跳保活 + 4倍超时 + 5次重试 + 512KB分片已生效。"
