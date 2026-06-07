"""Entropy Talk - physics presentation with GLM follow-up Q&A"""
from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')

GLM_API_KEY = '9ebc049fa4714a1f81aecf3cb20e3263.XlikQJpFJDQo9tNv'
GLM_API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
GLM_MODEL = 'glm-4-plus'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def api_ask():
    """Zhipu GLM follow-up question API"""
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'please provide a question'}), 400

    import urllib.request

    system_prompt = (
        '你是一位特别会讲课的大学物理老师，专精热力学。'
        '学生正在学习"熵"的概念，现在有追问。你的风格：\n'
        '1. 说人话！像跟朋友聊天一样，别端着\n'
        '2. 先用大白话给直觉，再上公式——公式用LaTeX，$...$行内，$$...$$独立\n'
        '3. 多举生活例子，越接地气越好\n'
        '4. 偶尔吐槽、偶尔幽默，让学生觉得物理好玩\n'
        '5. 控制在200字以内，别啰嗦，一针见血\n'
        '6. 不要用"同学们好"开头'
    )

    payload = json.dumps({
        'model': GLM_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': question}
        ],
        'stream': False,
        'temperature': 0.7,
    }).encode()

    auth_header = 'Bearer ' + GLM_API_KEY
    req = urllib.request.Request(
        GLM_API_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': auth_header,
        },
        method='POST'
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        reply = result['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except urllib.request.HTTPError as e:
        err_body = e.read().decode()
        err_msg = 'API error (' + str(e.code) + '): ' + err_body[:200]
        return jsonify({'error': err_msg}), 502
    except Exception as e:
        return jsonify({'error': 'request failed: ' + str(e)}), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
