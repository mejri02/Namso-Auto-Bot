import requests
import json
import time
import sys
import uuid
import random
import pickle
import os
from datetime import datetime, timezone, timedelta
from collections import deque

class Col:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    NEON_GREEN = '\033[38;5;46m'
    NEON_PINK = '\033[38;5;201m'
    NEON_BLUE = '\033[38;5;51m'
    PURPLE = '\033[38;5;141m'
    ORANGE = '\033[38;5;208m'

BASE_FARM_INTERVAL = 60
CHECKIN_INTERVAL = 86400
MIN_SYNC_INTERVAL = 300
MAX_SYNC_INTERVAL = 600
ADAPTIVE_SYNC = True
SESSION_FILE = 'sessions.dat'
active_users = []
use_proxy_mode = False

API_ENDPOINTS = {
    'connectAuth': 'https://sentry-api.namso.network/devv/api/connectAuth',
    'refreshConn': 'https://sentry-api.namso.network/devv/api/refreshConn',
    'taskSubmit': 'https://sentry-api.namso.network/devv/api/taskSubmit',
    'healthCheck': 'https://sentry-api.namso.network/devv/api/healthCheck',
    'fetchStatus': 'https://sentry-api.namso.network/devv/api/fetchStatus',
    'fetchConfig': 'https://sentry-api.namso.network/devv/api/fetchConfig',
    'disconnect': 'https://sentry-api.namso.network/devv/api/disconnect',
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def print_banner():
    banner = f"""
{Col.NEON_PINK}╔═══════════════════════════════════════════════════════════════╗
║  {Col.NEON_BLUE}███╗   ██╗ █████╗ ███╗   ███╗███████╗ ██████╗               {Col.NEON_PINK}║
║  {Col.NEON_BLUE}████╗  ██║██╔══██╗████╗ ████║██╔════╝██╔═══██╗              {Col.NEON_PINK}║
║  {Col.NEON_BLUE}██╔██╗ ██║███████║██╔████╔██║███████╗██║   ██║              {Col.NEON_PINK}║
║  {Col.NEON_BLUE}██║╚██╗██║██╔══██║██║╚██╔╝██║╚════██║██║   ██║              {Col.NEON_PINK}║
║  {Col.NEON_BLUE}██║ ╚████║██║  ██║██║ ╚═╝ ██║███████║╚██████╔╝              {Col.NEON_PINK}║
║  {Col.NEON_BLUE}╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝               {Col.NEON_PINK}║
║                                                               ║
║        {Col.NEON_GREEN}🚀 Namso Farming Bot v3.0 - Full Features 🚀{Col.NEON_PINK}                ║
║                                                               ║
║  {Col.PURPLE}Features:{Col.RESET} {Col.WHITE}Badges • RPS Games • Tasks • Token Refresh{Col.NEON_PINK}     ║
╚═══════════════════════════════════════════════════════════════╝{Col.RESET}
"""
    print(banner)

def print_section_header(title):
    print(f"\n{Col.NEON_PINK}{'═' * 65}{Col.RESET}")
    print(f"{Col.NEON_BLUE}{Col.BOLD}  {title}{Col.RESET}")
    print(f"{Col.NEON_PINK}{'═' * 65}{Col.RESET}\n")

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def read_file_lines(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def mask_email(email):
    if "@" in email:
        parts = email.split("@")
        user = parts[0]
        domain = parts[1]
        if len(user) > 3:
            return f"{user[:3]}***@{domain}"
        return f"{user[:1]}***@{domain}"
    return email

def mask_proxy(proxy):
    if not proxy:
        return f"{Col.NEON_GREEN}Direct{Col.RESET}"
    try:
        if "@" in proxy:
            parts = proxy.split("@")
            creds = parts[0].split(":")
            if len(creds) == 2:
                return f"{Col.ORANGE}****:****@{parts[1]}{Col.RESET}"
        return f"{Col.ORANGE}{proxy}{Col.RESET}"
    except:
        return f"{Col.ORANGE}Proxy{Col.RESET}"

def get_time():
    wib = timezone(timedelta(hours=7))
    return datetime.now(wib).strftime('%H:%M:%S')

def save_sessions(sessions_data):
    try:
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(sessions_data, f)
        print(f"  {Col.NEON_GREEN}✓ Sessions saved{Col.RESET}")
    except Exception as e:
        print(f"  {Col.YELLOW}⚠ Failed to save sessions: {e}{Col.RESET}")

def load_sessions():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'rb') as f:
                sessions_data = pickle.load(f)
            print(f"  {Col.NEON_GREEN}✓ Found saved sessions{Col.RESET}")
            return sessions_data
    except Exception as e:
        print(f"  {Col.YELLOW}⚠ Failed to load sessions: {e}{Col.RESET}")
    return {}

def parse_share_value(share_str):
    try:
        if isinstance(share_str, (int, float)):
            return float(share_str)
        return float(str(share_str).replace(',', '').replace(' SHARE', '').strip())
    except:
        return 0

def is_session_valid(session, email):
    try:
        timestamp = int(time.time() * 1000)
        url_check = f"https://app.namso.network/dashboard/api.php/data-stream?page=dashboard&p=1&_t={timestamp}"
        
        headers = {
            "accept": "*/*",
            "referer": "https://app.namso.network/dashboard/",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": get_random_user_agent()
        }
        
        response = session.get(url_check, headers=headers, timeout=15)
        
        if response.status_code == 403 and "cf-chl" in response.text:
            return False
            
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True
    except Exception as e:
        pass
    return False

def parse_proxy(proxy_str):
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    
    proxy_str = proxy_str.strip()
    
    proxy_types = ['http', 'socks5', 'socks5h', 'socks4']
    
    for ptype in proxy_types:
        if proxy_str.startswith(f'{ptype}://'):
            return proxy_str
    
    try:
        if "@" in proxy_str:
            return f"http://{proxy_str}"
        elif ":" in proxy_str:
            parts = proxy_str.split(":")
            if len(parts) == 2:
                return f"http://{proxy_str}"
            elif len(parts) == 4:
                host, port, user, password = parts
                return f"http://{user}:{password}@{host}:{port}"
    except:
        pass
    
    return None

def test_proxy_connection(proxy_url):
    if not proxy_url:
        return False
    
    try:
        test_session = requests.Session()
        test_session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        test_session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
        response = test_session.get('https://app.namso.network', timeout=15)
        
        if response.status_code == 403 and "cf-chl" in response.text:
            return True
            
        if response.status_code == 200:
            ip_response = test_session.get('https://api.ipify.org?format=json', timeout=10)
            if ip_response.status_code == 200:
                ip_data = ip_response.json()
                print(f"    {Col.NEON_GREEN}✓ Proxy IP: {ip_data.get('ip')}{Col.RESET}")
            return True
            
    except Exception as e:
        print(f"    {Col.RED}✗ Proxy test failed: {e}{Col.RESET}")
    
    return False

def fetch_dashboard_data(session):
    try:
        timestamp = int(time.time() * 1000)
        url = f"https://app.namso.network/dashboard/api.php/data-stream?page=dashboard&p=1&_t={timestamp}"
        
        headers = {
            "accept": "*/*",
            "referer": "https://app.namso.network/dashboard/",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": get_random_user_agent()
        }
        
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return None

def fetch_badges_data(session):
    try:
        timestamp = int(time.time() * 1000)
        url = f"https://app.namso.network/dashboard/api.php/data-stream?page=badges&p=1&_t={timestamp}"
        
        headers = {
            "accept": "*/*",
            "referer": "https://app.namso.network/dashboard/",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": get_random_user_agent()
        }
        
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data')
    except Exception as e:
        pass
    return None

def fetch_server_config(session, sentry_id):
    try:
        response = session.post(
            API_ENDPOINTS['fetchConfig'],
            json={"sentry_id": sentry_id},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data')
    except:
        pass
    return None

def check_session_health(farm_session):
    try:
        response = farm_session.get(API_ENDPOINTS['healthCheck'], timeout=10)
        return response.status_code == 200
    except:
        return False

def refresh_auth_token(user_data):
    try:
        refresh_token = user_data.get('refresh_token')
        if not refresh_token:
            return False
        
        session = requests.Session()
        if user_data.get('proxy'):
            proxy_url = parse_proxy(user_data['proxy'])
            if proxy_url:
                session.proxies.update({'http': proxy_url, 'https': proxy_url})
        
        response = session.post(
            API_ENDPOINTS['refreshConn'],
            json={"refresh_token": refresh_token},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_data['auth_token'] = data.get('token')
                user_data['refresh_token'] = data.get('refresh_token')
                
                headers = {
                    "accept": "*/*",
                    "authorization": f"Bearer {user_data['auth_token']}",
                    "content-type": "application/json",
                    "origin": "chrome-extension://ccdooaopgkfbikbdiekinfheklhbemcd",
                    "user-agent": get_random_user_agent(),
                }
                
                farm_session = requests.Session()
                if user_data.get('proxy'):
                    proxy_url = parse_proxy(user_data['proxy'])
                    if proxy_url:
                        farm_session.proxies.update({'http': proxy_url, 'https': proxy_url})
                farm_session.headers.update(headers)
                user_data['farm_session'] = farm_session
                return True
    except:
        pass
    return False

def perform_dashboard_login(email, password, proxy, saved_sessions=None):
    masked_email = mask_email(email)
    proxy_url = None
    
    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            print(f"\n  {Col.PURPLE}🔌 Testing proxy: {mask_proxy(proxy_url)}{Col.RESET}")
            if not test_proxy_connection(proxy_url):
                print(f"  {Col.YELLOW}⚠ Proxy may not work with Cloudflare{Col.RESET}")

    if saved_sessions and email in saved_sessions:
        print(f"\n{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")
        print(f"{Col.NEON_PINK}🔐 Dashboard Login (Checking Saved Session){Col.RESET}")
        print(f"  {Col.WHITE}Account: {Col.CYAN}{masked_email}{Col.RESET}")

        try:
            session_data = saved_sessions[email]
            session = requests.Session()
            
            if 'cookies' in session_data:
                session.cookies.update(session_data['cookies'])
            if 'headers' in session_data:
                session.headers.update(session_data['headers'])
            
            if proxy_url:
                session.proxies.update({'http': proxy_url, 'https': proxy_url})
                print(f"    {Col.PURPLE}🔌 Using proxy: {mask_proxy(proxy_url)}{Col.RESET}")

            if is_session_valid(session, email):
                print(f"  {Col.NEON_GREEN}✓ Saved session is valid!{Col.RESET}")
                print(f"{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")
                return session
            else:
                print(f"  {Col.YELLOW}⚠ Saved session expired{Col.RESET}")
        except Exception as e:
            print(f"  {Col.YELLOW}⚠ Session error: {e}{Col.RESET}")

    session = requests.Session()
    
    if proxy_url:
        session.proxies.update({'http': proxy_url, 'https': proxy_url})
        print(f"\n  {Col.PURPLE}🔌 Using proxy: {mask_proxy(proxy_url)}{Col.RESET}")

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://app.namso.network",
        "referer": "https://app.namso.network/",
        "user-agent": get_random_user_agent(),
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    session.headers.update(headers)
    
    url_login = "https://app.namso.network/login.php"

    print(f"\n{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")
    print(f"{Col.NEON_PINK}🔐 Dashboard Login{Col.RESET}")
    print(f"  {Col.WHITE}Account: {Col.CYAN}{masked_email}{Col.RESET}")
    print(f"{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")

    try:
        print(f"  {Col.DIM}→ Validating credentials...{Col.RESET}")
        validate_res = session.post(url_login, json={"email": email, "password": password, "action": "validate_credentials"}, timeout=15)
        
        if validate_res.status_code != 200:
            print(f"  {Col.RED}✗ Validation failed: {validate_res.status_code}{Col.RESET}")
            return None
        
        print(f"  {Col.DIM}→ Requesting OTP...{Col.RESET}")
        otp_res = session.post(url_login, json={"email": email, "action": "send_otp"}, timeout=15)
        
        if otp_res.status_code != 200:
            print(f"  {Col.RED}✗ OTP request failed{Col.RESET}")
            return None
            
        print(f"  {Col.NEON_GREEN}✓{Col.RESET} {Col.WHITE}OTP sent to email{Col.RESET}")

        otp_code = input(f"  {Col.YELLOW}📧 Enter OTP for {masked_email}: {Col.RESET}").strip()

        print(f"  {Col.DIM}→ Logging in with OTP...{Col.RESET}")
        login_res = session.post(url_login, json={"email": email, "password": password, "otp": otp_code, "action": "login"}, timeout=15)
        data = login_res.json()

        if data.get("success") is True or data.get("status") == "success":
            print(f"  {Col.NEON_GREEN}✓ Login Successful!{Col.RESET}")
            
            time.sleep(2)
            
            dashboard_data = fetch_dashboard_data(session)
            if dashboard_data and dashboard_data.get('success'):
                print(f"  {Col.NEON_GREEN}✓ Dashboard access verified{Col.RESET}")
                if 'username' in dashboard_data:
                    print(f"  {Col.CYAN}👤 Welcome: {dashboard_data.get('username')}{Col.RESET}")
            
            return session
        else:
            print(f"  {Col.RED}✗ Login Failed: {data}{Col.RESET}")
            return None
            
    except requests.exceptions.ProxyError as e:
        print(f"  {Col.RED}✗ Proxy Error: {e}{Col.RESET}")
        return None
    except Exception as e:
        print(f"  {Col.RED}✗ Error: {e}{Col.RESET}")
        return None

def perform_extension_auth(email, password, proxy):
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "chrome-extension://ccdooaopgkfbikbdiekinfheklhbemcd",
        "user-agent": get_random_user_agent(),
    }

    proxies_dict = None
    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            proxies_dict = {'http': proxy_url, 'https': proxy_url}

    try:
        session = requests.Session()
        if proxies_dict:
            session.proxies.update(proxies_dict)
        session.headers.update(headers)
        
        res = session.post(API_ENDPOINTS['connectAuth'], json={"email": email, "password": password}, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                return {
                    'token': data.get('token'),
                    'refresh_token': data.get('refresh_token'),
                    'user': data.get('user')
                }
    except Exception as e:
        print(f"  {Col.RED}✗ Extension Auth Error: {e}{Col.RESET}")
    return None

def create_farming_session(token, proxy):
    session = requests.Session()

    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            session.proxies.update({'http': proxy_url, 'https': proxy_url})

    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "origin": "chrome-extension://ccdooaopgkfbikbdiekinfheklhbemcd",
        "user-agent": get_random_user_agent(),
    }
    session.headers.update(headers)
    return session

def get_ip_with_proxy(session):
    try:
        response = session.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            return response.json().get('ip')
    except:
        pass
    return None

def setup_validator_node(session):
    base_info = {
        "device_id": str(uuid.uuid4()),
        "version": "1.0." + str(random.randint(1, 5)),
        "uptime": 0
    }

    ip_address = get_ip_with_proxy(session)
    if ip_address:
        print(f"  {Col.NEON_GREEN}🌐 IP: {Col.WHITE}{ip_address}{Col.RESET}")
        try:
            geoloc_url = f"https://ipapi.co/{ip_address}/json/"
            response = session.get(geoloc_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                base_info.update({
                    "ip": ip_address,
                    "city": data.get('city', 'Unknown'),
                    "region": data.get('region', 'Unknown'),
                    "country": data.get('country_code', 'XX'),
                    "country_name": data.get('country_name', 'Unknown'),
                    "timezone": data.get('timezone', 'UTC')
                })
                location = f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}"
                print(f"  {Col.NEON_GREEN}📍 Location: {Col.WHITE}{location}{Col.RESET}")
                return base_info
        except:
            pass
    else:
        print(f"  {Col.YELLOW}⚠ IP detection failed - using default{Col.RESET}")

    base_info.update({
        "ip": "0.0.0.0",
        "city": "Unknown",
        "country": "XX",
        "timezone": "UTC"
    })
    return base_info

def task_checkin(user_data):
    session = user_data['session']
    masked = mask_email(user_data['email'])
    
    if not session:
        return False

    try:
        url = "https://app.namso.network/dashboard/api.php/checkin"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "referer": "https://app.namso.network/dashboard/",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": get_random_user_agent()
        }
        
        response = session.post(url, headers=headers, timeout=10)
        data = response.json()
        
        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        
        if data.get('success'):
            user_data['next_checkin'] = time.time() + CHECKIN_INTERVAL
            user_data['total_checkin_streak'] = user_data.get('total_checkin_streak', 0) + 1
            print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}CHECK-IN{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}Success{Col.RESET} │ Streak: {user_data.get('total_checkin_streak', 1)}")
            return True
        else:
            if 'already' in str(data.get('message', '')).lower():
                if 'next_checkin' not in user_data or user_data['next_checkin'] < time.time():
                    user_data['next_checkin'] = time.time() + CHECKIN_INTERVAL
                print(f"{timestamp} {Col.YELLOW}⏭{Col.RESET} {Col.PURPLE}CHECK-IN{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.YELLOW}Already Done{Col.RESET}")
                return True
            else:
                print(f"{timestamp} {Col.RED}✗{Col.RESET} {Col.PURPLE}CHECK-IN{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.RED}Failed{Col.RESET}")
                return False
                
    except Exception as e:
        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        print(f"{timestamp} {Col.RED}✗ CHECK-IN{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Error: {str(e)[:50]}")
        return False

