import requests, json, time, os, sys

API_KEY = 'sk-721501cf022745c4b26c9a698ecabb82'
URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

CARDS = [
    ('salt', 'Dark minimalist illustration, a crystal glass of pure water with salt crystals, dark navy background, soft cyan light, digital art, no text, no people'),
    ('crowd', 'Dark minimalist illustration, people standing together viewed from above, dark navy background, golden light silhouettes, digital art, no text'),
]

os.makedirs('static/images', exist_ok=True)

for name, prompt in CARDS:
    print(f'[{name}] submitting...', flush=True)
    r = requests.post(URL, json={
        'model': 'wanx-v1',
        'input': {'prompt': prompt},
        'parameters': {'size': '1024*1024', 'n': 1, 'style': '<auto>'}
    }, headers={
        'Authorization': f'Bearer {API_KEY}',
        'X-DashScope-Async': 'enable'
    })
    resp = r.json()
    if 'output' not in resp:
        print(f'[{name}] API error: {resp}', flush=True)
        continue
    tid = resp['output']['task_id']
    print(f'[{name}] {tid[:8]} polling...', flush=True)
    
    for i in range(60):
        time.sleep(5)
        pr = requests.get(
            f'https://dashscope.aliyuncs.com/api/v1/tasks/{tid}',
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        d = pr.json()['output']
        st = d['task_status']
        if st == 'SUCCEEDED':
            img = requests.get(d['results'][0]['url'], timeout=60)
            p = f'static/images/{name}.png'
            with open(p, 'wb') as f:
                f.write(img.content)
            print(f'[{name}] OK {os.path.getsize(p)//1024}KB', flush=True)
            break
        elif st == 'FAILED':
            print(f'[{name}] FAIL: {d.get("message", "?")}', flush=True)
            break
        if i % 3 == 0:
            print('.', end='', flush=True)
    time.sleep(2)

print('Done', flush=True)
