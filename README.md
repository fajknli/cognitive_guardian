<!--
  Author:       fajknli
  Email:        fajknli@gmail.com
  Created Time: 2026-05-08 20:29
-->

# 认知姿态守护者 v3.1

## 项目简介

认知姿态守护者是一个智能对话分析工具，用于识别用户的认知姿态类型，并根据文本清晰度自动切换工作模式，提供姿态提醒或文本润色服务。

## 功能特性

- 输入归一化：自动清洗脏数据、去除表情符号、合并重复词汇
- 姿态识别：识别探索性、执行性、评价性、情感性四种认知姿态
- 双模式切换：根据文本清晰度自动切换审计模式或翻译模式
- 文本润色：使用量化小模型对模糊文本进行润色优化
- 自反审计：对输出内容进行质量校验，生成备检察看
- 数据持久化：SQLite存储对话记录、姿态历史、审计日志
- 可视化统计：Web界面提供图表展示和实时统计
- 双界面支持：命令行界面(CLI)和Web界面

## 技术栈

| 组件 | 技术 |
|------|------|
| 运行环境 | Python 3.10+ |
| Web框架 | Flask |
| 机器学习 | scikit-learn |
| 大模型推理 | llama-cpp-python |
| 量化模型 | Phi-2 GGUF |
| 数据库 | SQLite3 |
| 前端图表 | Chart.js |

## 目录结构

```
cognitive_guardian/
├── main.py                 # CLI主入口
├── web_app.py              # Web服务入口
├── config.yaml             # 全局配置文件
├── requirements.txt        # Python依赖
├── start.sh                # CLI启动脚本
├── start_web.sh            # Web启动脚本
├── utils/                  # 工具模块
│   ├── logger.py           # 日志系统
│   ├── config_loader.py    # 配置加载
│   ├── text_normalizer.py  # 输入归一化
│   └── self_check.py       # 离线自检
├── rules/                  # 规则库
│   ├── posture_rules.json      # 姿态规则
│   ├── clarity_rules.json      # 清晰度规则
│   ├── remind_templates.json   # 提醒模板
│   ├── reflection_rules.json   # 审计规则
│   ├── rule_loader.py          # 规则加载
│   └── template_renderer.py    # 模板渲染
├── classifiers/            # 分类器
│   ├── train.py            # 训练脚本
│   ├── infer.py            # 推理模块
│   └── models/             # 训练好的模型
├── llm/                    # 大模型模块
│   └── base.py             # 模型加载与推理
├── storage/                # 存储模块
│   └── db.py               # 数据库操作
├── orchestration/          # 调度核心
│   ├── mode_router.py      # 模式路由
│   ├── adaptor.py          # 档位自适应
│   ├── dispatcher.py       # 核心调度
│   └── self_reflection.py  # 自反审计
├── models/                 # 量化模型文件存放目录
├── data/                   # SQLite数据库文件
├── logs/                   # 日志文件
├── reports/                # 离线报告
├── templates/              # Web前端模板
└── docs/                   # 项目文档
```

## 快速启动

### 环境准备

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 启动CLI界面

```bash
./start.sh
```

### 启动Web界面

```bash
./start_web.sh
```

浏览器访问 http://127.0.0.1:5000

## 使用示例

### 审计模式示例

输入: 帮我写一个Python函数

输出:
- 模式: 审计模式
- 姿态: 执行性姿态
- 置信度: 64%
- 提醒: 明确行动步骤，确认资源可行性后再执行

### 翻译模式示例

输入: 因为所以具体明确，请帮我润色这段文字

输出:
- 模式: 翻译模式
- 润色结果: 优化后的文本
- 自反审计: 质量校验备注

## 文档索引

| 文档 | 说明 |
|------|------|
| docs/QUICKSTART.md | 快速开始指南 |
| docs/CONFIGURATION.md | 配置参数说明 |
| docs/WEB_GUIDE.md | Web界面使用说明 |
| docs/API_REFERENCE.md | API接口文档 |
| docs/ARCHITECTURE.md | 系统架构说明 |
| docs/TROUBLESHOOTING.md | 常见问题排查 |
| docs/rule_optimization.md | 规则优化指南 |
| docs/classifier_optimization.md | 分类器优化指南 |
| docs/prompt_optimization.md | 提示词优化指南 |
| docs/CHANGELOG.md | 版本更新记录 |

## 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核以上 |
| 内存 | 4GB | 8GB以上 |
| 磁盘 | 3GB | 5GB以上 |
| 操作系统 | Linux/macOS/Windows WSL2 | Linux |

## 注意事项

1. 首次启动需要下载量化模型文件(约1.7GB)
2. 模型首次加载需要30-60秒
3. CLI界面建议安装rlwrap解决中文输入问题: `sudo pacman -S rlwrap`
4. 分类器当前训练样本较少，可通过扩充数据提升准确率

## 许可证

内部项目

## 版本

v3.1 - 架构封版版本