def claim_eligible_badges(session, user_data):
    masked = mask_email(user_data['email'])
    print(f"  {Col.DIM}→ Checking badges for {masked}...{Col.RESET}")
    
    try:
        badges_data = fetch_badges_data(session)
        if not badges_data:
            print(f"  {Col.YELLOW}⚠ No badges data received{Col.RESET}")
            return
        
        badges = badges_data if isinstance(badges_data, list) else badges_data.get('badges', [])
        
        if not badges:
            print(f"  {Col.DIM}No badges available{Col.RESET}")
            return
        
        print(f"  {Col.CYAN}Found {len(badges)} badges{Col.RESET}")
        
        for badge in badges:
            badge_name = badge.get('name', 'Unknown')
            badge_status = badge.get('status', 'unknown')
            
            print(f"  {Col.DIM}Badge: {badge_name} | Status: {badge_status}{Col.RESET}")
            
            if badge_status == 'eligible':
                badge_id = badge.get('id')
                print(f"  {Col.NEON_GREEN}→ Attempting to claim: {badge_name}{Col.RESET}")
                
                claim_res = session.post(
                    "https://app.namso.network/dashboard/api.php/acquire-badge",
                    json={"badge_id": badge_id},
                    headers={
                        "accept": "application/json",
                        "content-type": "application/json",
                        "referer": "https://app.namso.network/dashboard/",
                        "x-requested-with": "XMLHttpRequest",
                        "user-agent": get_random_user_agent()
                    },
                    timeout=10
                )
                
                if claim_res.status_code == 200:
                    data = claim_res.json()
                    if data.get('success'):
                        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                        print(f"{timestamp} {Col.NEON_GREEN}🏆{Col.RESET} {Col.PURPLE}BADGE CLAIMED{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}{badge_name}{Col.RESET}")
                        time.sleep(1)
                    else:
                        print(f"  {Col.YELLOW}⚠ Claim failed: {data.get('message', 'Unknown error')}{Col.RESET}")
                else:
                    print(f"  {Col.YELLOW}⚠ Claim HTTP {claim_res.status_code}{Col.RESET}")
            elif badge_status == 'owned':
                print(f"  {Col.DIM}Already owned: {badge_name}{Col.RESET}")
            else:
                print(f"  {Col.DIM}Locked: {badge_name}{Col.RESET}")
                    
    except Exception as e:
        print(f"  {Col.RED}✗ Error claiming badges: {e}{Col.RESET}")

