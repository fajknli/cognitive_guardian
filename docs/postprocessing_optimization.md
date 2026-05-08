# 后处理优化指南

## 一、自反审计规则优化

### 当前规则位置
`orchestration/self_reflection.py`

### 优化维度

#### 1.1 歧义词列表扩充
```python
# 当前
AMBIGUOUS_WORDS = ["可能", "也许", "大概", "好像", "似乎", "有点儿", "稍微", "差不多"]

# 可扩充
AMBIGUOUS_WORDS = [
    "可能", "也许", "大概", "好像", "似乎", "有点儿", "稍微", "差不多",
    "差不多", "基本上", "大约", "左右", "上下", "一些", "某些",
    "sometimes", "maybe", "perhaps", "probably"
]
```

#### 1.2 执行性关键词扩充
```python
# 当前
EXECUTION_KEYWORDS = ["请", "帮忙", "写", "做", "实现", "创建", "生成", "提供", "给出", "建议"]

# 可扩充
EXECUTION_KEYWORDS = [
    "请", "帮忙", "写", "做", "实现", "创建", "生成", "提供", "给出", "建议",
    "修复", "修改", "删除", "添加", "配置", "部署", "运行", "执行", "调用",
    "封装", "重构", "优化", "测试", "验证", "检查"
]
```

#### 1.3 添加新审计维度

```python
def check_factual_accuracy(content: str) -> Tuple[bool, str]:
    """事实准确性检查"""
    # 检查是否存在明显事实错误
    pass

def check_format_compliance(content: str) -> Tuple[bool, str]:
    """格式规范检查"""
    # 检查输出格式是否符合要求
    pass
```

## 二、输入归一化优化

### 当前规则
`utils/text_normalizer.py`

### 优化方向

#### 2.1 添加更多清洗规则
```python
# 处理特殊符号
def _normalize_quotes(text: str) -> str:
    """统一引号格式"""
    pass

# 处理数字格式
def _normalize_numbers(text: str) -> str:
    """统一数字格式（中文数字转阿拉伯）"""
    pass
```

#### 2.2 正则优化
- 优化性能（编译正则）
- 增加边界条件处理
- 支持更多Unicode字符

## 三、置信度计算优化

### 当前融合公式
```python
final_conf = rule_conf * 0.6 + clf_conf * 0.4
```

### 可调参数
```python
# 动态权重
def adaptive_fusion(rule_conf, clf_conf, text_length):
    if text_length < 10:
        # 短文本更依赖规则
        return rule_conf * 0.8 + clf_conf * 0.2
    else:
        # 长文本更依赖分类器
        return rule_conf * 0.4 + clf_conf * 0.6
```
EOF

# 5. 调试和测试指南
cat > docs/debugging_guide.md << 'EOF'
# 调试和测试指南

## 一、快速测试命令

### 1.1 单元测试
```bash
# 测试输入归一化
python3 -c "from utils.text_normalizer import normalize_input; print(normalize_input('测试'))"

# 测试规则引擎
python3 -c "from rules.rule_loader import match_posture_type; print(match_posture_type('帮我写代码', {}))"

# 测试数据库
python3 -c "from storage.db import init_database; init_database()"
```

### 1.2 端到端测试
```bash
# 单轮测试
echo "帮我写一个Python函数" | python3 -c "
from main import single_turn_process
import sys
print(single_turn_process(sys.stdin.read().strip()))
"

# 批量测试
python3 test_phase5.py
```

### 1.3 API测试
```bash
# 测试聊天接口
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我写代码"}'
```

## 二、日志查看

### 2.1 实时日志
```bash
# 查看应用日志
tail -f logs/guardian_*.log

# 查看Web服务日志（如果后台运行）
tail -f web.log
```

### 2.2 日志级别调整
```python
# 在 config.yaml 中
logging:
  level: DEBUG  # INFO, DEBUG, WARNING, ERROR
```

## 三、性能分析

### 3.1 简单性能测试
```bash
# 测试响应时间
time echo "帮我写代码" | python3 -c "
from main import single_turn_process
import sys
single_turn_process(sys.stdin.read().strip())
"
```

### 3.2 内存监控
```bash
# 监控进程内存
ps aux | grep python3
```

## 四、常见问题排查

### 问题1：模型加载失败
```bash
# 检查模型文件
ls -la models/*.gguf

# 重新安装依赖
pip install llama-cpp-python --force-reinstall
```

### 问题2：中文输入乱码
```bash
# 安装 rlwrap
sudo pacman -S rlwrap

# 使用 rlwrap 启动
rlwrap python3 main.py
```

### 问题3：数据库锁定
```bash
# 检查数据库文件权限
ls -la data/guardian.db

# 手动修复
python3 -c "from storage.db import init_database; init_database()"
```

### 问题4：端口被占用
```bash
# 查看端口占用
lsof -i :5000

# 修改端口
# 编辑 web_app.py 最后一行的 port 参数
```
