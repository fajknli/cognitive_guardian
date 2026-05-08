"""
分类器训练脚本
构建姿态和清晰度分类器
"""
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from typing import List, Tuple

# 模型保存路径
MODEL_DIR = "classifiers/models"
os.makedirs(MODEL_DIR, exist_ok=True)

def build_posture_dataset() -> Tuple[List[str], List[str]]:
    """
    构建姿态训练数据集
    返回: (文本列表, 标签列表)
    """
    texts = []
    labels = []
    
    # 探索性姿态样本
    exploration_samples = [
        ("你觉得这个方案怎么样", "探索性姿态"),
        ("你怎么看待这个问题", "探索性姿态"),
        ("我想知道为什么", "探索性姿态"),
        ("能解释一下原理吗", "探索性姿态"),
        ("有什么好的建议", "探索性姿态"),
        ("这个问题怎么理解", "探索性姿态"),
        ("你的看法是什么", "探索性姿态"),
    ]
    
    # 执行性姿态样本
    execution_samples = [
        ("帮我写一个函数", "执行性姿态"),
        ("怎么做这个功能", "执行性姿态"),
        ("实现一个登录接口", "执行性姿态"),
        ("写代码完成任务", "执行性姿态"),
        ("部署到服务器", "执行性姿态"),
        ("帮我修改这段代码", "执行性姿态"),
        ("执行这个操作", "执行性姿态"),
    ]
    
    # 评价性姿态样本
    evaluation_samples = [
        ("评价一下这个方案", "评价性姿态"),
        ("分析优缺点", "评价性姿态"),
        ("对比这两个方法", "评价性姿态"),
        ("这个做得好不好", "评价性姿态"),
        ("值得采用吗", "评价性姿态"),
        ("点评一下我的代码", "评价性姿态"),
        ("评估一下风险", "评价性姿态"),
    ]
    
    # 情感性姿态样本
    emotional_samples = [
        ("我今天心情不好", "情感性姿态"),
        ("太开心了", "情感性姿态"),
        ("感觉很郁闷", "情感性姿态"),
        ("有点烦躁", "情感性姿态"),
        ("好激动啊", "情感性姿态"),
        ("很失望", "情感性姿态"),
        ("有点担心", "情感性姿态"),
    ]
    
    # 合并数据
    for text, label in exploration_samples:
        texts.append(text)
        labels.append(label)
    for text, label in execution_samples:
        texts.append(text)
        labels.append(label)
    for text, label in evaluation_samples:
        texts.append(text)
        labels.append(label)
    for text, label in emotional_samples:
        texts.append(text)
        labels.append(label)
    
    return texts, labels

def build_clarity_dataset() -> Tuple[List[str], List[str]]:
    """
    构建清晰度训练数据集
    返回: (文本列表, 标签列表)
    """
    texts = []
    labels = []
    
    # 清晰样本
    clear_samples = [
        ("因为今天下雨，所以我带了伞", "清晰"),
        ("首先打开文件，然后读取内容", "清晰"),
        ("具体步骤如下：第一步安装，第二步配置", "清晰"),
        ("明确地说，我需要一个排序算法", "清晰"),
        ("请帮我实现一个计算器功能", "清晰"),
        ("我想知道这个问题的正确答案", "清晰"),
        ("这个代码有三个问题需要修复", "清晰"),
    ]
    
    # 模糊样本
    vague_samples = [
        ("随便吧", "模糊"),
        ("大概可能也许", "模糊"),
        ("不知道怎么说", "模糊"),
        ("好像有点问题", "模糊"),
        ("随便什么都行", "模糊"),
        ("说不清楚", "模糊"),
        ("大概就是这个意思", "模糊"),
    ]
    
    for text, label in clear_samples:
        texts.append(text)
        labels.append(label)
    for text, label in vague_samples:
        texts.append(text)
        labels.append(label)
    
    return texts, labels

def train_posture_classifier():
    """
    训练姿态分类器
    """
    print("开始训练姿态分类器...")
    
    # 获取数据
    texts, labels = build_posture_dataset()
    print(f"  样本数量: {len(texts)}")
    print(f"  标签分布: {set(labels)}")
    
    # 创建Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    
    # 训练
    pipeline.fit(texts, labels)
    
    # 保存模型
    model_path = os.path.join(MODEL_DIR, 'posture_model.pkl')
    joblib.dump(pipeline, model_path)
    print(f"  模型已保存: {model_path}")
    
    # 简单验证
    test_texts = ["帮我写代码", "你觉得怎么样", "我很开心"]
    for text in test_texts:
        pred = pipeline.predict([text])[0]
        print(f"    测试: '{text}' -> {pred}")
    
    return pipeline

def train_clarity_classifier():
    """
    训练清晰度分类器
    """
    print("\n开始训练清晰度分类器...")
    
    # 获取数据
    texts, labels = build_clarity_dataset()
    print(f"  样本数量: {len(texts)}")
    print(f"  标签分布: {set(labels)}")
    
    # 创建Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    
    # 训练
    pipeline.fit(texts, labels)
    
    # 保存模型
    model_path = os.path.join(MODEL_DIR, 'clarity_model.pkl')
    joblib.dump(pipeline, model_path)
    print(f"  模型已保存: {model_path}")
    
    # 简单验证
    test_texts = ["因为所以具体明确", "好", "大概可能"]
    for text in test_texts:
        pred = pipeline.predict([text])[0]
        print(f"    测试: '{text}' -> {pred}")
    
    return pipeline

def train_all_classifiers():
    """
    批量训练所有分类器
    """
    print("=" * 40)
    print("开始训练所有分类器")
    print("=" * 40)
    
    posture_model = train_posture_classifier()
    clarity_model = train_clarity_classifier()
    
    print("\n" + "=" * 40)
    print("所有分类器训练完成！")
    print("=" * 40)
    
    return posture_model, clarity_model

if __name__ == "__main__":
    train_all_classifiers()
