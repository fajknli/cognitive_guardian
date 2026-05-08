"""
核心调度模块
负责全流程调度和子流程编排
"""
from typing import Dict, Optional
from datetime import datetime

# 导入各模块
from utils.logger import get_logger
from utils.text_normalizer import normalize_input
from storage.db import (
    save_original_dialogue, 
    save_posture_result, 
    save_reflection_result,
    save_mode_switch,
    get_history_window
)
from rules.rule_loader import match_posture_type, judge_text_clarity, load_all_rules
from rules.template_renderer import get_remind_content
from classifiers.infer import predict_posture, predict_clarity, fusion_rule_classifier

# 获取日志器
logger = get_logger("dispatcher")

# 全局规则缓存
_rules_cache = None

def get_rules():
    """获取规则缓存"""
    global _rules_cache
    if _rules_cache is None:
        _rules_cache = load_all_rules()
    return _rules_cache

def calc_output_confidence(result_source: str) -> float:
    """
    计算输出置信度
    result_source: "rule", "classifier", "fusion"
    """
    confidence_map = {
        "rule": 0.85,
        "classifier": 0.70,
        "fusion": 0.80,
        "fallback": 0.50
    }
    return confidence_map.get(result_source, 0.60)

def audit_mode_workflow(normalized_input: str, dialogue_id: int) -> Dict:
    """
    审计模式子流程：姿态判定 → 生成提醒
    """
    logger.info(f"执行审计模式工作流: {normalized_input[:50]}")
    
    rules = get_rules()
    posture_rules = rules.get("posture", {})
    
    # 1. 规则匹配姿态
    rule_posture, rule_conf = match_posture_type(normalized_input, posture_rules)
    logger.debug(f"规则匹配结果: {rule_posture} (置信度: {rule_conf})")
    
    # 2. 分类器预测姿态
    clf_posture, clf_conf = predict_posture(normalized_input)
    logger.debug(f"分类器预测结果: {clf_posture} (置信度: {clf_conf})")
    
    # 3. 融合结果
    final_posture, final_conf = fusion_rule_classifier(
        (rule_posture, rule_conf),
        (clf_posture, clf_conf)
    )
    
    # 4. 保存姿态结果
    save_posture_result(dialogue_id, final_posture, final_conf)
    
    # 5. 获取提醒内容
    remind_templates = rules.get("remind", {})
    remind_content = get_remind_content(final_posture, remind_templates)
    
    return {
        "mode": "audit",
        "posture": final_posture,
        "confidence": final_conf,
        "remind": remind_content,
        "result_source": "fusion"
    }

def translate_mode_workflow(normalized_input: str, dialogue_id: int) -> Dict:
    """
    翻译模式子流程：文本润色（使用模型或降级）
    """
    logger.info(f"执行翻译模式工作流: {normalized_input[:50]}")
    
    # 尝试使用模型润色
    polished_text = None
    source = "fallback"
    
    try:
        from llm.base import get_model, model_generate
        
        model = get_model()
        if model:
            prompt = f"请将以下文本改写得更加清晰流畅：\n{normalized_input}"
            polished_text = model_generate(model, prompt, temperature=0.1, max_tokens=256)
            if polished_text and len(polished_text) > 0:
                source = "model"
                logger.info("使用模型润色成功")
    except Exception as e:
        logger.warning(f"模型润色失败: {e}")
    
    # 降级：简单润色（去除重复空格、规范化）
    if not polished_text:
        polished_text = normalized_input.strip()
        source = "fallback"
        logger.info("使用降级润色")
    
    return {
        "mode": "translate",
        "original": normalized_input,
        "polished": polished_text,
        "source": source,
        "confidence": calc_output_confidence(source)
    }

def main_workflow(user_input: str) -> Dict:
    """
    全流程调度总入口
    """
    logger.info(f"收到用户输入: {user_input[:100]}")
    
    # 1. 输入归一化
    normalized = normalize_input(user_input)
    logger.debug(f"归一化结果: {normalized}")
    
    # 2. 保存原始对话
    dialogue_id = save_original_dialogue(user_input, normalized)
    logger.info(f"对话已保存, ID: {dialogue_id}")
    
    # 3. 获取规则和判定清晰度
    rules = get_rules()
    clarity_rules = rules.get("clarity", {})
    
    # 规则判定清晰度
    rule_clarity = judge_text_clarity(normalized, clarity_rules)
    
    # 分类器预测清晰度
    clf_clarity, clf_conf = predict_clarity(normalized)
    
    # 优先使用分类器结果（如果置信度够高）
    if clf_conf >= 0.7:
        clarity = clf_clarity
        clarity_conf = clf_conf
    else:
        clarity = rule_clarity
        clarity_conf = 0.7 if rule_clarity == "清晰" else 0.5
    
    logger.info(f"清晰度判定: {clarity} (置信度: {clarity_conf})")
    
    # 4. 历史窗口获取
    history = get_history_window(3)
    
    # 5. 模式判定
    from orchestration.mode_router import judge_work_mode, get_mode_reason
    mode = judge_work_mode(normalized, clarity, clarity_conf, history)
    mode_reason = get_mode_reason(mode, clarity, clarity_conf)
    logger.info(f"模式判定: {mode} - {mode_reason}")
    
    # 6. 记录模式切换
    save_mode_switch("", mode, mode_reason)
    
    # 7. 执行对应子流程
    if mode == "audit":
        result = audit_mode_workflow(normalized, dialogue_id)
    else:
        result = translate_mode_workflow(normalized, dialogue_id)
    
    # 8. 添加元信息
    result["dialogue_id"] = dialogue_id
    result["timestamp"] = datetime.now().isoformat()
    result["normalized_input"] = normalized
    
    logger.info(f"工作流完成，输出模式: {result.get('mode')}")
    return result

# 测试调度器
def test_dispatcher():
    """简单测试"""
    test_inputs = [
        "帮我写一个Python函数",
        "你觉得这个怎么样",
        "好",
    ]
    
    for inp in test_inputs:
        print(f"\n{'='*40}")
        print(f"输入: {inp}")
        result = main_workflow(inp)
        print(f"模式: {result.get('mode')}")
        if result.get('mode') == 'audit':
            print(f"姿态: {result.get('posture')}")
            print(f"提醒: {result.get('remind')[:50]}...")
        else:
            print(f"润色结果: {result.get('polished', '')[:50]}...")
        print(f"置信度: {result.get('confidence')}")

if __name__ == "__main__":
    test_dispatcher()
