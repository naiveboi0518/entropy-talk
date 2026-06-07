"""Regenerate fruit_after and headphone_after with more obvious effects"""
import urllib.request, json, time, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE, '.key')
IMG_DIR = os.path.join(BASE, 'static', 'images')

with open(KEY_PATH, 'r') as f:
    API_KEY = f.read().strip()

SUBMIT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

CARDS = [
    ('fruit_after', 'Photorealistic, a rotten apple covered in green and white fuzzy mold patches, brown mushy spots, skin shriveled and peeling, next to a completely blackened mushy banana with white mold growing on it, on a dark wooden table, dramatic side lighting, highly detailed macro food photography style, dark background'),
    ('headphone_after', 'Photorealistic, two white wired in-ear earphones with their long white cables completely tangled together into one tight messy knot, the cables are intertwined and wrapped around each other multiple times forming a chaotic ball of wires, close-up product photo on dark surface, dramatic lighting, highly detailed'),
]

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
            out = os.path.join(IMG_DIR, f'{name}.png')
            download(url, out)
            sz = os.path.getsize(out)
            print(f' OK ({sz//1024}KB)')
            ok += 1
            time.sleep(2)
        except Exception as e:
            print(f' FAILED: {e}')
    print(f'\nDone: {ok}/{len(CARDS)}')
