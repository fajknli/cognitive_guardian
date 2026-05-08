"""
分类器推理模块 - 静默版
"""
import os
import joblib
from typing import Tuple, Any

MODEL_DIR = "classifiers/models"
POSTURE_MODEL_PATH = os.path.join(MODEL_DIR, "posture_model.pkl")
CLARITY_MODEL_PATH = os.path.join(MODEL_DIR, "clarity_model.pkl")

_posture_model = None
_clarity_model = None

def load_posture_model() -> Any:
    global _posture_model
    if _posture_model is not None:
        return _posture_model
    
    try:
        if os.path.exists(POSTURE_MODEL_PATH):
            _posture_model = joblib.load(POSTURE_MODEL_PATH)
        else:
            _posture_model = None
    except Exception:
        _posture_model = None
    return _posture_model

def load_clarity_model() -> Any:
    global _clarity_model
    if _clarity_model is not None:
        return _clarity_model
    
    try:
        if os.path.exists(CLARITY_MODEL_PATH):
            _clarity_model = joblib.load(CLARITY_MODEL_PATH)
        else:
            _clarity_model = None
    except Exception:
        _clarity_model = None
    return _clarity_model

def predict_posture(normalized_text: str) -> Tuple[str, float]:
    if not normalized_text:
        return ("混合姿态", 0.5)
    
    model = load_posture_model()
    if model is None:
        return ("混合姿态", 0.5)
    
    try:
        pred_proba = model.predict_proba([normalized_text])
        pred_label = model.predict([normalized_text])[0]
        confidence = max(pred_proba[0])
        return (pred_label, confidence)
    except Exception:
        return ("混合姿态", 0.5)

def predict_clarity(normalized_text: str) -> Tuple[str, float]:
    if not normalized_text:
        return ("模糊", 0.5)
    
    model = load_clarity_model()
    if model is None:
        return ("模糊", 0.5)
    
    try:
        pred_proba = model.predict_proba([normalized_text])
        pred_label = model.predict([normalized_text])[0]
        confidence = max(pred_proba[0])
        return (pred_label, confidence)
    except Exception:
        return ("模糊", 0.5)

def fusion_rule_classifier(rule_result: Tuple[str, float], classifier_result: Tuple[str, float]) -> Tuple[str, float]:
    rule_type, rule_conf = rule_result
    clf_type, clf_conf = classifier_result
    
    if clf_conf <= 0.6 and clf_type == "混合姿态":
        return (rule_type, rule_conf)
    
    if rule_conf <= 0.6:
        return (clf_type, clf_conf)
    
    final_conf = rule_conf * 0.6 + clf_conf * 0.4
    
    if rule_type == clf_type:
        return (rule_type, final_conf)
    
    if rule_conf > clf_conf:
        return (rule_type, final_conf)
    else:
        return (clf_type, final_conf)
