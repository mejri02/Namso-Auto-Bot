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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
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
║        {Col.NEON_GREEN}🚀 Advanced Farming Bot v2.0 - Enhanced Edition 🚀{Col.NEON_PINK}       ║
║                                                               ║
║  {Col.PURPLE}Features:{Col.RESET} {Col.WHITE}Adaptive Sync • Smart Retry • Stats Tracking{Col.NEON_PINK}    ║
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
            masked = proxy.split("@")[1]
            return f"{Col.ORANGE}{masked}{Col.RESET}"
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

def is_session_valid(session, email):
    try:
        url_check = "https://app.namso.network/dashboard/api.php/user"
        res = session.get(url_check, timeout=10)
        if res.status_code == 200:
            return True
    except:
        pass
    return False

def parse_proxy(proxy_str):
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    proxy_str = proxy_str.strip()
    if proxy_str.startswith(('http://', 'https://', 'socks4://', 'socks5://', 'socks://')):
        return proxy_str
    try:
        if "@" in proxy_str:
            return f"socks5://{proxy_str}"
        elif ":" in proxy_str:
            parts = proxy_str.split(":")
            if len(parts) == 2:
                return f"socks5://{proxy_str}"
            elif len(parts) == 4:
                host, port, user, password = parts
                return f"socks5://{user}:{password}@{host}:{port}"
    except:
        pass
    return None

def perform_dashboard_login(email, password, proxy, saved_sessions=None):
    masked_email = mask_email(email)

    if saved_sessions and email in saved_sessions:
        print(f"\n{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")
        print(f"{Col.NEON_PINK}🔐 Dashboard Login (Checking Saved Session){Col.RESET}")
        print(f"  {Col.WHITE}Account: {Col.CYAN}{masked_email}{Col.RESET}")

        try:
            session = saved_sessions[email]['session']
            dashboard_token = saved_sessions[email]['token']

            if proxy:
                proxy_url = parse_proxy(proxy)
                if proxy_url:
                    session.proxies.update({'http': proxy_url, 'https': proxy_url})

            if is_session_valid(session, email):
                print(f"  {Col.NEON_GREEN}✓ Saved session is valid! Skipping OTP{Col.RESET}")
                print(f"{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")
                return session, dashboard_token
            else:
                print(f"  {Col.YELLOW}⚠ Saved session expired, re-authenticating...{Col.RESET}")
        except Exception as e:
            print(f"  {Col.YELLOW}⚠ Session error: {e}{Col.RESET}")

    session = requests.Session()

    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            print(f"    {Col.PURPLE}🔌 Proxy: {mask_proxy(proxy_url)}{Col.RESET}")
            session.proxies.update({'http': proxy_url, 'https': proxy_url})

    headers = {
        "authority": "app.namso.network",
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://app.namso.network",
        "referer": "https://app.namso.network/",
        "user-agent": get_random_user_agent(),
    }
    session.headers.update(headers)
    url_login = "https://app.namso.network/login.php"

    print(f"\n{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")
    print(f"{Col.NEON_PINK}🔐 Dashboard Login{Col.RESET}")
    print(f"  {Col.WHITE}Account: {Col.CYAN}{masked_email}{Col.RESET}")
    print(f"  {Col.WHITE}Method:  {mask_proxy(proxy) if proxy else f'{Col.NEON_GREEN}Direct Connection{Col.RESET}'}")
    print(f"{Col.NEON_BLUE}{'─' * 60}{Col.RESET}")

    try:
        session.post(url_login, json={"email": email, "password": password, "action": "validate_credentials"})
        session.post(url_login, json={"email": email, "action": "send_otp"})
        print(f"  {Col.NEON_GREEN}✓{Col.RESET} {Col.WHITE}OTP sent to email{Col.RESET}")

        otp_code = input(f"  {Col.YELLOW}📧 Enter OTP for {masked_email}: {Col.RESET}")

        res3 = session.post(url_login, json={"email": email, "password": password, "otp": otp_code, "action": "login"})
        data = res3.json()

        if data.get("success") is True or data.get("status") == "success":
            print(f"  {Col.NEON_GREEN}✓ Login Successful!{Col.RESET}")
            dashboard_token = data.get('token') or data.get('access_token')
            return session, dashboard_token
        else:
            print(f"  {Col.RED}✗ Login Failed: {data}{Col.RESET}")
            return None, None
    except Exception as e:
        print(f"  {Col.RED}✗ Error: {e}{Col.RESET}")
        return None, None

