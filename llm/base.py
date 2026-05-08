"""
小模型推理封装模块 - 静默版
"""
import os
from typing import Optional

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

_model = None

MODEL_DIR = "models"
MODEL_FILE = "TheBloke_phi-2-GGUF_phi-2.Q4_K_M.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

def load_quantized_model(model_path: str = None, n_ctx: int = 2048) -> Optional[object]:
    global _model
    
    if not LLAMA_AVAILABLE:
        return None
    
    path = model_path or MODEL_PATH
    
    if not os.path.exists(path):
        return None
    
    try:
        _model = Llama(
            model_path=path,
            n_ctx=n_ctx,
            n_threads=os.cpu_count(),
            verbose=False
        )
        return _model
    except Exception:
        return None

def get_model() -> Optional[object]:
    global _model
    if _model is None:
        load_quantized_model()
    return _model

def build_system_prompt(mode_type: str) -> str:
    prompts = {
        "audit": "你是一个认知姿态分析助手。",
        "translate": "你是一个文本润色助手。",
        "self_reflection": "你是一个质量检查助手。"
    }
    return prompts.get(mode_type, prompts["audit"])

def model_generate(model: object, prompt: str, temperature: float = 0.1, max_tokens: int = 512) -> str:
    if model is None:
        return ""
    
    try:
        response = model(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=["\n\n", "用户：", "User:"],
            echo=False
        )
        return response["choices"][0]["text"].strip()
    except Exception:
        return ""

def switch_model_profile(profile_name: str) -> Optional[object]:
    global _model
    profile_map = {"none": None, "tiny": None, "small": MODEL_PATH, "medium": None}
    model_path = profile_map.get(profile_name, MODEL_PATH)
    
    if model_path is None:
        _model = None
        return None
    
    return load_quantized_model(model_path)
