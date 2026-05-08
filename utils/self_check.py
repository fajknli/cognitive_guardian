"""
离线自检脚本
用于统计数据分析、误判分析、生成运行报告
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter

# 数据库路径
DB_PATH = "data/guardian.db"

def get_db_connection():
    """获取数据库连接"""
    if not os.path.exists(DB_PATH):
        return None
    return sqlite3.connect(DB_PATH)

def stat_posture_accuracy() -> Dict[str, Any]:
    """
    统计姿态判定分布
    返回: 姿态统计信息
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "数据库不存在", "total": 0}
    
    cursor = conn.cursor()
    
    # 统计各姿态出现次数
    cursor.execute('''
        SELECT posture_type, COUNT(*) as count, AVG(confidence) as avg_conf
        FROM postures
        GROUP BY posture_type
        ORDER BY count DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    stats = {
        "total": sum(row[1] for row in rows),
        "by_posture": [],
        "timestamp": datetime.now().isoformat()
    }
    
    for row in rows:
        stats["by_posture"].append({
            "posture": row[0],
            "count": row[1],
            "avg_confidence": round(row[2], 3) if row[2] else 0
        })
    
    return stats

def stat_mode_switch_frequency() -> Dict[str, Any]:
    """
    统计模式切换频率
    返回: 模式切换统计信息
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "数据库不存在", "total_switches": 0}
    
    cursor = conn.cursor()
    
    # 统计模式切换总数
    cursor.execute('SELECT COUNT(*) FROM mode_switches')
    total = cursor.fetchone()[0]
    
    # 统计最近7天的切换
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute('''
        SELECT COUNT(*) FROM mode_switches 
        WHERE created_at > ?
    ''', (seven_days_ago,))
    recent_7d = cursor.fetchone()[0]
    
    # 统计切换类型分布
    cursor.execute('''
        SELECT from_mode, to_mode, COUNT(*) as count
        FROM mode_switches
        GROUP BY from_mode, to_mode
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    transitions = []
    for row in cursor.fetchall():
        transitions.append({
            "from": row[0] or "start",
            "to": row[1],
            "count": row[2]
        })
    
    conn.close()
    
    return {
        "total_switches": total,
        "recent_7d": recent_7d,
        "avg_per_day": round(recent_7d / 7, 1) if recent_7d > 0 else 0,
        "top_transitions": transitions,
        "timestamp": datetime.now().isoformat()
    }

def stat_reflection_effectiveness() -> Dict[str, Any]:
    """
    统计自反审计有效率
    返回: 审计统计信息
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "数据库不存在", "total_reflections": 0}
    
    cursor = conn.cursor()
    
    # 统计自反审计总数
    cursor.execute('SELECT COUNT(*) FROM reflections')
    total = cursor.fetchone()[0]
    
    # 统计有备注的记录数（说明有问题）
    cursor.execute('''
        SELECT COUNT(*) FROM reflections 
        WHERE note IS NOT NULL AND note != ''
    ''')
    has_note = cursor.fetchone()[0]
    
    # 统计通过率（无备注的审计）
    pass_rate = (total - has_note) / total if total > 0 else 0
    
    # 获取最近的审计记录
    cursor.execute('''
        SELECT dialogue_id, note, created_at
        FROM reflections
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    
    recent = []
    for row in cursor.fetchall():
        recent.append({
            "dialogue_id": row[0],
            "note_preview": (row[1] or "")[:50],
            "created_at": row[2]
        })
    
    conn.close()
    
    return {
        "total_reflections": total,
        "has_note_count": has_note,
        "pass_rate": round(pass_rate * 100, 1),
        "issue_rate": round((has_note / total) * 100, 1) if total > 0 else 0,
        "recent_audits": recent,
        "timestamp": datetime.now().isoformat()
    }

def stat_daily_activity(days: int = 7) -> Dict[str, Any]:
    """
    统计每日活动情况
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "数据库不存在", "daily_stats": []}
    
    cursor = conn.cursor()
    
    # 统计每天对话数
    cursor.execute('''
        SELECT DATE(created_at), COUNT(*)
        FROM dialogues
        WHERE created_at > DATE('now', ?)
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at) DESC
    ''', (f'-{days} days',))
    
    daily = []
    for row in cursor.fetchall():
        daily.append({
            "date": row[0],
            "dialogues": row[1]
        })
    
    conn.close()
    
    return {
        "days": days,
        "daily_stats": daily,
        "total_dialogues": sum(d["dialogues"] for d in daily),
        "timestamp": datetime.now().isoformat()
    }

def generate_daily_check_report() -> str:
    """
    生成离线自检报告
    """
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("认知姿态守护者 - 离线自检报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60)
    
    # 1. 姿态统计
    posture_stats = stat_posture_accuracy()
    report_lines.append("\n【1. 认知姿态统计】")
    if "error" in posture_stats:
        report_lines.append(f"  错误: {posture_stats['error']}")
    else:
        report_lines.append(f"  总记录数: {posture_stats['total']}")
        for p in posture_stats["by_posture"]:
            report_lines.append(f"    - {p['posture']}: {p['count']}次 (平均置信度: {p['avg_confidence']})")
    
    # 2. 模式切换统计
    switch_stats = stat_mode_switch_frequency()
    report_lines.append("\n【2. 模式切换统计】")
    if "error" in switch_stats:
        report_lines.append(f"  错误: {switch_stats['error']}")
    else:
        report_lines.append(f"  总切换次数: {switch_stats['total_switches']}")
        report_lines.append(f"  最近7天: {switch_stats['recent_7d']}次 (日均: {switch_stats['avg_per_day']})")
        if switch_stats["top_transitions"]:
            report_lines.append("  主要切换路径:")
            for t in switch_stats["top_transitions"][:3]:
                report_lines.append(f"    - {t['from']} → {t['to']}: {t['count']}次")
    
    # 3. 自反审计统计
    reflection_stats = stat_reflection_effectiveness()
    report_lines.append("\n【3. 自反审计统计】")
    if "error" in reflection_stats:
        report_lines.append(f"  错误: {reflection_stats['error']}")
    else:
        report_lines.append(f"  审计次数: {reflection_stats['total_reflections']}")
        report_lines.append(f"  检出问题: {reflection_stats['has_note_count']}次")
        report_lines.append(f"  通过率: {reflection_stats['pass_rate']}%")
        report_lines.append(f"  问题率: {reflection_stats['issue_rate']}%")
    
    # 4. 活动统计
    activity_stats = stat_daily_activity(7)
    report_lines.append("\n【4. 近期活动统计】")
    if "error" in activity_stats:
        report_lines.append(f"  错误: {activity_stats['error']}")
    else:
        report_lines.append(f"  总对话数: {activity_stats['total_dialogues']}")
        report_lines.append("  每日对话:")
        for d in activity_stats["daily_stats"][:7]:
            report_lines.append(f"    - {d['date']}: {d['dialogues']}次")
    
    report_lines.append("\n" + "=" * 60)
    report_lines.append("报告生成完成")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)

def print_report():
    """打印报告到控制台"""
    report = generate_daily_check_report()
    print(report)
    
    # 同时保存到文件
    report_dir = "reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    report_file = os.path.join(report_dir, f"check_report_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存至: {report_file}")

if __name__ == "__main__":
    print_report()
