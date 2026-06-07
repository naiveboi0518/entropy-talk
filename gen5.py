import urllib.request, json, time, os, sys

# Read key from .key file
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.key'), 'r') as f:
    API_KEY = f.read().strip()

print(f'Key length: {len(API_KEY)}', flush=True)
