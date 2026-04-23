import urllib.request, json
try:
    url = 'https://bolls.life/api/v1/translations/'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for t in data:
            print(f"{t.get('short_name')}: {t.get('full_name')} ({t.get('language')})")
except Exception as e:
    print(f"Error: {e}")
