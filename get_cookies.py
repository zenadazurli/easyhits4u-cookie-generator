#!/usr/bin/env python3
# get_cookies.py - Chiavi hardcodate (come easyhits4u-login-complete)

import requests
import json
import time
import os
import pickle
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== CHIAVI FUNZIONANTI (HARDCODATE) ====================
VALID_KEYS = [
    "2UKnWYAI4XjhlTbcc2b8d6928494d4a5f5542a74d00c06124",
    "2UKnXObX8RYBJ295ef966bc0a2342b47bba9e9e07f267d129",
    "2UKnZUgK5OICl9Tc02c85cc0d4272328dbb2f69636e31e49f",
    "2UKnbvt91chXu5k4eeaf9dac4dec56392775bfc3d0f2bf5b0",
    "2UKnex0F79iSOfgc76b35051414ec0c29974df1b6273bb037",
    "2UKnoI5dfbaqB5W71071e88ff897ee16f5c09566cac51043f",
    "2UKnwp0jDBj6L394f1f5d6b3b9be3db83ff2b75f359479b99",
    "2UKnxh5NTuseSDqf61c86934ec2bc68cdec73d44fdccce106",
    "2UKnzzEOtKeedO830957353ce0de6a17c94ce2f5b684463e9",
    "2UKo1s5wjiBFm1kbc0cdca7b0264e264470bcf92167a8d8b3",
    "2UKo2MAf1hz67Pma6ae81ea276974e4abd1d5c6049fe30562",
    "2UKo41T4eBxMroO972f754c66c5c24a4115fc8bf8e73cb163",
    "2UKo53fcth6cQbX24ba80659d5397546d67080ff7977b0719",
    "2UKo7MFmnuhLQBl2fb827baa83359d5c509e765c052fbe563",
    "2UKo8NOjaRRABF829743dddff0d99b3d7e4d6f1bdf47a6b1e",
    "2UKoJa4UH2qXOE82abaef4a28adf70bbf170d1806e513255f",
    "2UKoKWRM3NqPnvR4927430b0917be86ca0d88f5d33c83863d",
    "2UKoRweE2WuHvB00fccb9dcf28457f9ed811b6db1d409656f",
]

# ==================== CONFIGURAZIONE ====================
EASYHITS_EMAIL = "sandrominori50+uiszuzoqatr@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"
BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

OUTPUT_DIR = "/tmp/easyhits4u"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== SERVER HTTP ====================
PORT = int(os.environ.get("PORT", 10000))

class CookieHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/cookies':
            try:
                latest_path = os.path.join(OUTPUT_DIR, "cookies_latest.txt")
                if os.path.exists(latest_path):
                    with open(latest_path, "r") as f:
                        cookie_string = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(cookie_string.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Cookie file not found yet")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def start_http_server():
    server = HTTPServer(('0.0.0.0', PORT), CookieHandler)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Server HTTP avviato sulla porta {PORT}")
    server.serve_forever()

threading.Thread(target=start_http_server, daemon=True).start()
time.sleep(1)

# ==================== FUNZIONI LOGIN ====================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_cf_token(api_key):
    query = """
    mutation {
      goto(url: "https://www.easyhits4u.com/logon/", waitUntil: networkIdle, timeout: 60000) {
        status
      }
      solve(type: cloudflare, timeout: 60000) {
        solved
        token
        time
      }
    }
    """
    url = f"{BROWSERLESS_URL}?token={api_key}"
    try:
        start = time.time()
        response = requests.post(url, json={"query": query}, headers={"Content-Type": "application/json"}, timeout=120)
        if response.status_code != 200:
            return None
        data = response.json()
        if "errors" in data:
            return None
        solve_info = data.get("data", {}).get("solve", {})
        if solve_info.get("solved"):
            token = solve_info.get("token")
            log(f"   ✅ Token ({time.time()-start:.1f}s)")
            return token
        return None
    except Exception as e:
        log(f"   ❌ Errore token: {e}")
        return None

def build_cookie_string(cookies_dict):
    return '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

def login_and_get_cookies(api_key):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/148.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # GET homepage
    log("   🌐 GET homepage...")
    home = session.get("https://www.easyhits4u.com/", headers=headers, verify=False, timeout=15)
    log(f"      Homepage status: {home.status_code}")
    time.sleep(1)
    
    # Token
    token = get_cf_token(api_key)
    if not token:
        return None
    
    # POST login
    login_headers = headers.copy()
    login_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    login_headers['Referer'] = REFERER_URL
    data = {
        'manual': '1',
        'fb_id': '',
        'fb_token': '',
        'google_code': '',
        'username': EASYHITS_EMAIL,
        'password': EASYHITS_PASSWORD,
        'cf-turnstile-response': token,
    }
    login_resp = session.post("https://www.easyhits4u.com/logon/", data=data, headers=login_headers, allow_redirects=True, timeout=30)
    log(f"      Login POST status: {login_resp.status_code}")
    time.sleep(2)
    
    # GET /member/
    member = session.get("https://www.easyhits4u.com/member/", headers=headers, verify=False, timeout=15)
    log(f"      Member status: {member.status_code}")
    time.sleep(1)
    
    # GET /surf/
    surf = session.get("https://www.easyhits4u.com/surf/", headers=headers, verify=False, timeout=15)
    log(f"      Surf status: {surf.status_code}")
    time.sleep(1)
    
    # GET referer
    ref = session.get(REFERER_URL, headers=headers, verify=False, timeout=15)
    log(f"      Referer status: {ref.status_code}")
    
    cookies_dict = session.cookies.get_dict()
    log(f"   🍪 Cookie ricevuti: {list(cookies_dict.keys())}")
    
    if 'user_id' in cookies_dict and 'sesids' in cookies_dict:
        log(f"   ✅✅✅ SUCCESSO! user_id={cookies_dict['user_id']}, sesids={cookies_dict['sesids']}")
        cookie_string = build_cookie_string(cookies_dict)
        return cookies_dict, cookie_string, session
    else:
        log(f"   ❌ Login fallito: manca sesids")
        return None

def save_cookies(cookies_dict, cookie_string, session):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(os.path.join(OUTPUT_DIR, f"cookies_{timestamp}.json"), "w") as f:
        json.dump(cookies_dict, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, f"cookie_string_{timestamp}.txt"), "w") as f:
        f.write(cookie_string)
    with open(os.path.join(OUTPUT_DIR, "cookies_latest.txt"), "w") as f:
        f.write(cookie_string)
    with open(os.path.join(OUTPUT_DIR, f"session_{timestamp}.pkl"), "wb") as f:
        pickle.dump(session, f)
    with open(os.path.join(OUTPUT_DIR, "session_latest.pkl"), "wb") as f:
        pickle.dump(session, f)
    
    print("   💾 Cookie salvati")

def main():
    log("=" * 50)
    log("🚀 GENERATORE COOKIE (CHIAVI HARDCODATE)")
    log("=" * 50)
    log(f"🔑 Trovate {len(VALID_KEYS)} chiavi hardcodate")
    
    for i, api_key in enumerate(VALID_KEYS, 1):
        log(f"\n🔑 [{i}/{len(VALID_KEYS)}] Test: {api_key[:15]}...")
        result = login_and_get_cookies(api_key)
        if result is not None:
            cookies_dict, cookie_string, session = result
            if cookies_dict and cookie_string:
                log("🎉 SUCCESSO! Login riuscito!")
                save_cookies(cookies_dict, cookie_string, session)
                log(f"   🌐 curl http://localhost:{PORT}/cookies")
                while True:
                    time.sleep(60)
        else:
            log(f"   ❌ Fallito")
    
    log("❌ Nessuna chiave funzionante")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
