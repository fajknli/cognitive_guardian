"""
配置加载模块
负责读取和管理全局配置
"""
import yaml
import os
from typing import Any, Dict, Optional

_config = None

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    加载配置文件
    """
    global _config
    
    # 默认兜底配置
    default_config = {
        "logging": {"level": "INFO", "file": "logs/guardian.log"},
        "database": {"path": "data/guardian.db"},
        "models": {"default_profile": "small", "profiles": {}},
        "mode_hysteresis": {"window_size": 3, "switch_threshold": 2},
        "rules": {}
    }
    
    try:
        if not os.path.exists(config_path):
            print(f"配置文件 {config_path} 不存在，使用默认配置")
            _config = default_config
            return _config
        
        with open(config_path, 'r', encoding='utf-8') as f:
            _config = yaml.safe_load(f)
            print(f"配置文件加载成功: {config_path}")
            return _config
            
    except yaml.YAMLError as e:
        print(f"配置文件解析错误: {e}，使用默认配置")
        _config = default_config
        return _config
    except Exception as e:
        print(f"配置文件加载异常: {e}，使用默认配置")
        _config = default_config
        return _config

def get_config_value(key_path: str) -> Optional[Any]:
    """
    按路径获取配置值，支持点号分隔
    例如: get_config_value("database.path")
    """
    global _config
    
    if _config is None:
        load_config()
    
    keys = key_path.split('.')
    value = _config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return None

# 自动加载配置
load_config()
