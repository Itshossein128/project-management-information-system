import urllib.request
import json

url = "https://quay.io/api/v1/repository/minio/minio/tag/"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    for t in data.get('tags', []):
        print(t['name'])