def perform_extension_auth(email, password, proxy):
    url = "https://sentry-api.namso.network/devv/api/connectAuth"
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
        res = requests.post(url, json={"email": email, "password": password}, headers=headers, proxies=proxies_dict, timeout=15)
        if res.status_code == 200:
            data = res.json()
            token = data.get("token") or data.get("access_token")
            if token:
                return token
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
        test_urls = [
            "https://api.ipify.org?format=json",
            "https://api64.ipify.org?format=json",
        ]
        for url in test_urls:
            try:
                response = session.get(url, timeout=10)
                if response.status_code == 200:
                    if "ipify" in url:
                        ip_data = response.json()
                        return ip_data.get('ip')
                    else:
                        return response.text.strip()
            except:
                continue
    except Exception as e:
        print(f"  {Col.RED}[IP Check] Error: {e}{Col.RESET}")
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
        return

    url_checkin = "https://app.namso.network/dashboard/api.php/checkin"
    try:
        res = session.post(url_checkin)
        data = res.json()
        msg = data.get("message", res.text[:50])

        if data.get("success") or "Success" in str(msg):
            status_icon = f"{Col.NEON_GREEN}✓{Col.RESET}"
            status = f"{Col.NEON_GREEN}Success{Col.RESET}"
            user_data['next_checkin'] = time.time() + CHECKIN_INTERVAL
            msg = "Daily check-in completed!"
        elif "already" in str(msg).lower():
            status_icon = f"{Col.YELLOW}⏭{Col.RESET}"
            status = f"{Col.YELLOW}Already Done{Col.RESET}"
            if 'next_checkin' not in user_data or user_data['next_checkin'] < time.time():
                user_data['next_checkin'] = time.time() + CHECKIN_INTERVAL
            remaining = int(user_data['next_checkin'] - time.time())
            if remaining > 0:
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                msg = f"Next in {hours}h {minutes}m"
            else:
                msg = "Next in 24h"
        else:
            status_icon = f"{Col.RED}✗{Col.RESET}"
            status = f"{Col.RED}Failed{Col.RESET}"

        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        print(f"{timestamp} {status_icon} {Col.PURPLE}CHECK-IN{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {status} │ {Col.WHITE}{msg}{Col.RESET}")
    except Exception as e:
        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        print(f"{timestamp} {Col.RED}✗ CHECK-IN{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Error: {str(e)[:50]}")

def calculate_adaptive_interval(user_data, server_suggested=None):
    if server_suggested and server_suggested > 0:
        variance = random.randint(-5, 5)
        return max(MIN_SYNC_INTERVAL, min(server_suggested + variance, MAX_SYNC_INTERVAL))

    fail_count = user_data.get('fail_count', 0)
    if fail_count > 0:
        return min(MIN_SYNC_INTERVAL * (1.5 ** fail_count), MAX_SYNC_INTERVAL)

    interval_history = user_data.get('interval_history', deque(maxlen=10))
    if len(interval_history) > 3:
        avg_interval = sum(interval_history) / len(interval_history)
        return max(MIN_SYNC_INTERVAL, min(int(avg_interval), MAX_SYNC_INTERVAL))

    return MIN_SYNC_INTERVAL

