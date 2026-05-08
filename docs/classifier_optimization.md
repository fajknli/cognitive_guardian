# 分类器优化指南

## 一、当前状态

| 分类器 | 样本数 | 准确率 | 状态 |
|--------|--------|--------|------|
| 姿态分类器 | 28条 | 约60% | 待提升 |
| 清晰度分类器 | 14条 | 约70% | 待提升 |

## 二、扩充训练数据

### 2.1 姿态数据扩充模板

在 `classifiers/train.py` 的 `build_posture_dataset()` 函数中添加：

```python
# 新增执行性姿态样本
execution_samples = [
    ("帮我写一个快速排序", "执行性姿态"),
    ("这个bug怎么修复", "执行性姿态"),
    ("实现用户登录功能", "执行性姿态"),
    # 继续添加...
]

# 新增探索性姿态样本
exploration_samples = [
    ("为什么会这样", "探索性姿态"),
    ("能解释一下原理吗", "探索性姿态"),
    ("有什么更好的方法", "探索性姿态"),
    # 继续添加...
]
```

### 2.2 推荐样本数量
- 每种姿态至少50-100条
- 覆盖不同长度和复杂度
- 包含口语和书面语

### 2.3 数据来源建议
1. 历史对话记录（logs/目录）
2. 公开语料库
3. 人工构造

## 三、重新训练

```bash
cd ~/Project/Python/cognitive_guardian
source .venv/bin/activate
python3 classifiers/train.py
```

## 四、评估方法

```python
from sklearn.model_selection import cross_val_score
from classifiers.train import build_posture_dataset

X, y = build_posture_dataset()
# 进行交叉验证评估
```

## 五、参数调优

### 5.1 TF-IDF参数
```python
TfidfVectorizer(
    max_features=2000,    # 增加特征数
    ngram_range=(1, 3),   # 支持3-gram
    min_df=2,             # 忽略低频词
    max_df=0.9            # 忽略高频词
)
```

### 5.2 分类器参数
```python
LogisticRegression(
    C=1.0,                # 正则化强度
    max_iter=2000,        # 增加迭代
    class_weight='balanced' # 处理样本不平衡
)
```
