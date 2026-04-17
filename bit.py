import time
import requests

url = "https://mangal-bhawan.onrender.com"

while True:
    try:
        r = requests.get(url)
        print(f"Pinged! Status: {r.status_code}")
    except Exception as e:
        print("Error:", e)

    time.sleep(180)  # 3 minutes