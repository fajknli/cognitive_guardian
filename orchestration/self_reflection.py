"""
自反审计模块
负责翻译模式输出的质量校验，生成侧边备注
"""
from typing import List, Dict, Tuple
from utils.logger import get_logger

logger = get_logger("self_reflection")

# 歧义词列表
AMBIGUOUS_WORDS = ["可能", "也许", "大概", "好像", "似乎", "有点儿", "稍微", "差不多"]

# 执行性关键词（表示有可执行内容）
EXECUTION_KEYWORDS = ["请", "帮忙", "写", "做", "实现", "创建", "生成", "提供", "给出", "建议"]

def check_intent_completeness(translate_content: str, rules: Dict = None) -> Tuple[bool, str]:
    """
    校验翻译结果意图完整性
    返回: (是否完整, 缺失说明)
    """
    if not translate_content:
        return False, "输出内容为空"
    
    # 简单规则：长度检查
    if len(translate_content) < 10:
        return False, "输出内容过短，可能未完整表达意图"
    
    # 检查是否包含不完整的句子标记
    incomplete_indicators = ["...", "等等", "等。", "略", "省略"]
    for indicator in incomplete_indicators:
        if indicator in translate_content:
            return False, f"输出包含不完整标记'{indicator}'"
    
    # 检查是否有明确的结尾
    if translate_content[-1] not in ['.', '！', '？', '。', '!', '?']:
        # 不是严格要求必须有标点，但给出提示
        pass
    
    return True, "意图完整"

def check_execution_necessity(translate_content: str, rules: Dict = None) -> List[str]:
    """
    校验执行要素是否缺失
    返回: 缺失要素列表
    """
    missing = []
    
    if not translate_content:
        return ["输出内容为空"]
    
    # 检查是否包含执行性关键词
    has_execution = any(kw in translate_content for kw in EXECUTION_KEYWORDS)
    
    # 如果内容较长但没有执行性关键词，可能缺少明确指令
    if len(translate_content) > 20 and not has_execution:
        missing.append("缺少明确的执行指令或行动建议")
    
    # 检查是否有步骤性内容（包含数字序号或连接词）
    has_steps = any(step in translate_content for step in ["1.", "2.", "首先", "然后", "接着", "最后"])
    if len(translate_content) > 50 and not has_steps:
        missing.append("建议补充具体步骤说明")
    
    return missing

def check_ambiguity_risk(translate_content: str) -> Tuple[bool, List[str]]:
    """
    校验是否存在歧义风险
    返回: (是否有风险, 风险列表)
    """
    risks = []
    
    if not translate_content:
        return True, ["输出内容为空"]
    
    # 检查歧义词
    ambiguous_found = []
    for word in AMBIGUOUS_WORDS:
        if word in translate_content:
            ambiguous_found.append(word)
    
    if ambiguous_found:
        risks.append(f"包含歧义词: {', '.join(ambiguous_found)}")
    
    # 检查过长的句子（可能结构混乱）
    sentences = translate_content.split('。')
    for i, sent in enumerate(sentences):
        if len(sent) > 80:
            risks.append(f"第{i+1}句较长({len(sent)}字)，可能存在结构歧义")
            break
    
    # 检查缺少主语的情况
    if translate_content and not any(char in translate_content for char in ["我", "你", "他", "她", "它", "我们", "你们", "他们"]):
        if len(translate_content) > 15:
            risks.append("缺少明确主语，可能产生指代歧义")
    
    return len(risks) > 0, risks

def run_full_reflection(translate_content: str) -> str:
    """
    自反审计总入口，串联三大维度校验
    返回: 格式化的侧边备注
    """
    logger.info(f"执行自反审计，内容长度: {len(translate_content)}")
    
    # 初始化结果
    issues = []
    
    # 1. 意图完整性校验
    is_complete, completeness_issue = check_intent_completeness(translate_content)
    if not is_complete:
        issues.append(f"⚠️ 意图完整性不足: {completeness_issue}")
    
    # 2. 执行必要性校验
    execution_missing = check_execution_necessity(translate_content)
    for missing in execution_missing:
        issues.append(f"📋 {missing}")
    
    # 3. 歧义风险校验
    has_risk, risks = check_ambiguity_risk(translate_content)
    if has_risk:
        for risk in risks:
            issues.append(f"❓ {risk}")
    
    # 格式化输出
    if not issues:
        return "✅ 自反审计通过\n输出质量良好，无显著问题"
    
    result = "📋 **自反审计备注**\n" + "\n".join(issues)
    return result

def format_reflection_output(reflection_note: str, original_output: str = "") -> str:
    """
    格式化自反审计输出，添加侧边备注格式
    """
    if not reflection_note:
        return ""
    
    # 如果原始输出存在，将备注附加在末尾
    if original_output:
        return f"{original_output}\n\n---\n{reflection_note}"
    
    return reflection_note

# 测试自反审计
if __name__ == "__main__":
    test_cases = [
        "这是一个很好的建议。",
        "可能你需要考虑一下这个问题。",
        "写一个Python函数来计算斐波那契数列。首先定义函数，然后实现循环。",
        "好。",
        "大概也许可能差不多这样吧。"
    ]
    
    print("=== 自反审计测试 ===\n")
    for i, test in enumerate(test_cases, 1):
        print(f"测试{i}: {test}")
        result = run_full_reflection(test)
        print(f"结果:\n{result}\n")
        print("-" * 40)