def task_farming_and_monitor(user_data):
    farm_session = user_data['farm_session']
    masked = mask_email(user_data['email'])
    email = user_data['email']
    password = user_data['password']
    proxy = user_data['proxy']

    if not farm_session:
        new_token = perform_extension_auth(email, password, proxy)
        if new_token:
            user_data['farm_session'] = create_farming_session(new_token, proxy)
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

    url_health = "https://sentry-api.namso.network/devv/api/healthCheck"
    url_task = "https://sentry-api.namso.network/devv/api/taskSubmit"

    need_relogin = False
    farming_success = False
    rate_limited = False
    server_error = False
    shares = "N/A"
    points_today = "N/A"
    server_next_sync = None

    try:
        health_res = farm_session.post(url_health, timeout=15)
        if health_res.status_code == 401:
            need_relogin = True
            raise Exception("Token expired")

        payload = {"email": email}
        res_submit = farm_session.post(url_task, json=payload, timeout=15)

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
                shares = data.get('shares', 'N/A')
                points_today = data.get('points_today', 'N/A')

                if isinstance(shares, (int, float)):
                    user_data['total_shares'] = shares
                if isinstance(points_today, (int, float)):
                    user_data['total_points'] = points_today

                next_sync = data.get('next_sync')
                if next_sync:
                    server_next_sync = next_sync - int(time.time())
                    if server_next_sync > 0:
                        user_data['optimal_interval'] = calculate_adaptive_interval(user_data, server_next_sync)
            else:
                error_msg = data.get('error', 'Unknown')
                if 'too frequent' in error_msg.lower() or 'sync' in error_msg.lower():
                    rate_limited = True
                    user_data['optimal_interval'] = calculate_adaptive_interval(user_data)
                elif 'invalid session' in error_msg.lower() or 'session' in error_msg.lower():
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
        interval_used = user_data.get('optimal_interval', MIN_SYNC_INTERVAL)
        user_data['interval_history'].append(interval_used)

    if need_relogin:
        timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
        print(f"{timestamp} {Col.YELLOW}🔄{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Re-authenticating...")
        new_token = perform_extension_auth(email, password, proxy)
        if new_token:
            user_data['farm_session'] = create_farming_session(new_token, proxy)
            user_data['geo_info'] = setup_validator_node(user_data['farm_session'])
            user_data['start_time'] = time.time()
            timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"
            print(f"{timestamp} {Col.NEON_GREEN}✓{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ Token refreshed")

            try:
                farm_session = user_data['farm_session']
                payload = {"email": email}
                res_submit = farm_session.post(url_task, json=payload, timeout=15)

                if res_submit.status_code == 200:
                    data = res_submit.json()
                    if data.get('success'):
                        farming_success = True
                        shares = data.get('shares', 'N/A')
                        points_today = data.get('points_today', 'N/A')

                        if isinstance(shares, (int, float)):
                            user_data['total_shares'] = shares
                        if isinstance(points_today, (int, float)):
                            user_data['total_points'] = points_today

                        next_sync = data.get('next_sync')
                        if next_sync:
                            server_next_sync = next_sync - int(time.time())
                            if server_next_sync > 0:
                                user_data['optimal_interval'] = calculate_adaptive_interval(user_data, server_next_sync)
            except Exception as retry_err:
                pass

    elapsed = int(time.time() - user_data.get('start_time', time.time()))
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    uptime_str = f"{hours}h {minutes}m"

    timestamp = f"{Col.DIM}[{get_time()}]{Col.RESET}"

    if farming_success:
        if isinstance(shares, (int, float)):
            shares_str = f"{shares:,.4f}"
        else:
            shares_str = str(shares)

        if isinstance(points_today, (int, float)):
            points_str = f"{points_today:.2f}"
        else:
            points_str = str(points_today)

        next_interval = user_data.get('optimal_interval', MIN_SYNC_INTERVAL)
        print(f"{timestamp} {Col.NEON_GREEN}●{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.NEON_GREEN}Online{Col.RESET} │ SHR: {Col.WHITE}{shares_str}{Col.RESET} │ PTS: {Col.WHITE}{points_str}{Col.RESET} │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET} │ Next: {Col.ORANGE}{next_interval}s{Col.RESET}")
    elif rate_limited:
        next_interval = user_data.get('optimal_interval', MIN_SYNC_INTERVAL)
        print(f"{timestamp} {Col.YELLOW}⏳{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.YELLOW}Rate Limited{Col.RESET} │ Wait: {Col.ORANGE}{next_interval}s{Col.RESET} │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET}")
    elif server_error:
        print(f"{timestamp} {Col.RED}⚠{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.RED}Server Error{Col.RESET} │ Retry next cycle │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET}")
    else:
        status_text = "Token Expired" if need_relogin else "Failed"
        print(f"{timestamp} {Col.RED}✗{Col.RESET} {Col.PURPLE}FARMING{Col.RESET} │ {Col.CYAN}{masked}{Col.RESET} │ {Col.RED}{status_text}{Col.RESET} │ Will retry │ ⏱ {Col.YELLOW}{uptime_str}{Col.RESET}")

