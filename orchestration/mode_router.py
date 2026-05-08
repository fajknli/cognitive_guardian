"""
模式路由模块
负责根据文本清晰度和历史窗口判定工作模式
"""
from typing import List, Dict

# 模式常量
MODE_AUDIT = "audit"      # 审计模式
MODE_TRANSLATE = "translate"  # 翻译模式

def judge_work_mode(normalized_text: str, 
                    clarity_result: str,
                    confidence: float = 0.5,
                    history_window: List[Dict] = None) -> str:
    """
    根据文本清晰度+历史窗口，判定审计/翻译模式
    
    规则：
    1. 如果文本清晰且置信度>=0.6 -> 翻译模式
    2. 如果文本模糊或置信度<0.6 -> 审计模式
    3. 结合历史窗口做滞回处理
    """
    if history_window is None:
        history_window = []
    
    # 基本判定
    is_clear = (clarity_result == "清晰" and confidence >= 0.6)
    
    current_mode = MODE_TRANSLATE if is_clear else MODE_AUDIT
    
    return current_mode

def mode_hysteresis_switch(current_mode: str, 
                           new_mode: str,
                           mode_log: List[Dict],
                           switch_threshold: int = 2) -> str:
    """
    模式滞回缓冲，抑制频繁切换
    
    参数:
        current_mode: 当前模式
        new_mode: 新判定的模式
        mode_log: 历史模式切换日志
        switch_threshold: 需要连续几次一致才切换
    
    返回:
        最终使用的模式
    """
    if current_mode == new_mode:
        return current_mode
    
    # 如果没有历史记录，直接切换
    if not mode_log:
        return new_mode
    
    # 统计最近N次的新模式出现次数
    recent_modes = [log.get("to_mode", "") for log in mode_log[-switch_threshold:]]
    new_mode_count = recent_modes.count(new_mode)
    
    # 如果连续switch_threshold次都判定为新模式，才切换
    if new_mode_count >= switch_threshold:
        return new_mode
    
    # 否则保持当前模式
    return current_mode

def get_mode_reason(mode: str, clarity_result: str, confidence: float) -> str:
    """
    获取模式判定的原因说明
    """
    if mode == MODE_TRANSLATE:
        return f"文本清晰(置信度:{confidence:.2f})，进入翻译模式"
    else:
        return f"文本模糊或置信度低({confidence:.2f})，进入审计模式"
