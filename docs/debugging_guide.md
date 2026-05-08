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
