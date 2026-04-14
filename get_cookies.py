#!/usr/bin/env python3
# get_cookies.py - Prova TUTTE le chiavi da GitHub (senza filtri)

import requests
import json
import time
import os
import pickle
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== CONFIGURAZIONE ====================
KEYS_URL = "https://raw.githubusercontent.com/zenadazurli/easyhits4u-keys/refs/heads/main/chiavi.txt"

EASYHITS_EMAIL = "sandrominori50+uiszuzoqatr@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"
BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

OUTPUT_DIR = "/tmp/easyhits4u"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== CARICA TUTTE LE CHIAVI ====================
def load_all_keys():
    """Legge TUTTE le chiavi dal file, senza alcun filtro"""
    print(f"📥 Download da: {KEYS_URL}")
    try:
        response = requests.get(KEYS_URL, timeout=30)
        if response.status_code == 200:
            keys = [line.strip() for line in response.text.splitlines() if line.strip()]
            print(f"📁 Caricate {len(keys)} chiavi da GitHub (TUTTE)")
            # Mostra tutte le chiavi (prime 5 e ultime 5)
            if keys:
                print(f"   Prime 5: {[k[:15] for k in keys[:5]]}")
                if len(keys) > 10:
                    print(f"   Ultime 5: {[k[:15] for k in keys[-5:]]}")
            return keys
        else:
            print(f"❌ Errore download: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Errore: {e}")
        return []

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
    """Richiede il token a Browserless"""
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
            log(f"      ❌ HTTP {response.status_code}")
            return None
        
        data = response.json()
        if "errors" in data:
            log(f"      ❌ GraphQL error: {data['errors'][0].get('message', '')[:100]}")
            return None
        
        solve_info = data.get("data", {}).get("solve", {})
        if solve_info.get("solved"):
            token = solve_info.get("token")
            log(f"      ✅ Token ({time.time()-start:.1f}s)")
            return token
        else:
            log(f"      ❌ Token non ottenuto (solved=False)")
            return None
    except requests.exceptions.Timeout:
        log(f"      ❌ Timeout dopo 120s")
        return None
    except Exception as e:
        log(f"      ❌ Eccezione: {e}")
        return None

def build_cookie_string(cookies_dict):
    return '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

def login_and_get_cookies(api_key):
    """Tenta il login completo con una chiave"""
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/148.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    log("   🌐 GET homepage...")
    try:
        home = session.get("https://www.easyhits4u.com/", headers=headers, verify=False, timeout=15)
        log(f"      Homepage status: {home.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore homepage: {e}")
        return None, None, None
    
    log("   🔑 Richiedo token...")
    token = get_cf_token(api_key)
    if not token:
        return None, None, None
    
    log("   🌐 POST login...")
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
    try:
        login_resp = session.post("https://www.easyhits4u.com/logon/", data=data, headers=login_headers, allow_redirects=True, timeout=30)
        log(f"      Login POST status: {login_resp.status_code}")
        time.sleep(2)
    except Exception as e:
        log(f"      ❌ Errore POST login: {e}")
        return None, None, None
    
    log("   🌐 GET /member/...")
    try:
        member = session.get("https://www.easyhits4u.com/member/", headers=headers, verify=False, timeout=15)
        log(f"      Member status: {member.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore member: {e}")
        return None, None, None
    
    log("   🌐 GET /surf/...")
    try:
        surf = session.get("https://www.easyhits4u.com/surf/", headers=headers, verify=False, timeout=15)
        log(f"      Surf status: {surf.status_code}")
        time.sleep(1)
    except Exception as e:
        log(f"      ❌ Errore surf: {e}")
        return None, None, None
    
    log("   🌐 GET referer...")
    try:
        ref = session.get(REFERER_URL, headers=headers, verify=False, timeout=15)
        log(f"      Referer status: {ref.status_code}")
    except Exception as e:
        log(f"      ⚠️ Errore referer: {e}")
    
    cookies_dict = session.cookies.get_dict()
    log(f"   🍪 Cookie ricevuti: {list(cookies_dict.keys())}")
    
    if 'user_id' in cookies_dict and 'sesids' in cookies_dict:
        log(f"   ✅✅✅ LOGIN COMPLETO! user_id={cookies_dict['user_id']}, sesids={cookies_dict['sesids']}")
        cookie_string = build_cookie_string(cookies_dict)
        return cookies_dict, cookie_string, session
    else:
        log(f"   ❌ Login fallito: user_id={cookies_dict.get('user_id')}, sesids={cookies_dict.get('sesids')}")
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
    
    print("   💾 Cookie salvati localmente")

def main():
    log("=" * 50)
    log("🚀 GENERATORE COOKIE (TUTTE LE CHIAVI)")
    log("=" * 50)
    
    keys = load_all_keys()
    if not keys:
        log("❌ Nessuna chiave caricata")
        return
    
    log(f"🔑 Trovate {len(keys)} chiavi totali")
    
    for i, api_key in enumerate(keys, 1):
        log(f"\n🔑 [{i}/{len(keys)}] Test: {api_key[:15]}...")
        cookies_dict, cookie_string, session = login_and_get_cookies(api_key)
        if cookies_dict:
            log("🎉🎉🎉 SUCCESSO! Login riuscito!")
            save_cookies(cookies_dict, cookie_string, session)
            log("✅ Cookie salvati.")
            log(f"   🌐 curl http://localhost:{PORT}/cookies")
            # Rimane in esecuzione
            while True:
                time.sleep(60)
        else:
            log(f"   ❌ Fallito con questa chiave")
    
    log("❌ Nessuna chiave funzionante")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
