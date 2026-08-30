import requests
BASE_URL = "http://localhost:7875/api"
HEADERS = {
    "Authorization": "Token hEL327l1wBRNqnIxCW47UDwKQIsLKSy0:YICsgyH71f5TQ8qCIgliAXe0wGBJsqJW",
    "Accept": "application/json"
}

res = requests.get(f"{BASE_URL}/search?query=IPCAS", headers=HEADERS)
print("Search IPCAS:", res.json())
res = requests.get(f"{BASE_URL}/search?query=Velora", headers=HEADERS)
print("Search Velora:", res.json()['total'])

