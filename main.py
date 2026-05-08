#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认知姿态守护者 v3.1
主入口文件 - 修复版
"""
import sys
import os
import warnings

warnings.filterwarnings("ignore")

# 设置编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger, setup_logger, set_console_logging
from storage.db import init_database
from rules.rule_loader import load_all_rules
from orchestration.dispatcher_with_reflection import main_workflow

logger = None

def init_all_modules(silent: bool = False):
    """初始化所有模块"""
    global logger
    
    print("=" * 50)
    print("认知姿态守护者 v3.1")
    print("=" * 50)
    
    # 1. 初始化日志（静默模式，不输出到控制台）
    print("[1/4] 初始化...")
    setup_logger(console_output=False)  # 关闭控制台日志
    logger = get_logger("main")
    
    # 2. 加载配置
    print("[2/4] 加载配置...")
    from utils.config_loader import load_config
    load_config()
    
    # 3. 初始化数据库
    print("[3/4] 初始化数据库...")
    init_database()
    
    # 4. 加载规则
    print("[4/4] 加载规则库...")
    load_all_rules()
    
    print("=" * 50)
    print("✅ 初始化完成！")
    print("=" * 50)

def single_turn_process(user_input: str) -> dict:
    """单轮对话处理"""
    if not user_input or not user_input.strip():
        return {"error": "输入为空", "mode": "error", "message": "请输入有效内容"}
    
    try:
        return main_workflow(user_input)
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return {"error": str(e), "mode": "error", "message": "处理过程中出现错误"}

def cli_interactive_mode():
    """交互模式"""
    print("\n" + "=" * 50)
    print("交互模式")
    print("输入 'exit' 退出 | 输入 'help' 帮助")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n[你]: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n再见！👋")
                break
            
            if user_input.lower() == 'help':
                print("\n帮助:")
                print("  直接输入文字进行分析")
                print("  示例: 帮我写一个Python函数")
                continue
            
            if not user_input:
                continue
            
            print("\n[守护者] 分析中...")
            result = single_turn_process(user_input)
            
            mode = result.get("mode", "unknown")
            
            if mode == "audit":
                print(f"\n[审计模式]")
                print(f"  姿态: {result.get('posture', '未知')}")
                print(f"  置信度: {result.get('confidence', 0):.2f}")
                print(f"\n  {result.get('remind', '')}")
            elif mode == "translate":
                print(f"\n[翻译模式]")
                final_output = result.get('final_output', result.get('polished', ''))
                print(f"  {final_output}")
            elif mode == "error":
                print(f"\n❌ 错误: {result.get('message', '未知')}")
            else:
                print(f"\n{result}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n再见！👋")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")

def main():
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    init_all_modules()
    cli_interactive_mode()

if __name__ == "__main__":
    main()
