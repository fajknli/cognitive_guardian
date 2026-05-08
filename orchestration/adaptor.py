"""
档位自适应模块
根据系统资源自动调整模型档位
"""
import os
import platform

# 模型档位定义
PROFILE_NONE = "none"      # 无模型
PROFILE_TINY = "tiny"      # 最小模型 (~250MB)
PROFILE_SMALL = "small"    # 小模型 (~650MB)
PROFILE_MEDIUM = "medium"  # 中模型 (~800MB)

def get_system_resource() -> dict:
    """
    获取本地CPU、内存占用信息
    """
    resources = {
        "cpu_count": os.cpu_count() or 1,
        "platform": platform.system(),
        "memory_gb": 4,  # 默认值
        "available_memory_gb": 2  # 默认值
    }
    
    # 尝试获取内存信息 (Linux)
    if platform.system() == "Linux":
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        mem_kb = int(line.split()[1])
                        resources["memory_gb"] = mem_kb / (1024 * 1024)
                    elif "MemAvailable" in line:
                        avail_kb = int(line.split()[1])
                        resources["available_memory_gb"] = avail_kb / (1024 * 1024)
        except:
            pass
    
    return resources

def auto_adjust_model_profile() -> str:
    """
    根据系统资源自动切换模型档位
    
    规则：
    - 内存 < 2GB -> none (无模型)
    - 内存 2-4GB -> tiny
    - 内存 4-8GB -> small
    - 内存 >= 8GB -> medium
    """
    resources = get_system_resource()
    memory_gb = resources.get("memory_gb", 4)
    
    print(f"系统资源检测: {memory_gb:.1f}GB 内存, {resources['cpu_count']} 核CPU")
    
    if memory_gb < 2:
        profile = PROFILE_NONE
        print(f"内存不足({memory_gb:.1f}GB)，切换到无模型模式")
    elif memory_gb < 4:
        profile = PROFILE_TINY
        print(f"内存适中({memory_gb:.1f}GB)，切换到tiny模型档位")
    elif memory_gb < 8:
        profile = PROFILE_SMALL
        print(f"内存充足({memory_gb:.1f}GB)，切换到small模型档位")
    else:
        profile = PROFILE_MEDIUM
        print(f"内存充裕({memory_gb:.1f}GB)，切换到medium模型档位")
    
    return profile

def get_recommended_profile() -> str:
    """
    获取推荐的模型档位（不自动切换）
    """
    resources = get_system_resource()
    memory_gb = resources.get("memory_gb", 4)
    
    if memory_gb < 2:
        return PROFILE_NONE
    elif memory_gb < 4:
        return PROFILE_TINY
    elif memory_gb < 8:
        return PROFILE_SMALL
    else:
        return PROFILE_MEDIUM
