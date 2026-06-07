import requests, json, time, os, sys

API_KEY='***'
URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

CARDS = [
    ('salt', 'Dark minimalist illustration, a crystal glass of pure water with white salt crystals, dark navy background, soft cyan light, digital art, no text, no people'),
    ('crowd', 'Dark minimalist illustration, people standing together viewed from above, dark navy background, golden light silhouettes, digital art, no text'),
]

for name, prompt in CARDS:
    print(f'[{name}] generating (sync)...', flush=True)
    r = requests.post(URL, json={
        'model': 'wanx-v1',
        'input': {'prompt': prompt},
        'parameters': {'size': '1024*1024', 'n': 1, 'style': '<auto>'}
    }, headers={
        'Authorization': f'Bearer {API_KEY}',
    }, timeout=180)
    resp = r.json()
    print(f'[{name}] status: {r.status_code}', flush=True)
    if r.status_code == 200 and 'output' in resp:
        results = resp['output'].get('results', [])
        if results:
            url = results[0].get('url', '')
            if url:
                img = requests.get(url, timeout=60)
                p = f'static/images/{name}.png'
                with open(p, 'wb') as f:
                    f.write(img.content)
                print(f'[{name}] OK {os.path.getsize(p)//1024}KB', flush=True)
                continue
    print(f'[{name}] response: {json.dumps(resp, ensure_ascii=False)[:300]}', flush=True)

print('Done', flush=True)