def complete_eligible_tasks(session, user_data):
    try:
        dashboard = fetch_dashboard_data(session)
        if not dashboard:
            return
            
        if not dashboard.get('tasks_by_category'):
            return
            
        masked = mask_email(user_data['email'])
        tasks_by_category = dashboard.get('tasks_by_category', {})
        
        for category, tasks in tasks_by_category.items():
            for task in tasks:
                if task.get('status') == 'eligible':
                    if task.get('task_type') == 'social_click':
                        continue
                    
                    complete_res = session.post(
                        "https://app.namso.network/dashboard/api.php/complete-task",
                        json={"task_id": task['id']},
                        headers={
                            "accept": "application/json",
                            "content-type": "application/json",
                            "referer": "https://app.namso.network/dashboard/",
                            "x-requested-with": "XMLHttpRequest",
                            "user-agent": get_random_user_agent()
                        },
                        timeout=10
                    )
                    
                    if complete_res.status_code == 200:
                        data = complete_res.json()
                        if data.get('success'):
                            points = task.get('reward_points', 0)
                            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                            print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}TASK COMPLETED{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}{task.get('title', 'Unknown')}{Col.RESET} │ +{points} Points")
                            time.sleep(1)
                            
    except Exception as e:
        pass

def play_rps(session, user_data):
    masked = mask_email(user_data['email'])
    print(f"  {Col.DIM}→ Checking RPS for {masked}...{Col.RESET}")
    
    try:
        dashboard = fetch_dashboard_data(session)
        if dashboard and dashboard.get('cooldowns'):
            cooldown = dashboard['cooldowns'].get('rps', {})
            if cooldown.get('active'):
                print(f"  {Col.YELLOW}⚠ RPS on cooldown: {cooldown.get('remaining')}{Col.RESET}")
                return
            else:
                print(f"  {Col.NEON_GREEN}✓ RPS ready to play{Col.RESET}")

        start_res = session.post(
            "https://app.namso.network/dashboard/api.php/rps-start",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "referer": "https://app.namso.network/dashboard/",
                "x-requested-with": "XMLHttpRequest"
            }
        )

        if start_res.status_code == 200:
            start_data = start_res.json()
            if start_data.get('success'):
                timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                print(f"{timestamp} {Col.NEON_GREEN}🎮{Col.RESET} {Col.PURPLE}RPS{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}Game started{Col.RESET}")
                
                moves = ['rock', 'paper', 'scissors']
                round_num = 1
                player_wins = 0
                server_wins = 0
                
                while True:
                    time.sleep(1.5)
                    move = random.choice(moves)
                    
                    play_res = session.post(
                        "https://app.namso.network/dashboard/api.php/rps-play",
                        json={"move": move},
                        headers={
                            "accept": "application/json",
                            "content-type": "application/json",
                            "referer": "https://app.namso.network/dashboard/",
                            "x-requested-with": "XMLHttpRequest"
                        }
                    )
                    
                    if play_res.status_code == 200:
                        data = play_res.json()
                        if data.get('success'):
                            player_move = data.get('player_move', 'unknown')
                            server_move = data.get('server_move', 'unknown')
                            outcome = data.get('outcome', 'unknown')
                            
                            if outcome == 'PLAYER_WINS':
                                player_wins += 1
                            elif outcome == 'SERVER_WINS':
                                server_wins += 1
                            
                            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                            outcome_color = Col.NEON_GREEN if outcome == 'PLAYER_WINS' else Col.RED if outcome == 'SERVER_WINS' else Col.YELLOW
                            
                            print(f"{timestamp} {outcome_color}🎮{Col.RESET} {Col.PURPLE}RPS{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Round {round_num}: {player_move.upper()} vs {server_move.upper()} → {outcome_color}{outcome}{Col.RESET} ({player_wins}-{server_wins})")
                            
                            if data.get('is_game_over'):
                                if data.get('final_result') == 'PLAYER_WON_MATCH':
                                    reward = data.get('reward_amount', 0)
                                    print(f"{timestamp} {Col.NEON_GREEN}🏆{Col.RESET} {Col.PURPLE}RPS{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}WON MATCH{Col.RESET} │ +{reward} SHARE")
                                    user_data['total_points'] = user_data.get('total_points', 0) + reward
                                elif data.get('final_result') == 'SERVER_WON_MATCH':
                                    print(f"{timestamp} {Col.RED}💔{Col.RESET} {Col.PURPLE}RPS{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.RED}Lost match{Col.RESET}")
                                    
                                    loss_res = session.post(
                                        "https://app.namso.network/dashboard/api.php/rps-report-loss",
                                        headers={
                                            "accept": "application/json",
                                            "content-type": "application/json",
                                            "referer": "https://app.namso.network/dashboard/",
                                            "x-requested-with": "XMLHttpRequest"
                                        }
                                    )
                                    
                                    if loss_res.status_code == 200:
                                        loss_data = loss_res.json()
                                        if loss_data.get('success') and loss_data.get('second_try_available'):
                                            print(f"{timestamp} {Col.YELLOW}✨{Col.RESET} {Col.PURPLE}RPS{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.YELLOW}Second chance! Starting new match...{Col.RESET}")
                                            time.sleep(2)
                                            play_rps(session, user_data)
                                            return
                                break
                            
                            round_num += 1
                    else:
                        print(f"  {Col.RED}✗ Play failed: HTTP {play_res.status_code}{Col.RESET}")
                        break
            else:
                print(f"  {Col.RED}✗ Failed to start RPS: {start_data.get('message', 'Unknown error')}{Col.RESET}")
    except Exception as e:
        print(f"  {Col.RED}✗ Error in RPS: {e}{Col.RESET}")