def display_stats_summary():
    if not active_users:
        return

    print(f"\n{Col.NEON_PINK}{'═' * 80}{Col.RESET}")
    print(f"{Col.NEON_BLUE}{Col.BOLD}  📊 FARMING STATISTICS SUMMARY{Col.RESET}")
    print(f"{Col.NEON_PINK}{'═' * 80}{Col.RESET}")

    total_shares = 0
    total_points = 0
    online_count = 0

    for user_data in active_users:
        masked = mask_email(user_data['email'])
        shares = user_data.get('total_shares', 0)
        points = user_data.get('total_points', 0)
        is_online = user_data.get('farm_session') is not None

        if isinstance(shares, (int, float)):
            total_shares += shares
        if isinstance(points, (int, float)):
            total_points += points
        if is_online:
            online_count += 1

        elapsed = int(time.time() - user_data.get('start_time', time.time()))
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60

        status = f"{Col.NEON_GREEN}●{Col.RESET}" if is_online else f"{Col.RED}○{Col.RESET}"
        shares_str = f"{shares:,.4f}" if isinstance(shares, (int, float)) else "N/A"
        points_str = f"{points:.2f}" if isinstance(points, (int, float)) else "N/A"

        print(f"  {status} {Col.CYAN}{masked:30}{Col.RESET} │ SHR: {Col.WHITE}{shares_str:12}{Col.RESET} │ PTS: {Col.WHITE}{points_str:10}{Col.RESET} │ ⏱ {Col.YELLOW}{hours}h {minutes}m{Col.RESET}")

    print(f"{Col.NEON_PINK}{'─' * 80}{Col.RESET}")
    print(f"  {Col.BOLD}Total Accounts:{Col.RESET} {Col.WHITE}{len(active_users)}{Col.RESET} │ {Col.BOLD}Online:{Col.RESET} {Col.NEON_GREEN}{online_count}{Col.RESET} │ {Col.BOLD}Total Shares:{Col.RESET} {Col.WHITE}{total_shares:,.4f}{Col.RESET} │ {Col.BOLD}Total Points:{Col.RESET} {Col.WHITE}{total_points:.2f}{Col.RESET}")
    print(f"{Col.NEON_PINK}{'═' * 80}{Col.RESET}\n")

