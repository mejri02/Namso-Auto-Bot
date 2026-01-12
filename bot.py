import requests
import json
import time
import sys
import uuid
import random
import threading
from datetime import datetime

# Vibrant Color Palette
class Col:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    C = '\033[96m'  # Cyan
    M = '\033[95m'  # Magenta
    W = '\033[97m'  # White
    B = '\033[94m'  # Blue
    RESET = '\033[0m'
    BOLD = '\033[1m'

FARM_INTERVAL = 60
CHECKIN_INTERVAL = 86400
MIN_SYNC_INTERVAL = 60
active_users = []
total_shares = 0.0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

def get_time():
    return datetime.now().strftime('%H:%M:%S')

def log_msg(color, tag, email, msg):
    masked = mask_email(email)
    print(f"{Col.W}[{get_time()}] {color}{Col.BOLD}[{tag.upper()}] {Col.RESET}{Col.W}{masked.ljust(20)} {Col.RESET}| {msg}")

def mask_email(email):
    if "@" in email:
        parts = email.split("@")
        return f"{parts[0][:3]}***@{parts[1]}"
    return email

def parse_proxy(proxy_str):
    if not proxy_str: return None
    proxy_str = proxy_str.strip()
    if proxy_str.startswith(('http', 'socks')): return proxy_str
    if ":" in proxy_str:
        parts = proxy_str.split(":")
        if len(parts) == 4:
            return f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        return f"socks5://{proxy_str}"
    return None

def perform_dashboard_login(email, password, proxy):
    session = requests.Session()
    if proxy:
        p_url = parse_proxy(proxy)
        session.proxies.update({'http': p_url, 'https': p_url})
    
    headers = {"accept": "application/json", "content-type": "application/json", "user-agent": random.choice(USER_AGENTS)}
    session.headers.update(headers)
    
    try:
        url_login = "https://app.namso.network/login.php"
        session.post(url_login, json={"email": email, "password": password, "action": "validate_credentials"})
        session.post(url_login, json={"email": email, "action": "send_otp"})
        
        print(f"    {Col.M}➜ OTP Sent to {mask_email(email)}{Col.RESET}")
        otp_code = input(f"    {Col.M}➜ Enter OTP: {Col.RESET}")
        
        res = session.post(url_login, json={"email": email, "password": password, "otp": otp_code, "action": "login"})
        data = res.json()
        if data.get("success") or data.get("status") == "success":
            return session, data.get('token')
    except:
        pass
    return None, None

def perform_extension_auth(email, password, proxy):
    url = "https://sentry-api.namso.network/devv/api/connectAuth"
    p_url = parse_proxy(proxy)
    proxies = {'http': p_url, 'https': p_url} if p_url else None
    try:
        res = requests.post(url, json={"email": email, "password": password}, proxies=proxies, timeout=15)
        if res.status_code == 200:
            return res.json().get("token")
    except:
        pass
    return None

def create_farming_session(token, proxy):
    s = requests.Session()
    if proxy:
        p_url = parse_proxy(proxy)
        s.proxies.update({'http': p_url, 'https': p_url})
    s.headers.update({
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "user-agent": random.choice(USER_AGENTS)
    })
    return s