def pre_farm_health_check(farm_session):
    try:
        health_res = farm_session.get(API_ENDPOINTS['healthCheck'], timeout=10)
        return health_res.status_code == 200
    except:
        return False

def monitor_validator_quality(user_data):
    session = user_data['session']
    dashboard = fetch_dashboard_data(session)
    if dashboard:
        valid_str = dashboard.get('valid_contribution', '0')
        invalid_str = dashboard.get('invalid_contribution', '0')
        
        valid = parse_share_value(valid_str)
        invalid = parse_share_value(invalid_str)
        
        if valid + invalid > 0:
            quality = valid / (valid + invalid) * 100
            user_data['validator_quality'] = quality
            
            if quality < 80:
                masked = mask_email(user_data['email'])
                timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                print(f"{timestamp} {Col.YELLOW}⚠{Col.RESET} {Col.PURPLE}QUALITY{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.YELLOW}{quality:.1f}%{Col.RESET}")

def get_farming_intensity(user_data):
    reputation = user_data.get('last_reputation', 0)
    
    if reputation >= 90:
        return MIN_SYNC_INTERVAL, 'high'
    elif reputation >= 84:
        return MIN_SYNC_INTERVAL + 60, 'normal'
    elif reputation >= 65:
        return MIN_SYNC_INTERVAL + 120, 'low'
    else:
        return MAX_SYNC_INTERVAL, 'minimal'

