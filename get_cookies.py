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
    "2TPBw78eoqITsdsc25e9ff6270092838010c06b1652627c8f",
    "2UB2mJ8Pu4KvAwya658a33c2af825bbe2f707870ba088d746",
    "2UB6xXPVzalwmFrdf68265d93b745fd095899467d21a32326",
    "2UB72G0jNe5RsxL6b2e845d0b94bb6897966e88f662bc99a7",
    "2UCe01EH3vUJLnP6d3f028660d770ed840a0c6b05b6dcf71e",
    "2UCyusO830dLAcyda29244c83c2bfa0217728908ff8810c42",
    "2UD3pQCcge39YhQce5797773c8508515a295a1298d0105b42",
    "2UDOf1dHJeNmeOl0a373211ade4280ba7e212cde93dfc9e20",
    "2UDOnpiBIFokFEBcb1017abfdd901756272f2ff182c4a9f32",
    "2UDPWeUf62vB2I8aa37152a5b515e5360c127d669b813f23c",
    # Aggiungi qui tutte le altre chiavi funzionanti
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
        return None, None, None
    
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
        return None, None, None

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
        if result:
            cookies_dict, cookie_string, session = result
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
