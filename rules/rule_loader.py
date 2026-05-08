"""
规则加载模块
负责加载和管理所有规则文件
"""
import json
import os
from typing import Dict, List, Tuple, Any

# 规则缓存
_rules_cache = {}

def load_single_rule(file_path: str) -> Dict[str, Any]:
    """
    加载单个JSON规则文件
    """
    try:
        if not os.path.exists(file_path):
            # 
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        #  {file_path}: {e}")
        return {}
    except Exception as e:
        #  {file_path}: {e}")
        return {}

def load_all_rules(rules_dir: str = "rules") -> Dict[str, Dict]:
    """
    一次性加载所有规则，全局复用
    """
    global _rules_cache
    
    if _rules_cache:
        return _rules_cache
    
    rule_files = {
        "posture": "posture_rules.json",
        "clarity": "clarity_rules.json",
        "remind": "remind_templates.json",
        "reflection": "reflection_rules.json"
    }
    
    for key, filename in rule_files.items():
        file_path = os.path.join(rules_dir, filename)
        _rules_cache[key] = load_single_rule(file_path)
    
    return _rules_cache

def match_posture_type(normalized_text: str, rules: Dict) -> Tuple[str, float]:
    """
    匹配认知姿态类型
    返回: (姿态类型, 置信度)
    """
    if not normalized_text or not rules:
        return ("混合姿态", 0.5)
    
    text_lower = normalized_text.lower()
    posture_rules = rules.get("rules", [])
    
    matches = []
    for rule in posture_rules:
        posture_name = rule.get("name", "")
        keywords = rule.get("keywords", [])
        weight = rule.get("weight", 0.5)
        
        # 统计匹配的关键词数量
        matched_count = 0
        for kw in keywords:
            if kw in text_lower:
                matched_count += 1
        
        min_matches = rule.get("min_matches", 1)
        if matched_count >= min_matches and keywords:
            confidence = min(0.9, weight * (1 + 0.1 * matched_count))
            matches.append((posture_name, confidence))
    
    if not matches:
        return ("混合姿态", 0.5)
    
    # 返回置信度最高的
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[0]

def judge_text_clarity(normalized_text: str, rules: Dict) -> str:
    """
    判定文本清晰/模糊
    返回: "清晰" 或 "模糊"
    """
    if not normalized_text:
        return "模糊"
    
    text_lower = normalized_text.lower()
    text_len = len(normalized_text)
    
    clear_indicators = rules.get("clear_indicators", {})
    vague_indicators = rules.get("vague_indicators", {})
    default_clarity = rules.get("default_clarity", "模糊")
    
    # 检查清晰指标
    clear_keywords = clear_indicators.get("keywords", [])
    min_length = clear_indicators.get("min_length", 5)
    has_punctuation = clear_indicators.get("has_punctuation", True)
    
    clear_score = 0
    for kw in clear_keywords:
        if kw in text_lower:
            clear_score += 1
    
    # 检查模糊指标
    vague_keywords = vague_indicators.get("keywords", [])
    too_short_threshold = vague_indicators.get("too_short_threshold", 3)
    
    vague_score = 0
    for kw in vague_keywords:
        if kw in text_lower:
            vague_score += 1
    
    # 短文本判定
    if text_len <= too_short_threshold:
        return "模糊"
    
    # 综合判定
    if clear_score > vague_score and text_len >= min_length:
        return "清晰"
    elif vague_score >= clear_score:
        return "模糊"
    
    return default_clarity

def check_reflection_rules(content: str, rule_set: Dict) -> List[str]:
    """
    校验自反审计维度，返回缺失要素列表
    """
    if not content:
        return ["意图完整性", "歧义风险"]
    
    dimensions = rule_set.get("dimensions", [])
    missing = []
    
    for dim in dimensions:
        dim_name = dim.get("name", "")
        is_required = dim.get("required", True)
        
        if not is_required:
            continue
        
        # 简单规则检查
        if dim_name == "意图完整性":
            if len(content) < 10:
                missing.append(dim_name)
        elif dim_name == "歧义风险":
            ambiguous_words = ["可能", "也许", "大概", "好像", "有点儿"]
            for word in ambiguous_words:
                if word in content:
                    missing.append(dim_name)
                    break
    
    return missing

# 自动加载所有规则
load_all_rules()