def user_thread_loop(user):
    while True:
        now = time.time()
        
        # 1. Daily Check-in Logic
        if now >= user['next_checkin']:
            try:
                if user['session']:
                    res = user['session'].post("https://app.namso.network/dashboard/api.php/checkin")
                    msg = res.json().get("message", "Checked")
                    log_msg(Col.C, "DAILY", user['email'], f"{Col.G}{msg}")
            except:
                log_msg(Col.R, "DAILY", user['email'], "Failed check-in")
            user['next_checkin'] = now + CHECKIN_INTERVAL

        # 2. Optimized Farming (Fast & Smart)
        if now >= user['next_farm']:
            try:
                url_task = "https://sentry-api.namso.network/devv/api/taskSubmit"
                res = user['farm_session'].post(url_task, json={"email": user['email']}, timeout=15)
                
                if res.status_code == 200:
                    data = res.json()
                    if data.get('success'):
                        shares = data.get('shares', 0)
                        pts = data.get('points_today', 0)
                        log_msg(Col.G, "FARM", user['email'], f"SHARES: {Col.G}{shares} {Col.W}| PTS: {Col.Y}{pts}")
                        
                        # Sync perfectly with server timestamp
                        next_sync = data.get('next_sync')
                        wait_time = (next_sync - int(now)) if next_sync else MIN_SYNC_INTERVAL
                        # Added small random delay (3-7s) to prevent 'Too Frequent' errors
                        user['next_farm'] = now + max(wait_time, 5) + random.randint(3, 7)
                    else:
                        # Server limit detected: Wait 120s to reset
                        err = data.get('error', 'Sync too frequent')
                        user['next_farm'] = now + 120 
                        log_msg(Col.Y, "WAIT", user['email'], f"{Col.Y}{err} (Auto-reset in 120s)")
                elif res.status_code == 401:
                    log_msg(Col.R, "AUTH", user['email'], "Refreshing Token...")
                    new_token = perform_extension_auth(user['email'], user['password'], user['proxy'])
                    if new_token:
                        user['farm_session'] = create_farming_session(new_token, user['proxy'])
                    user['next_farm'] = now + 10
                else:
                    user['next_farm'] = now + 60
            except:
                user['next_farm'] = now + 30
        
        time.sleep(1)

def banner():
    print(f"""
{Col.C}╔═══════════════════════════════════════════════════════════╗
{Col.C}║ {Col.M}{Col.BOLD}   _  _   _   __  __  ___  ___    ___  ___  _____      {Col.C}║
{Col.C}║ {Col.M}{Col.BOLD}  | \| | /_\ |  \/  |/ __|/ _ \  | _ )/ _ \_   _|     {Col.C}║
{Col.C}║ {Col.M}{Col.BOLD}  | .` |/ _ \| |\/| |\__ \ (_) | | _ \ (_) || |       {Col.C}║
{Col.C}║ {Col.M}{Col.BOLD}  |_|\_/_/ \_\_|  |_||___/\___/  |___/\___/ |_|       {Col.C}║
{Col.C}║                                                           ║
{Col.C}║ {Col.W}      >> HIGH-SPEED MULTI-THREADED FARMING <<       {Col.C}║
{Col.C}╚═══════════════════════════════════════════════════════════╝{Col.RESET}
    """)

if __name__ == "__main__":
    banner()
    print(f"{Col.B}[1]{Col.W} Run With Proxy")
    print(f"{Col.B}[2]{Col.W} Run Without Proxy")
    choice = input(f"{Col.Y}Choice {Col.C}➜ {Col.RESET}")

    use_proxy = (choice == '1')
    try:
        raw_accs = [line.strip() for line in open("accounts.txt", 'r') if line.strip()]
    except FileNotFoundError:
        print(f"{Col.R}Error: accounts.txt not found!{Col.RESET}")
        sys.exit()

    raw_proxies = []
    if use_proxy:
        try:
            raw_proxies = [line.strip() for line in open("proxy.txt", 'r') if line.strip()]
        except FileNotFoundError:
            print(f"{Col.Y}Warning: proxy.txt not found!{Col.RESET}")

    ready_to_farm = []
    for i, line in enumerate(raw_accs):
        parts = line.split(':')
        if len(parts) >= 2:
            email, pwd = parts[0], parts[1]
            p = raw_proxies[i % len(raw_proxies)] if use_proxy and raw_proxies else None
            
            print(f"\n{Col.B}[Account {i+1}/{len(raw_accs)}] {Col.W}Login: {Col.G}{mask_email(email)}...")
            s_dash, t_dash = perform_dashboard_login(email, pwd, p)
            t_ext = perform_extension_auth(email, pwd, p)
            
            final_token = t_dash if t_dash else t_ext
            if final_token:
                ready_to_farm.append({
                    "email": email, "password": pwd, "proxy": p,
                    "session": s_dash, "farm_session": create_farming_session(final_token, p),
                    "next_checkin": time.time(), "next_farm": time.time()
                })
                print(f"    {Col.G}✓ Setup Complete!{Col.RESET}")
            else:
                print(f"    {Col.R}✗ Auth Failed!{Col.RESET}")

    print(f"\n{Col.Y}🚀 Starting all farming threads...{Col.RESET}\n")
    for user in ready_to_farm:
        threading.Thread(target=user_thread_loop, args=(user,), daemon=True).start()

    while True:
        time.sleep(1)

