#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认知姿态守护者 v3.1 - Web界面
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from utils.text_normalizer import normalize_input
from orchestration.dispatcher_with_reflection import main_workflow
from storage.db import get_history_window
from utils.self_check import stat_posture_accuracy, generate_daily_check_report

app = Flask(__name__)
CORS(app)

# 会话历史存储
session_history = []

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    data = request.get_json()
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({'error': '请输入内容'}), 400
    
    try:
        result = main_workflow(user_input)
        
        response = {
            'success': True,
            'mode': result.get('mode'),
            'input': user_input,
            'normalized': result.get('normalized_input', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        if result.get('mode') == 'audit':
            response['posture'] = result.get('posture')
            response['confidence'] = result.get('confidence')
            response['remind'] = result.get('remind')
        else:
            response['polished'] = result.get('polished')
            response['reflection_note'] = result.get('reflection_note')
            response['final_output'] = result.get('final_output')
        
        session_history.append({
            'user': user_input,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        while len(session_history) > 50:
            session_history.pop(0)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取会话历史"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({
        'history': session_history[-limit:],
        'total': len(session_history)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    try:
        posture_stats = stat_posture_accuracy()
        history = get_history_window(10)
        
        mode_counts = {'audit': 0, 'translate': 0}
        for item in session_history:
            mode = item.get('response', {}).get('mode')
            if mode in mode_counts:
                mode_counts[mode] += 1
        
        return jsonify({
            'posture_stats': posture_stats,
            'recent_count': len(history),
            'mode_counts': mode_counts,
            'session_count': len(session_history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['GET'])
def get_report():
    """获取离线报告"""
    try:
        report = generate_daily_check_report()
        return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """清除会话历史"""
    global session_history
    session_history = []
    return jsonify({'success': True, 'message': '历史已清除'})

if __name__ == '__main__':
    print("=" * 50)
    print("认知姿态守护者 v3.1 - Web界面")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 退出")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
