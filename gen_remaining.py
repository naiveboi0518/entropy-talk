import urllib.request, json, time, os, sys

API_KEY = 'sk-721501cf022745c4b26c9a698ecabb82'
SUBMIT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')

CARDS = [
    ('salt', 'Dark minimalist illustration, a crystal clear glass of pure water with white salt crystals beside it on dark surface, dark navy background, soft cyan light, digital art, no text, no people, macro photography'),
    ('crowd', 'Dark minimalist illustration, a group of people standing together in formation viewed from above, dark navy background, soft golden light silhouettes, digital art, no text, minimalist'),
]

for name, prompt in CARDS:
    print(f'[{name}] Submitting...', flush=True)
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
    tid = json.loads(resp.read())['output']['task_id']
    print(f'[{name}] task={tid[:8]} polling...', flush=True)
    
    poll_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{tid}'
    found = False
    for i in range(60):
        time.sleep(5)
        preq = urllib.request.Request(poll_url, headers={'Authorization': f'Bearer {API_KEY}'})
        presp = urllib.request.urlopen(preq, timeout=30)
        pdata = json.loads(presp.read())
        st = pdata['output']['task_status']
        if st == 'SUCCEEDED':
            url = pdata['output']['results'][0]['url']
            img_req = urllib.request.Request(url)
            img_resp = urllib.request.urlopen(img_req, timeout=60)
            out = os.path.join(OUTPUT_DIR, f'{name}.png')
            with open(out, 'wb') as f:
                f.write(img_resp.read())
            print(f'[{name}] OK ({os.path.getsize(out)//1024}KB)', flush=True)
            found = True
            break
        elif st == 'FAILED':
            print(f'[{name}] FAILED: {pdata["output"].get("message","?")}', flush=True)
            break
        if i % 3 == 0:
            print('.', end='', flush=True)
    if not found:
        print(f'[{name}] TIMEOUT', flush=True)
    time.sleep(2)

print('Done', flush=True)
