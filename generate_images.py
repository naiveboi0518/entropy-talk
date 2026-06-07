"""Generate section images via DashScope Wanx API"""
import json
import urllib.request
import time
import os
import base64

API_KEY = 'sk-721501cf022745c4b26c9a698ecabb82'
SUBMIT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
RESULT_URL = 'https://dashscope.aliyuncs.com/api/v1/tasks/'
OUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')

# Image prompts - dark cinematic style matching the site aesthetic
PROMPTS = {
    'carnot': (
        'A vintage steam engine in a dark moody setting, warm orange glow from furnace, '
        'cold blue shadows, cinematic lighting, dramatic contrast, physics illustration style, '
        'no text, no watermark, dark background'
    ),
    'clausius': (
        'An antique scientific notebook page with handwritten entropy equations, '
        'quill pen, warm candlelight, dark wood desk, dramatic chiaroscuro, '
        'physics concept art, no text overlay, dark moody atmosphere'
    ),
    'boltzmann': (
        'Countless colorful particles scattered chaotically vs a few particles in perfect order, '
        'split composition, left side ordered blue particles right side chaotic rainbow particles, '
        'dark background, glowing particles, physics visualization, no text'
    ),
    'ice': (
        'A crystal clear ice cube sitting on a dark slate surface, tiny water droplets forming, '
        'subtle steam, dramatic rim lighting, deep blue and cyan tones, '
        'macro photography style, dark moody background, no text'
    ),
    'life': (
        'Abstract visualization of life fighting entropy, a glowing human silhouette '
        'absorbing golden low-entropy energy from a bright sun, dark chaotic particles '
        'emanating outward, dark background, cinematic, no text'
    ),
    'universe': (
        'The heat death of the universe, dim fading stars in an endless dark void, '
        'uniform faint red glow spreading across empty space, cosmic emptiness, '
        'melancholic atmosphere, dark cinematic, no text no watermark'
    ),
}

def submit_task(prompt, size='1024*1024'):
    payload = json.dumps({
        'model': 'wanx2.1-t2i-turbo',
        'input': {'prompt': prompt},
        'parameters': {
            'size': size,
            'n': 1,
            'style': '<auto>',
        }
    }).encode()

    req = urllib.request.Request(
        SUBMIT_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}',
            'X-DashScope-Async': 'enable',
        },
        method='POST'
    )

    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    task_id = result.get('output', {}).get('task_id')
    print(f"  Submitted task: {task_id}")
    return task_id

def poll_task(task_id, max_wait=120):
    url = RESULT_URL + task_id
    start = time.time()
    while time.time() - start < max_wait:
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {API_KEY}'},
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        status = result.get('output', {}).get('task_status', '')
        print(f"  Status: {status}")

        if status == 'SUCCEEDED':
            results = result.get('output', {}).get('results', [])
            if results:
                return results[0].get('url')
        elif status == 'FAILED':
            msg = result.get('output', {}).get('message', 'unknown error')
            print(f"  FAILED: {msg}")
            return None

        time.sleep(5)

    print("  Timeout waiting for task")
    return None

def download_image(url, filepath):
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=60)
    data = resp.read()
    with open(filepath, 'wb') as f:
        f.write(data)
    print(f"  Saved: {filepath} ({len(data)} bytes)")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Submit all tasks first
    tasks = {}
    for key, prompt in PROMPTS.items():
        print(f"\n[{key}] Submitting...")
        try:
            task_id = submit_task(prompt)
            tasks[key] = task_id
        except Exception as e:
            print(f"  Error submitting: {e}")

    # Poll and download
    for key, task_id in tasks.items():
        print(f"\n[{key}] Polling...")
        url = poll_task(task_id)
        if url:
            filepath = os.path.join(OUT_DIR, f'{key}.png')
            try:
                download_image(url, filepath)
            except Exception as e:
                print(f"  Download error: {e}")
        else:
            print(f"  No image for {key}")

    print("\n=== Done ===")
    # List generated files
    for f in os.listdir(OUT_DIR):
        fpath = os.path.join(OUT_DIR, f)
        print(f"  {fpath} ({os.path.getsize(fpath)} bytes)")

if __name__ == '__main__':
    main()