def track_farming_efficiency(user_data, shares_change):
    hour = datetime.now().hour
    
    if 'hourly_efficiency' not in user_data:
        user_data['hourly_efficiency'] = {}
    
    if hour not in user_data['hourly_efficiency']:
        user_data['hourly_efficiency'][hour] = []
    
    user_data['hourly_efficiency'][hour].append(shares_change)
    
    if len(user_data['hourly_efficiency'][hour]) > 10:
        user_data['hourly_efficiency'][hour] = user_data['hourly_efficiency'][hour][-10:]

def calculate_smart_interval(user_data, server_response):
    base_interval, _ = get_farming_intensity(user_data)
    
    if server_response and 'next_sync' in server_response:
        server_interval = server_response['next_sync'] - int(time.time())
        if server_interval > 0:
            base_interval = min(server_interval, base_interval)
    
    online = user_data.get('online_validators', 0)
    if online > 0:
        base_interval = max(MIN_SYNC_INTERVAL, base_interval - (online * 3))
    
    reputation = user_data.get('last_reputation', 0)
    if reputation < 65:
        base_interval = min(MAX_SYNC_INTERVAL, int(base_interval * 1.3))
    
    return min(MAX_SYNC_INTERVAL, max(MIN_SYNC_INTERVAL, base_interval))

