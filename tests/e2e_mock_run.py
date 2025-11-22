import time
import requests

BASE = "http://localhost:8000"

payload = {
  "bpm": 90,
  "lyrics": "Hello world, sing along",
  "voice": {"type": "Male", "preset": "male_hindi_1"},
  "moods": ["Romantic"],
  "tracks": []
}

r = requests.post(f"{BASE}/api/generate/create", json=payload)
print("create status:", r.status_code, r.text)
job = r.json()["jobId"]

while True:
    s = requests.get(f"{BASE}/api/job/{job}/status").json()
    print(s["percent"], s["step"]) 
    if s["status"] in ["done","error"]:
        print("Finished:", s)
        break
    time.sleep(1)
