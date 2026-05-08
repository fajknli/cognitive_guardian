"""
核心调度模块（含自反审计）
"""
from typing import Dict
from datetime import datetime

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
from orchestration.self_reflection import run_full_reflection, format_reflection_output

logger = get_logger("dispatcher")

_rules_cache = None

def get_rules():
    global _rules_cache
    if _rules_cache is None:
        _rules_cache = load_all_rules()
    return _rules_cache

def calc_output_confidence(result_source: str) -> float:
    confidence_map = {
        "rule": 0.85,
        "classifier": 0.70,
        "fusion": 0.80,
        "fallback": 0.50,
        "model": 0.75
    }
    return confidence_map.get(result_source, 0.60)

def audit_mode_workflow(normalized_input: str, dialogue_id: int) -> Dict:
    logger.info(f"执行审计模式工作流: {normalized_input[:50]}")
    
    rules = get_rules()
    posture_rules = rules.get("posture", {})
    
    rule_posture, rule_conf = match_posture_type(normalized_input, posture_rules)
    clf_posture, clf_conf = predict_posture(normalized_input)
    final_posture, final_conf = fusion_rule_classifier(
        (rule_posture, rule_conf),
        (clf_posture, clf_conf)
    )
    
    save_posture_result(dialogue_id, final_posture, final_conf)
    
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
    logger.info(f"执行翻译模式工作流: {normalized_input[:50]}")
    
    polished_text = None
    source = "fallback"
    
    # 尝试使用模型润色
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
    
    if not polished_text:
        polished_text = normalized_input.strip()
        source = "fallback"
        logger.info("使用降级润色")
    
    # ===== 新增：自反审计 =====
    reflection_note = run_full_reflection(polished_text)
    save_reflection_result(dialogue_id, polished_text, reflection_note)
    logger.info(f"自反审计完成，备注长度: {len(reflection_note)}")
    
    # 格式化输出（带备注）
    final_output = format_reflection_output(reflection_note, polished_text)
    
    return {
        "mode": "translate",
        "original": normalized_input,
        "polished": polished_text,
        "reflection_note": reflection_note,
        "final_output": final_output,
        "source": source,
        "confidence": calc_output_confidence(source)
    }

def main_workflow(user_input: str) -> Dict:
    logger.info(f"收到用户输入: {user_input[:100]}")
    
    normalized = normalize_input(user_input)
    dialogue_id = save_original_dialogue(user_input, normalized)
    logger.info(f"对话已保存, ID: {dialogue_id}")
    
    rules = get_rules()
    clarity_rules = rules.get("clarity", {})
    
    rule_clarity = judge_text_clarity(normalized, clarity_rules)
    clf_clarity, clf_conf = predict_clarity(normalized)
    
    if clf_conf >= 0.7:
        clarity = clf_clarity
        clarity_conf = clf_conf
    else:
        clarity = rule_clarity
        clarity_conf = 0.7 if rule_clarity == "清晰" else 0.5
    
    logger.info(f"清晰度判定: {clarity} (置信度: {clarity_conf})")
    
    history = get_history_window(3)
    
    from orchestration.mode_router import judge_work_mode, get_mode_reason
    mode = judge_work_mode(normalized, clarity, clarity_conf, history)
    mode_reason = get_mode_reason(mode, clarity, clarity_conf)
    logger.info(f"模式判定: {mode} - {mode_reason}")
    
    save_mode_switch("", mode, mode_reason)
    
    if mode == "audit":
        result = audit_mode_workflow(normalized, dialogue_id)
    else:
        result = translate_mode_workflow(normalized, dialogue_id)
    
    result["dialogue_id"] = dialogue_id
    result["timestamp"] = datetime.now().isoformat()
    result["normalized_input"] = normalized
    
    logger.info(f"工作流完成，输出模式: {result.get('mode')}")
    return result

if __name__ == "__main__":
    # 测试翻译模式（需要清晰文本）
    test_inputs = ["因为所以具体明确，请帮我润色这段文字"]
    
    for inp in test_inputs:
        print(f"\n输入: {inp}")
        result = main_workflow(inp)
        print(f"模式: {result.get('mode')}")
        if result.get('mode') == 'translate':
            print(f"润色结果: {result.get('polished', '')[:100]}")
            print(f"自反备注: {result.get('reflection_note', '')[:100]}")
        print(f"置信度: {result.get('confidence')}")