def task_farming_and_monitor(user_data):
    farm_session = user_data['farm_session']
    masked = mask_email(user_data['email'])
    email = user_data['email']
    password = user_data['password']
    proxy = user_data['proxy']

    if not farm_session:
        auth_result = perform_extension_auth(email, password, proxy)
        if auth_result:
            user_data['auth_token'] = auth_result['token']
            user_data['refresh_token'] = auth_result['refresh_token']
            user_data['farm_session'] = create_farming_session(auth_result['token'], proxy)
            farm_session = user_data['farm_session']
            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
            print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Extension authenticated")
            user_data['geo_info'] = setup_validator_node(farm_session)
            user_data['start_time'] = time.time()
            user_data['total_shares'] = 0
            user_data['total_points'] = 0
            user_data['interval_history'] = deque(maxlen=10)
        else:
            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
            print(f"{timestamp} {Col.YELLOW}⏭{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Skipped (auth failed)")
            return

    if not pre_farm_health_check(farm_session):
        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        print(f"{timestamp} {Col.YELLOW}⚠{Col.RESET} {Col.PURPLE}HEALTH{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Unhealthy session")
        if refresh_auth_token(user_data):
            farm_session = user_data['farm_session']
            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
            print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Token refreshed")
        else:
            new_token = perform_extension_auth(email, password, proxy)
            if new_token:
                user_data['farm_session'] = create_farming_session(new_token, proxy)
                farm_session = user_data['farm_session']
                timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Token refreshed")

    url_task = API_ENDPOINTS['taskSubmit']

    need_relogin = False
    farming_success = False
    rate_limited = False
    server_error = False
    shares = 0
    points_today = 0
    server_next_sync = None
    shares_value = 0

    try:
        geo = user_data.get('geo_info', {})
        enhanced_payload = {
            "email": email,
            "device_id": geo.get('device_id', ''),
            "uptime": int(time.time() - user_data.get('start_time', time.time())),
            "version": geo.get('version', '1.0.0')
        }
        
        res_submit = farm_session.post(url_task, json=enhanced_payload, timeout=15)

        if res_submit.status_code == 401:
            need_relogin = True
            raise Exception("Token expired")

        if res_submit.status_code == 500:
            server_error = True
            raise Exception("Server error")

        if res_submit.status_code == 200:
            data = res_submit.json()
            if data.get('success'):
                farming_success = True
                shares = parse_share_value(data.get('shares', 0))
                points_today = data.get('points_today', 0)

                if shares > 0:
                    shares_value = shares - user_data.get('total_shares', 0)
                    user_data['total_shares'] = shares
                    track_farming_efficiency(user_data, shares_value)
                    
                if points_today > 0:
                    user_data['total_points'] = points_today

                next_sync = data.get('next_sync')
                if next_sync:
                    server_next_sync = next_sync - int(time.time())
                    if server_next_sync > 0:
                        user_data['server_hint'] = server_next_sync
            else:
                error_msg = data.get('error', 'Unknown')
                if 'too frequent' in error_msg.lower() or 'sync' in error_msg.lower():
                    rate_limited = True
                elif 'invalid session' in error_msg.lower():
                    need_relogin = True

    except Exception as e:
        error_msg = str(e)
        if "401" not in error_msg and "Token" not in error_msg and "Server error" not in error_msg:
            pass

    if not farming_success:
        user_data['fail_count'] = user_data.get('fail_count', 0) + 1
        if user_data['fail_count'] >= 3 and not need_relogin:
            need_relogin = True
            user_data['fail_count'] = 0
    else:
        user_data['fail_count'] = 0
        user_data['last_success'] = time.time()

    if need_relogin:
        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        print(f"{timestamp} {Col.YELLOW}🔄{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Re-authenticating...")
        if refresh_auth_token(user_data):
            farm_session = user_data['farm_session']
            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
            print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Token refreshed")
        else:
            new_token = perform_extension_auth(email, password, proxy)
            if new_token:
                user_data['farm_session'] = create_farming_session(new_token, proxy)
                user_data['geo_info'] = setup_validator_node(user_data['farm_session'])
                user_data['start_time'] = time.time()
                timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
                print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Token refreshed")

    monitor_validator_quality(user_data)
    
    dashboard = fetch_dashboard_data(user_data['session'])
    if dashboard:
        user_data['online_validators'] = dashboard.get('online_validators', 0)
        user_data['last_reputation'] = dashboard.get('reputation_score', user_data.get('last_reputation', 0))
        user_data['average_uptime'] = dashboard.get('average_uptime', '0%')
        
        valid_str = dashboard.get('valid_contribution', '0')
        invalid_str = dashboard.get('invalid_contribution', '0')
        
        valid = parse_share_value(valid_str)
        invalid = parse_share_value(invalid_str)
        
        if valid + invalid > 0:
            quality = valid / (valid + invalid) * 100
            user_data['validator_quality'] = quality

    elapsed = int(time.time() - user_data.get('start_time', time.time()))
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    uptime_str = f"{hours}h {minutes}m"

    timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"

    if farming_success:
        shares_str = f"{user_data.get('total_shares', 0):,.4f}"
        points_str = f"{user_data.get('total_points', 0):.2f}"

        smart_interval = calculate_smart_interval(user_data, {'next_sync': server_next_sync}) if server_next_sync else MIN_SYNC_INTERVAL
        user_data['optimal_interval'] = smart_interval
        
        quality = user_data.get('validator_quality', 100)
        quality_color = Col.NEON_GREEN if quality >= 90 else Col.YELLOW if quality >= 80 else Col.RED
        
        print(f"{timestamp} {Col.NEON_GREEN}●{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}Online{Col.RESET} │ SHR: {Col.WHITE}{shares_str}{Col.RESET} │ PTS: {Col.WHITE}{points_str}{Col.RESET} │ REP: {Col.MAGENTA}{user_data.get('last_reputation', 0):.1f}{Col.RESET} │ QLTY: {quality_color}{quality:.1f}%{Col.RESET} │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET} │ Next: {Col.ORANGE}{smart_interval}s{Col.RESET}")
    elif rate_limited:
        user_data['optimal_interval'] = user_data.get('optimal_interval', MIN_SYNC_INTERVAL) + 30
        print(f"{timestamp} {Col.YELLOW}⏳{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.YELLOW}Rate Limited{Col.RESET} │ Wait: {Col.ORANGE}{user_data['optimal_interval']}s{Col.RESET} │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET}")
    elif server_error:
        print(f"{timestamp} {Col.RED}⚠{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.RED}Server Error{Col.RESET} │ Retry next cycle │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET}")
    else:
        status_text = "Token Expired" if need_relogin else "Failed"
        print(f"{timestamp} {Col.RED}✗{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.RED}{status_text}{Col.RESET} │ Will retry │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET}")

