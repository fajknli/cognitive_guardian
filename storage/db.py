"""
数据库操作模块
负责本地数据存储，记录对话、姿态、审计日志
"""
import sqlite3
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import contextmanager

# 数据库路径
DB_PATH = "data/guardian.db"

@contextmanager
def get_connection():
    """
    获取数据库连接的上下文管理器
    自动处理事务和关闭
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使返回结果为字典形式
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database() -> None:
    """
    初始化数据库，创建4张核心表
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. 对话记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_input TEXT NOT NULL,
                normalized_input TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 姿态历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS postures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dialogue_id INTEGER NOT NULL,
                posture_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dialogue_id) REFERENCES dialogues(id)
            )
        ''')
        
        # 3. 自反审计记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dialogue_id INTEGER NOT NULL,
                reflection_content TEXT NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dialogue_id) REFERENCES dialogues(id)
            )
        ''')
        
        # 4. 模式切换日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mode_switches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_mode TEXT,
                to_mode TEXT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 

def save_original_dialogue(user_raw_input: str, normalized_input: str) -> int:
    """
    保存用户原始输入+归一化输入
    返回记录ID
    """
    if not user_raw_input and not normalized_input:
        return -1
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO dialogues (raw_input, normalized_input) VALUES (?, ?)',
            (user_raw_input or "", normalized_input or "")
        )
        return cursor.lastrowid

def save_posture_result(dialogue_id: int, posture_type: str, confidence: float) -> None:
    """
    保存姿态判定结果
    """
    if dialogue_id <= 0:
        return
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO postures (dialogue_id, posture_type, confidence) VALUES (?, ?, ?)',
            (dialogue_id, posture_type, confidence)
        )

def save_reflection_result(dialogue_id: int, reflection_content: str, note: str) -> None:
    """
    保存自反审计结果
    """
    if dialogue_id <= 0:
        return
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reflections (dialogue_id, reflection_content, note) VALUES (?, ?, ?)',
            (dialogue_id, reflection_content, note or "")
        )

def get_history_window(window_size: int = 3) -> List[Dict]:
    """
    获取指定长度时序历史窗口
    返回最近N条对话的姿态记录
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.raw_input, d.normalized_input, p.posture_type, p.confidence
            FROM dialogues d
            LEFT JOIN postures p ON d.id = p.dialogue_id
            ORDER BY d.created_at DESC
            LIMIT ?
        ''', (window_size,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_mode_switch_log(limit: int = 10) -> List[Dict]:
    """
    获取模式切换日志
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM mode_switches
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def save_mode_switch(from_mode: str, to_mode: str, reason: str = "") -> None:
    """
    保存模式切换记录
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO mode_switches (from_mode, to_mode, reason) VALUES (?, ?, ?)',
            (from_mode or "", to_mode, reason or "")
        )
