#!/bin/bash
# 全方面测试脚本

cd ~/cognitive_guardian
source .venv/bin/activate
export PYTHONPATH=.

echo "=========================================="
echo "   认知姿态守护者 v3.1 - 全方面测试"
echo "=========================================="
echo ""

# 测试1：输入归一化
echo "[测试1] 输入归一化模块"
python3 -c "
from utils.text_normalizer import normalize_input
tests = [
    ('  你好  世界  ', '你好 世界'),
    ('你好，世界！', '你好,世界!'),
    ('那个那个那个不错', '那个不错'),
    ('@user 你好啊😀😀', 'user 你好啊'),
]
for inp, exp in tests:
    res = normalize_input(inp)
    status = '✓' if res == exp else '✗'
    print(f'  {status} {inp} -> {res}')
"

# 测试2：规则引擎
echo ""
echo "[测试2] 规则引擎"
python3 -c "
from rules.rule_loader import match_posture_type, judge_text_clarity, load_all_rules
rules = load_all_rules()
posture_rules = rules.get('posture', {})
clarity_rules = rules.get('clarity', {})

tests = [
    ('帮我写代码', '执行性姿态'),
    ('你觉得怎么样', '探索性姿态'),
    ('我很开心', '情感性姿态'),
]
for text, expected in tests:
    posture, conf = match_posture_type(text, posture_rules)
    status = '✓' if posture == expected else '✗'
    print(f'  {status} {text} -> {posture} (期望: {expected})')

clarity_tests = [
    ('因为所以具体明确', '清晰'),
    ('好', '模糊'),
]
for text, expected in clarity_tests:
    result = judge_text_clarity(text, clarity_rules)
    status = '✓' if result == expected else '✗'
    print(f'  {status} {text} -> {result} (期望: {expected})')
"

# 测试3：数据库
echo ""
echo "[测试3] 数据库模块"
python3 -c "
from storage.db import init_database, save_original_dialogue, get_history_window
init_database()
dialogue_id = save_original_dialogue('测试输入', '测试归一化')
print(f'  ✓ 保存对话成功, ID: {dialogue_id}')
history = get_history_window(3)
print(f'  ✓ 历史记录数: {len(history)}')
"

# 测试4：分类器
echo ""
echo "[测试4] 分类器模块"
python3 -c "
from classifiers.infer import predict_posture, predict_clarity
posture, conf = predict_posture('帮我写代码')
print(f'  ✓ 姿态预测: {posture} ({conf:.2f})')
clarity, conf = predict_clarity('因为所以具体明确')
print(f'  ✓ 清晰度预测: {clarity} ({conf:.2f})')
"

# 测试5：完整流程（多轮对话）
echo ""
echo "[测试5] 完整流程测试"
python3 << 'PYEOF'
from main import single_turn_process

test_cases = [
    ("帮我写一个Python函数", "audit"),
    ("你觉得这个方案怎么样", "audit"),
    ("我今天心情不好", "audit"),
]

for text, expected_mode in test_cases:
    result = single_turn_process(text)
    mode = result.get('mode')
    posture = result.get('posture', 'N/A')
    status = '✓' if mode == expected_mode else '✗'
    print(f'  {status} [{mode}] {text[:20]}... -> {posture}')
PYEOF

# 测试6：异常处理
echo ""
echo "[测试6] 异常处理"
python3 -c "
from main import single_turn_process
print(f'  ✓ 空输入: {single_turn_process("").get(\"mode\")}')
print(f'  ✓ None输入: {single_turn_process(None).get(\"mode\")}')
print(f'  ✓ 超长输入: {single_turn_process(\"a\"*1000).get(\"mode\")}')
"

# 测试7：自反审计
echo ""
echo "[测试7] 自反审计"
python3 -c "
from orchestration.self_reflection import run_full_reflection
tests = ['好', '可能需要考虑一下', '请帮我写一个完整的函数']
for text in tests:
    result = run_full_reflection(text)
    status = '✓' if result else '✗'
    print(f'  {status} {text} -> {len(result)}字符')
"

# 测试8：离线报告
echo ""
echo "[测试8] 离线自检报告"
python3 -c "
from utils.self_check import generate_daily_check_report
report = generate_daily_check_report()
lines = report.split('\n')
print(f'  ✓ 报告行数: {len(lines)}')
print(f'  ✓ 报告包含: {lines[0]}')
"

# 测试9：模型加载（可选）
echo ""
echo "[测试9] 模型加载"
python3 -c "
from llm.base import get_model
model = get_model()
status = '✓' if model else '⚠'
print(f'  {status} 模型状态: {\"已加载\" if model else \"未加载(降级模式)\"}')
"

# 测试10：模式路由
echo ""
echo "[测试10] 模式路由"
python3 -c "
from orchestration.mode_router import judge_work_mode, mode_hysteresis_switch
mode = judge_work_mode('测试', '清晰', 0.8)
print(f'  ✓ 清晰文本 -> {mode}')
mode = judge_work_mode('测试', '模糊', 0.4)
print(f'  ✓ 模糊文本 -> {mode}')
"

echo ""
echo "=========================================="
echo "   ✅ 全方面测试完成"
echo "=========================================="
