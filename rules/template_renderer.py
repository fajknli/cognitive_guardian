"""
模板渲染模块
负责填充模板变量，生成固定文本
"""
from typing import Dict, List, Any

def render_fixed_template(template_key: str, params: Dict[str, str]) -> str:
    """
    填充模板变量，生成固定文本
    """
    if not template_key or not params:
        return ""
    
    # 简单模板渲染：替换 {{变量名}}
    result = template_key
    for key, value in params.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    
    return result

def get_remind_content(posture_type: str, template_list: Dict) -> str:
    """
    根据姿态类型获取对应提醒模板
    """
    if not template_list:
        return "请保持专注，继续您的表达。"
    
    templates = template_list.get("templates", {})
    
    # 精确匹配
    if posture_type in templates:
        template = templates[posture_type]
        return f"{template.get('title', '')}\n{template.get('content', '')}"
    
    # 降级到默认模板
    default_template = templates.get("default", {})
    return f"{default_template.get('title', '💡 认知提醒')}\n{default_template.get('content', '请更清晰地表达您的需求。')}"

def format_reflection_note(reflection_result: List[str]) -> str:
    """
    格式化自反审计备注内容
    """
    if not reflection_result:
        return "✅ 自反审计通过，输出符合规范"
    
    notes = []
    for item in reflection_result:
        if item == "意图完整性":
            notes.append("⚠️ 意图完整性不足：建议进一步确认用户的核心诉求")
        elif item == "歧义风险":
            notes.append("❓ 存在歧义风险：建议使用更明确的表述")
        elif item == "执行必要性":
            notes.append("📋 执行要素缺失：建议补充具体操作步骤")
        else:
            notes.append(f"📌 {item}: 需关注")
    
    return "\n".join(notes)

# 简单测试（运行时自动执行）
if __name__ == "__main__":
    # 测试提醒模板获取
    test_templates = {
        "templates": {
            "执行性姿态": {
                "title": "⚡ 测试标题",
                "content": "测试内容"
            },
            "default": {
                "title": "💡 默认",
                "content": "默认内容"
            }
        }
    }
    
    result = get_remind_content("执行性姿态", test_templates)
    print(f"提醒模板测试: {result[:30]}...")
    
    # 测试备注格式化
    notes = format_reflection_note(["意图完整性", "歧义风险"])
    print(f"备注格式化测试:\n{notes}")
