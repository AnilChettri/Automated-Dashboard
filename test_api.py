import urllib.request
import json
import urllib.error

url = 'http://localhost:8000/api/chat/ask'
data = json.dumps({"query": "Show me total revenue"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as res:
        print(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
