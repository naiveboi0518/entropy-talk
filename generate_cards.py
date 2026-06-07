"""Generate 6 daily entropy card images via DashScope Wanx API"""
import urllib.request, json, time, os, sys

API_KEY='sk-721501cf022745c4b26c9a698ecabb82'
SUBMIT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')

CARDS = [
    ('headphone_before', 'Dark minimalist illustration, two small white wired in-ear earbuds separated, each with its own short cable, laid out side by side neatly, dark navy background, soft light, digital art, no text'),
    ('headphone_after', 'Dark minimalist illustration, the two small white wired earbuds with their cables tangled together into one big messy knot, dark navy background, dim light, digital art, no text'),
    ('fruit_before', 'Dark minimalist illustration, a fresh ripe apple and a fresh banana on a dark surface, vibrant colors, perfect condition, dark navy background, warm light, digital art, no text'),
    ('fruit_after', 'Dark minimalist illustration, the same apple and banana now rotten, apple has brown spots and shriveled skin, banana peel is black and mushy, mold visible, dark navy background, dim light, digital art, no text'),
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def submit(prompt):
    payload = json.dumps({
        'model': 'wanx-v1',
        'input': {'prompt': prompt},
        'parameters': {'size': '1024*1024', 'n': 1, 'style': '<auto>'}
    }).encode()
    req = urllib.request.Request(SUBMIT_URL, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'X-DashScope-Async': 'enable',
    }, method='POST')
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())['output']['task_id']

def poll(task_id, timeout=300):
    poll_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(5)
        req = urllib.request.Request(poll_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        status = data['output']['task_status']
        if status == 'SUCCEEDED':
            return data['output']['results'][0]['url']
        elif status == 'FAILED':
            raise Exception(data['output'].get('message', 'unknown failure'))
        sys.stdout.write('.')
        sys.stdout.flush()
    raise Exception('timeout')

def download(url, path):
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=30)
    with open(path, 'wb') as f:
        f.write(resp.read())

if __name__ == '__main__':
    ok = 0
    for name, prompt in CARDS:
        try:
            print(f'\n[{name}] Submitting...', end='', flush=True)
            tid = submit(prompt)
            print(f' task={tid[:8]}')
            print(f'[{name}] Polling...', end='', flush=True)
            url = poll(tid)
            out = os.path.join(OUTPUT_DIR, f'{name}.png')
            download(url, out)
            sz = os.path.getsize(out)
            print(f' OK ({sz//1024}KB)')
            ok += 1
            time.sleep(2)
        except Exception as e:
            print(f' FAILED: {e}')
    print(f'\nDone: {ok}/{len(CARDS)}')
