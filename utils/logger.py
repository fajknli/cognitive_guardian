import sys
"""
日志工具模块 - 修复版
交互模式时不输出日志到控制台
"""
import logging
import os
from datetime import datetime

_loggers = {}
_log_dir = "logs"

# 是否开启控制台日志（交互模式时关闭）
_console_logging = True

def set_console_logging(enabled: bool):
    """设置是否输出日志到控制台"""
    global _console_logging
    _console_logging = enabled
    
    # 调整根日志器的控制台处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(logging.DEBUG if enabled else logging.ERROR)

def setup_logger(console_output: bool = True):
    """初始化全局日志系统"""
    global _console_logging
    _console_logging = console_output
    
    # 创建日志目录
    if not os.path.exists(_log_dir):
        os.makedirs(_log_dir)
    
    # 配置根日志器
    log_file = os.path.join(_log_dir, f"guardian_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（始终开启）
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 清除已有处理器
    root_logger.handlers.clear()
    
    # 添加文件处理器
    root_logger.addHandler(file_handler)
    
    # 添加控制台处理器（可选）
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
    
    logging.info("日志系统初始化完成")
    return root_logger

def get_logger(module_name):
    """获取模块日志器"""
    if module_name not in _loggers:
        _loggers[module_name] = logging.getLogger(module_name)
    return _loggers[module_name]