def main():
    global active_users, use_proxy_mode

    print_banner()

    print_section_header("🔧 CONFIGURATION")

    proxy_choice = input(f"  {Col.YELLOW}Use proxies? (y/n): {Col.RESET}").strip().lower()
    use_proxy_mode = proxy_choice == 'y'

    if use_proxy_mode:
        print(f"  {Col.NEON_GREEN}✓ Proxy mode enabled{Col.RESET}")
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

    print_section_header("🔑 AUTHENTICATION")

    saved_sessions = load_sessions()
    sessions_to_save = {}

    for idx, (email, password) in enumerate(zip(emails, passwords)):
        proxy = None
        if use_proxy_mode and proxies:
            proxy = proxies[idx % len(proxies)]

        session, dashboard_token = perform_dashboard_login(email, password, proxy, saved_sessions)
        if not session:
            print(f"{Col.RED}✗ Failed to login {mask_email(email)}, skipping...{Col.RESET}")
            continue

        sessions_to_save[email] = {
            'session': session,
            'token': dashboard_token,
            'timestamp': time.time()
        }

        ext_token = perform_extension_auth(email, password, proxy)
        if not ext_token:
            print(f"{Col.RED}✗ Extension auth failed for {mask_email(email)}, skipping...{Col.RESET}")
            continue

        farm_session = create_farming_session(ext_token, proxy)
        geo_info = setup_validator_node(farm_session)

        user_data = {
            'email': email,
            'password': password,
            'proxy': proxy,
            'session': session,
            'dashboard_token': dashboard_token,
            'farm_session': farm_session,
            'geo_info': geo_info,
            'start_time': time.time(),
            'next_checkin': time.time(),
            'optimal_interval': MIN_SYNC_INTERVAL,
            'fail_count': 0,
            'total_shares': 0,
            'total_points': 0,
            'interval_history': deque(maxlen=10)
        }
        active_users.append(user_data)
        print(f"  {Col.NEON_GREEN}✓ {mask_email(email)} ready{Col.RESET}\n")

    if sessions_to_save:
        save_sessions(sessions_to_save)

    if not active_users:
        print(f"{Col.RED}✗ No users successfully authenticated{Col.RESET}")
        sys.exit(1)

    print_section_header("🚀 STARTING FARMING")
    print(f"  {Col.NEON_GREEN}Active Accounts: {len(active_users)}{Col.RESET}")
    print(f"  {Col.PURPLE}Adaptive Sync: {'Enabled' if ADAPTIVE_SYNC else 'Disabled'}{Col.RESET}")
    print(f"  {Col.CYAN}Base Interval: {BASE_FARM_INTERVAL}s{Col.RESET}\n")

    cycle_count = 0
    last_stats_display = time.time()

    while True:
        cycle_count += 1
        print(f"\n{Col.NEON_BLUE}{'─' * 80}{Col.RESET}")
        print(f"{Col.BOLD}{Col.NEON_PINK}  🔄 CYCLE #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Col.RESET}")
        print(f"{Col.NEON_BLUE}{'─' * 80}{Col.RESET}\n")

        for user_data in active_users:
            if time.time() >= user_data.get('next_checkin', 0):
                task_checkin(user_data)

            task_farming_and_monitor(user_data)
            time.sleep(2)

        if time.time() - last_stats_display >= 300:
            display_stats_summary()
            last_stats_display = time.time()

        min_interval = min([user.get('optimal_interval', BASE_FARM_INTERVAL) for user in active_users])
        wait_time = max(min_interval, BASE_FARM_INTERVAL)

        print(f"\n{Col.DIM}[{get_time()}]{Col.RESET} {Col.YELLOW}⏸{Col.RESET} {Col.PURPLE}SYSTEM{Col.RESET} │ Waiting {Col.ORANGE}{wait_time}s{Col.RESET} for next cycle...")
        time.sleep(wait_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Col.NEON_PINK}{'═' * 80}{Col.RESET}")
        print(f"{Col.YELLOW}  ⚠ Bot stopped by user{Col.RESET}")
        display_stats_summary()
        print(f"{Col.NEON_BLUE}  👋 Thank you for using Namso Farming Bot!{Col.RESET}")
        print(f"{Col.NEON_PINK}{'═' * 80}{Col.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Col.RED}✗ Fatal error: {e}{Col.RESET}")
        sys.exit(1)