def display_stats_summary():
    if not active_users:
        return

    print(f"\n{Col.NEON_PINK}{'═' * 100}{Col.RESET}")
    print(f"{Col.NEON_BLUE}{Col.BOLD}  📊 ENHANCED FARMING STATISTICS SUMMARY{Col.RESET}")
    print(f"{Col.NEON_PINK}{'═' * 100}{Col.RESET}")

    total_shares = 0
    total_points = 0
    online_count = 0
    total_reputation = 0
    total_streak = 0
    total_validators = 0
    total_quality = 0
    quality_count = 0

    for user_data in active_users:
        masked = mask_email(user_data['email'])
        shares = user_data.get('total_shares', 0)
        points = user_data.get('total_points', 0)
        is_online = user_data.get('farm_session') is not None
        reputation = user_data.get('last_reputation', 0)
        streak = user_data.get('total_checkin_streak', 0)
        validators = user_data.get('online_validators', 0)
        quality = user_data.get('validator_quality', 100)
        uptime = user_data.get('average_uptime', '0%')

        if isinstance(shares, (int, float)):
            total_shares += shares
        if isinstance(points, (int, float)):
            total_points += points
        if is_online:
            online_count += 1
        if isinstance(reputation, (int, float)):
            total_reputation += reputation
        if isinstance(streak, int):
            total_streak += streak
        if isinstance(validators, int):
            total_validators += validators
        if isinstance(quality, (int, float)):
            total_quality += quality
            quality_count += 1

        elapsed = int(time.time() - user_data.get('start_time', time.time()))
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60

        status = f"{Col.NEON_GREEN}●{Col.RESET}" if is_online else f"{Col.RED}○{Col.RESET}"
        shares_str = f"{shares:,.4f}" if isinstance(shares, (int, float)) else "N/A"
        points_str = f"{points:.2f}" if isinstance(points, (int, float)) else "N/A"
        rep_str = f"{reputation:.2f}" if isinstance(reputation, (int, float)) else "N/A"
        quality_str = f"{quality:.1f}%" if isinstance(quality, (int, float)) else "N/A"
        quality_color = Col.NEON_GREEN if quality >= 90 else Col.YELLOW if quality >= 80 else Col.RED

        print(f"  {status} {Col.CYAN}{masked:30}{Col.RESET} │ SHR: {Col.WHITE}{shares_str:12}{Col.RESET} │ PTS: {Col.WHITE}{points_str:8}{Col.RESET} │ REP: {Col.MAGENTA}{rep_str:6}{Col.RESET} │ QLTY: {quality_color}{quality_str:6}{Col.RESET} │ STRK: {Col.YELLOW}{streak:2}{Col.RESET} │ VAL: {Col.BLUE}{validators:2}{Col.RESET} │ UPT: {uptime:6} │ ⏱ {Col.YELLOW}{hours}h {minutes}m{Col.RESET}")

    avg_reputation = total_reputation / len(active_users) if active_users else 0
    avg_validators = total_validators / len(active_users) if active_users else 0
    avg_quality = total_quality / quality_count if quality_count > 0 else 100

    print(f"{Col.NEON_PINK}{'─' * 100}{Col.RESET}")
    print(f"  {Col.BOLD}Total Accounts:{Col.RESET} {Col.WHITE}{len(active_users)}{Col.RESET} │ {Col.BOLD}Online:{Col.RESET} {Col.NEON_GREEN}{online_count}{Col.RESET} │ {Col.BOLD}Total Shares:{Col.RESET} {Col.WHITE}{total_shares:,.4f}{Col.RESET}")
    print(f"  {Col.BOLD}Total Points:{Col.RESET} {Col.WHITE}{total_points:.2f}{Col.RESET} │ {Col.BOLD}Avg Reputation:{Col.RESET} {Col.MAGENTA}{avg_reputation:.2f}{Col.RESET} │ {Col.BOLD}Avg Quality:{Col.RESET} {Col.CYAN}{avg_quality:.1f}%{Col.RESET}")
    print(f"  {Col.BOLD}Total Validators:{Col.RESET} {Col.BLUE}{total_validators}{Col.RESET} │ {Col.BOLD}Avg Validators:{Col.RESET} {Col.CYAN}{avg_validators:.1f}{Col.RESET} │ {Col.BOLD}Total Streak:{Col.RESET} {Col.YELLOW}{total_streak}{Col.RESET}")
    print(f"{Col.NEON_PINK}{'═' * 100}{Col.RESET}\n")

def run_initial_tasks():
    print_section_header("🏆 INITIAL TASKS & BADGES & GAMES")
    
    for user_data in active_users:
        masked = mask_email(user_data['email'])
        print(f"\n{Col.CYAN}╔══ Processing {masked}{Col.RESET}")
        print(f"{Col.CYAN}╚══{Col.RESET}")
        
        print(f"  {Col.DIM}→ Checking in...{Col.RESET}")
        task_checkin(user_data)
        time.sleep(2)
        
        print(f"  {Col.DIM}→ Checking badges...{Col.RESET}")
        claim_eligible_badges(user_data['session'], user_data)
        time.sleep(2)
        
        print(f"  {Col.DIM}→ Checking tasks...{Col.RESET}")
        complete_eligible_tasks(user_data['session'], user_data)
        time.sleep(2)
        
        print(f"  {Col.DIM}→ Playing RPS...{Col.RESET}")
        play_rps(user_data['session'], user_data)
        time.sleep(2)
        
        print(f"  {Col.NEON_GREEN}✓ Initial processing complete for {masked}{Col.RESET}")

