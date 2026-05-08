"""
输入归一化模块 - 纯数据清洗，无状态无IO
负责将用户输入的脏数据清洗为标准格式
"""
import re

def _trim_blank(text: str) -> str:
    """
    去除首尾空格、多余换行、连续空格
    """
    if not text:
        return ""
    # 将多个空白字符（空格、换行、制表符）替换为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空格
    return text.strip()

def _convert_punctuation(text: str) -> str:
    """
    全角标点转半角，统一标点格式
    """
    if not text:
        return ""
    
    # 全角到半角的映射表
    full_to_half = {
        '，': ',', '。': '.', '！': '!', '？': '?',
        '；': ';', '：': ':', '“': '"', '”': '"',
        '‘': "'", '’': "'", '（': '(', '）': ')',
        '【': '[', '】': ']', '《': '<', '》': '>'
    }
    
    result = []
    for char in text:
        result.append(full_to_half.get(char, char))
    
    return ''.join(result)

def _remove_special_chars(text: str) -> str:
    """
    过滤表情包、@符号、特殊符号、非中英文字符
    保留：中文、英文、数字、常用标点
    """
    if not text:
        return ""
    
    # 保留中文字符、英文字母、数字、常用标点
    # \u4e00-\u9fff 是中文字符范围
    pattern = r'[^\u4e00-\u9fffA-Za-z0-9\s\.\,\!\?\;\:\'\"\(\)]'
    text = re.sub(pattern, '', text)
    
    # 移除单独的@符号
    text = re.sub(r'@', '', text)
    
    return text

def _merge_duplicate_words(text: str) -> str:
    """
    合并连续重复词汇（如"那个那个" -> "那个"）
    """
    if not text:
        return ""
    
    # 匹配2-3字的重复词汇
    pattern = r'(.{2,3})\1+'
    text = re.sub(pattern, r'\1', text)
    
    # 处理单字重复（如"哈哈哈" -> "哈"）
    pattern_single = r'(.)\1{2,}'
    text = re.sub(pattern_single, r'\1', text)
    
    return text

def normalize_input(text: str) -> str:
    """
    输入归一化总入口
    串联所有清洗逻辑，兜底处理空输入
    """
    # 兜底：空输入处理
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # 按顺序执行清洗
        normalized = text
        normalized = _trim_blank(normalized)
        normalized = _convert_punctuation(normalized)
        normalized = _remove_special_chars(normalized)
        normalized = _merge_duplicate_words(normalized)
        
        return normalized
    except Exception as e:
        # 异常兜底：返回空字符串
        print(f"归一化处理异常: {e}")
        return ""