def main():
    global active_users, use_proxy_mode

    print_banner()

    print_section_header("🔧 CONFIGURATION")

    proxy_choice = input(f"  {Col.YELLOW}Use proxies? (y/n): {Col.RESET}").strip().lower()
    use_proxy_mode = proxy_choice == 'y'

    if use_proxy_mode:
        print(f"  {Col.NEON_GREEN}✓ Proxy mode enabled{Col.RESET}")
        print(f"  {Col.YELLOW}⚠ Note: Cloudflare may block datacenter proxies{Col.RESET}")
    else:
        print(f"  {Col.NEON_GREEN}✓ Direct connection mode{Col.RESET}")

    print_section_header("📂 LOADING CREDENTIALS")

    accounts_data = read_file_lines('accounts.txt')
    proxies = read_file_lines('proxy.txt') if use_proxy_mode else []

    if not accounts_data:
        print(f"{Col.RED}✗ Error: accounts.txt not found or empty{Col.RESET}")
        print(f"{Col.YELLOW}Format: email|password or email:password (one per line){Col.RESET}")
        sys.exit(1)

    emails = []
    passwords = []

    for line in accounts_data:
        if '|' in line:
            parts = line.split('|', 1)
            emails.append(parts[0].strip())
            passwords.append(parts[1].strip())
        elif ':' in line:
            parts = line.split(':', 1)
            emails.append(parts[0].strip())
            passwords.append(parts[1].strip())
        else:
            print(f"{Col.YELLOW}⚠ Warning: Skipping invalid format: {line[:20]}...{Col.RESET}")

    if not emails or not passwords:
        print(f"{Col.RED}✗ Error: No valid credentials found in accounts.txt{Col.RESET}")
        sys.exit(1)

    if use_proxy_mode and len(proxies) < len(emails):
        print(f"{Col.YELLOW}⚠ Warning: Not enough proxies. Some accounts will reuse proxies{Col.RESET}")

    print(f"  {Col.NEON_GREEN}✓ Loaded {len(emails)} accounts{Col.RESET}")
    if use_proxy_mode:
        print(f"  {Col.NEON_GREEN}✓ Loaded {len(proxies)} proxies{Col.RESET}")

    print_section_header("🔑 BULK AUTHENTICATION")

    saved_sessions = load_sessions()
    sessions_to_save = {}

    for idx, (email, password) in enumerate(zip(emails, passwords)):
        proxy = None
        if use_proxy_mode and proxies:
            proxy = proxies[idx % len(proxies)]
            print(f"\n{Col.CYAN}📌 Account {idx+1}/{len(emails)} - Using proxy #{idx % len(proxies) + 1}{Col.RESET}")

        session = perform_dashboard_login(email, password, proxy, saved_sessions)
        if not session:
            print(f"{Col.RED}✗ Failed to login {mask_email(email)}, skipping...{Col.RESET}")
            continue

        auth_result = perform_extension_auth(email, password, proxy)
        if not auth_result:
            print(f"{Col.RED}✗ Extension auth failed for {mask_email(email)}, skipping...{Col.RESET}")
            continue

        farm_session = create_farming_session(auth_result['token'], proxy)
        geo_info = setup_validator_node(farm_session)
        
        server_config = fetch_server_config(session, auth_result.get('user', {}).get('sentry_id', ''))

        sessions_to_save[email] = {
            'cookies': session.cookies.get_dict(),
            'headers': dict(session.headers),
            'refresh_token': auth_result['refresh_token'],
            'timestamp': time.time()
        }

        current_time = time.time()
        user_data = {
            'email': email,
            'password': password,
            'proxy': proxy,
            'session': session,
            'farm_session': farm_session,
            'auth_token': auth_result['token'],
            'refresh_token': auth_result['refresh_token'],
            'geo_info': geo_info,
            'server_config': server_config,
            'start_time': time.time(),
            'next_checkin': time.time(),
            'next_badges_check': current_time - 86400,
            'next_tasks_check': current_time - 86400,
            'next_rps_check': current_time - 86400,
            'optimal_interval': MIN_SYNC_INTERVAL,
            'fail_count': 0,
            'total_shares': 0,
            'total_points': 0,
            'interval_history': deque(maxlen=10),
            'total_checkin_streak': 0,
            'last_reputation': 0,
            'reputation_history': [],
            'online_validators': 0,
            'total_validators': 0,
            'average_uptime': '0%',
            'validator_quality': 100,
            'hourly_efficiency': {},
            'last_success': time.time()
        }
        active_users.append(user_data)
        print(f"  {Col.NEON_GREEN}✓ {mask_email(email)} ready{Col.RESET}\n")

    if sessions_to_save:
        save_sessions(sessions_to_save)

    if not active_users:
        print(f"{Col.RED}✗ No users successfully authenticated{Col.RESET}")
        sys.exit(1)

    run_initial_tasks()

    print_section_header("🚀 STARTING ENHANCED FARMING")
    print(f"  {Col.NEON_GREEN}Active Accounts: {len(active_users)}{Col.RESET}")
    print(f"  {Col.PURPLE}Adaptive Sync: {'Enabled' if ADAPTIVE_SYNC else 'Disabled'}{Col.RESET}")
    print(f"  {Col.CYAN}Base Interval: {BASE_FARM_INTERVAL}s{Col.RESET}")
    print(f"  {Col.MAGENTA}Features: Badges • RPS Games • Tasks • Token Refresh{Col.RESET}\n")

    cycle_count = 0
    last_stats_display = time.time()

    while True:
        cycle_count += 1
        print(f"\n{Col.NEON_BLUE}{'─' * 100}{Col.RESET}")
        print(f"{Col.BOLD}{Col.NEON_PINK}  🔄 CYCLE #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Col.RESET}")
        print(f"{Col.NEON_BLUE}{'─' * 100}{Col.RESET}\n")

        for user_data in active_users:
            current_time = time.time()
            
            if current_time >= user_data.get('next_checkin', 0):
                task_checkin(user_data)
                user_data['next_checkin'] = current_time + CHECKIN_INTERVAL
            
            if current_time >= user_data.get('next_badges_check', 0):
                print(f"  {Col.DIM}→ Daily badges check...{Col.RESET}")
                claim_eligible_badges(user_data['session'], user_data)
                user_data['next_badges_check'] = current_time + CHECKIN_INTERVAL
            
            if current_time >= user_data.get('next_tasks_check', 0):
                print(f"  {Col.DIM}→ Daily tasks check...{Col.RESET}")
                complete_eligible_tasks(user_data['session'], user_data)
                user_data['next_tasks_check'] = current_time + CHECKIN_INTERVAL
            
            if current_time >= user_data.get('next_rps_check', 0):
                print(f"  {Col.DIM}→ Daily RPS check...{Col.RESET}")
                play_rps(user_data['session'], user_data)
                user_data['next_rps_check'] = current_time + CHECKIN_INTERVAL
            
            task_farming_and_monitor(user_data)
            
            time.sleep(2)

        if time.time() - last_stats_display >= 300:
            display_stats_summary()
            last_stats_display = time.time()

        wait_time = min([user.get('optimal_interval', BASE_FARM_INTERVAL) for user in active_users])

        print(f"\n{Col.DIM}[{get_time()}]{Col.RESET} {Col.YELLOW}⏸{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ Waiting {Col.ORANGE}{wait_time}s{Col.RESET} for next cycle...")
        time.sleep(wait_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Col.NEON_PINK}{'═' * 100}{Col.RESET}")
        print(f"{Col.YELLOW}  ⚠ Bot stopped by user{Col.RESET}")
        display_stats_summary()
        print(f"{Col.NEON_BLUE}  👋 Thank you for using Namso Farming Bot v3.0!{Col.RESET}")
        print(f"{Col.NEON_PINK}{'═' * 100}{Col.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Col.RED}✗ Fatal error: {e}{Col.RESET}")
        sys.exit(1)
