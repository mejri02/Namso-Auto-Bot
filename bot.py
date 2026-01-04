import requests
import json
import time
import sys
import uuid
import random
from datetime import datetime, timezone, timedelta

class Col:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

FARM_INTERVAL = 60
CHECKIN_INTERVAL = 86400
active_users = []
MIN_SYNC_INTERVAL = 300

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

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
        return "Direct"
    try:
        if "@" in proxy:
            return proxy.split("@")[1]
        return proxy
    except:
        return "Proxy"

def get_time():
    wib = timezone(timedelta(hours=7))
    return datetime.now(wib).strftime('%H:%M:%S')

def parse_proxy(proxy_str):
    """Parse proxy string into proper format"""
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

def perform_dashboard_login(email, password, proxy):
    session = requests.Session()

    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            print(f"    {Col.YELLOW}Using proxy: {mask_proxy(proxy_url)}{Col.RESET}")
            session.proxies.update({
                'http': proxy_url,
                'https': proxy_url
            })

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

    masked_email = mask_email(email)
    masked_proxy = mask_proxy(proxy) if proxy else "Direct"
    print(f"{Col.CYAN}--- [1] Dashboard Login: {masked_email} | IP: {masked_proxy} ---{Col.RESET}")

    try:
        session.post(url_login, json={"email": email, "password": password, "action": "validate_credentials"})
        session.post(url_login, json={"email": email, "action": "send_otp"})
        print(f"    {Col.YELLOW}OTP sent to email.{Col.RESET}")

        otp_code = input(f"    {Col.YELLOW}Enter OTP for {masked_email}: {Col.RESET}")

        res3 = session.post(url_login, json={"email": email, "password": password, "otp": otp_code, "action": "login"})
        data = res3.json()

        if data.get("success") is True or data.get("status") == "success":
            print(f"    {Col.GREEN}Dashboard Login Successful!{Col.RESET}")
            dashboard_token = data.get('token') or data.get('access_token')
            return session, dashboard_token
        else:
            print(f"    {Col.RED}Dashboard Failed: {data}{Col.RESET}")
            return None, None
    except Exception as e:
        print(f"    {Col.RED}Dashboard Error: {e}{Col.RESET}")
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
        print(f"    {Col.RED}Extension Auth Error: {e}{Col.RESET}")
    return None

def create_farming_session(token, proxy):
    session = requests.Session()

    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            session.proxies.update({'http': proxy_url, 'https': proxy_url})

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "content-type": "application/json",
        "host": "sentry-api.namso.network",
        "origin": "chrome-extension://ccdooaopgkfbikbdiekinfheklhbemcd",
        "pragma": "no-cache",
        "sec-ch-ua": random.choice([
            '"Chromium";v="122", "Google Chrome";v="122", "Not_A Brand";v="99"',
            '"Chromium";v="121", "Google Chrome";v="121", "Not_A Brand";v="99"',
        ]),
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": random.choice(['"Windows"', '"macOS"']),
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "user-agent": get_random_user_agent(),
    }
    session.headers.update(headers)
    return session

def get_ip_with_proxy(session):
    """Get IP address using session's proxy"""
    try:
        test_urls = [
            "https://api.ipify.org?format=json",
            "https://api64.ipify.org?format=json",
            "https://icanhazip.com",
            "https://checkip.amazonaws.com"
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
        print(f"    {Col.RED}[IP Check] Error: {e}{Col.RESET}")

    return None

def setup_validator_node(session):
    base_info = {
        "device_id": str(uuid.uuid4()),
        "version": "1.0." + str(random.randint(1, 5)),
        "uptime": 0
    }

    ip_address = get_ip_with_proxy(session)

    if ip_address:
        print(f"    {Col.GREEN}[Validator] IP: {ip_address}{Col.RESET}")

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
                print(f"    {Col.GREEN}[Validator] Location: {data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}{Col.RESET}")
                return base_info
        except:
            pass
    else:
        print(f"    {Col.YELLOW}[Validator] IP detection failed - using default{Col.RESET}")

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
            color = Col.GREEN
            status = "✓ Success"
        elif "already" in str(msg).lower():
            color = Col.YELLOW
            status = "⏭ Already"
            next_checkin_time = user_data.get('next_checkin', time.time())
            remaining = int(next_checkin_time - time.time())
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            msg = f"Already checked in (Next in {hours}h {minutes}m)"
        else:
            color = Col.RED
            status = "✗ Failed"

        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {color}[CHECK-IN]{Col.RESET} {Col.WHITE}{masked}{Col.RESET} | {color}{status}{Col.RESET} | {msg}")
    except Exception as e:
        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.RED}[CHECK-IN]{Col.RESET} {Col.WHITE}{masked}{Col.RESET} | Error: {str(e)[:50]}")

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
            print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.YELLOW}[SYSTEM]{Col.RESET} {masked} | Ext Login OK")
            user_data['geo_info'] = setup_validator_node(farm_session)
            user_data['start_time'] = time.time()
        else:
            print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.YELLOW}[FARMING]{Col.RESET} {masked} | SKIP")
            return

    url_health = "https://sentry-api.namso.network/devv/api/healthCheck"
    url_task = "https://sentry-api.namso.network/devv/api/taskSubmit"

    need_relogin = False
    farming_success = False
    rate_limited = False
    server_error = False
    shares = "N/A"
    points_today = "N/A"

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
            print(f"    {Col.RED}[Error] Server error (500){Col.RESET}")
            raise Exception("Server error")

        if res_submit.status_code == 200:
            data = res_submit.json()
            if data.get('success'):
                farming_success = True
                shares = data.get('shares', 'N/A')
                points_today = data.get('points_today', 'N/A')

                next_sync = data.get('next_sync')
                if next_sync:
                    next_sync_time = next_sync - int(time.time())
                    if next_sync_time > 0:
                        user_data['optimal_interval'] = next_sync_time
                        print(f"    {Col.GREEN}[Info] Next sync in {next_sync_time}s{Col.RESET}")
            else:
                error_msg = data.get('error', 'Unknown')
                if 'too frequent' in error_msg.lower() or 'sync' in error_msg.lower():
                    rate_limited = True
                    user_data['optimal_interval'] = MIN_SYNC_INTERVAL
                    print(f"    {Col.YELLOW}[Warning] {error_msg} - Next sync in {MIN_SYNC_INTERVAL}s{Col.RESET}")
                elif 'invalid session' in error_msg.lower() or 'session' in error_msg.lower():
                    need_relogin = True
                    print(f"    {Col.RED}[Error] {error_msg} - Re-authenticating...{Col.RESET}")
                else:
                    print(f"    {Col.RED}[Error] {error_msg}{Col.RESET}")
        else:
            print(f"    {Col.RED}[Error] Status {res_submit.status_code}{Col.RESET}")

    except Exception as e:
        error_msg = str(e)
        if "401" not in error_msg and "Token" not in error_msg and "Server error" not in error_msg:
            print(f"    {Col.RED}[Error] {error_msg[:100]}{Col.RESET}")

    if not farming_success:
        user_data['fail_count'] = user_data.get('fail_count', 0) + 1

        if user_data['fail_count'] >= 3 and not need_relogin:
            print(f"    {Col.YELLOW}[Warning] Multiple failures - Forcing token refresh{Col.RESET}")
            need_relogin = True
            user_data['fail_count'] = 0
    else:
        user_data['fail_count'] = 0

    if need_relogin:
        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.RED}[SYSTEM]{Col.RESET} {masked} | Session Invalid - Re-authenticating...")
        new_token = perform_extension_auth(email, password, proxy)
        if new_token:
            user_data['farm_session'] = create_farming_session(new_token, proxy)
            user_data['geo_info'] = setup_validator_node(user_data['farm_session'])
            user_data['start_time'] = time.time()
            print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.GREEN}[SYSTEM]{Col.RESET} {masked} | Token Refreshed")

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

                        next_sync = data.get('next_sync')
                        if next_sync:
                            next_sync_time = next_sync - int(time.time())
                            if next_sync_time > 0:
                                user_data['optimal_interval'] = next_sync_time
            except Exception as retry_err:
                print(f"    {Col.RED}[Error] Retry failed: {str(retry_err)[:50]}{Col.RESET}")

    elapsed = int(time.time() - user_data.get('start_time', time.time()))
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    uptime_str = f"{hours}h {minutes}m"

    if farming_success:
        if isinstance(shares, (int, float)):
            shares_str = f"{shares:,.4f}"
        else:
            shares_str = str(shares)

        if isinstance(points_today, (int, float)):
            points_str = f"{points_today:.2f}"
        else:
            points_str = str(points_today)

        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.GREEN}[FARMING]{Col.RESET} {Col.WHITE}{masked}{Col.RESET} | {Col.GREEN}✓ Online{Col.RESET} | SHARES: {shares_str} | Today: {points_str} | Uptime: {uptime_str}")
    elif rate_limited:
        next_interval = user_data.get('optimal_interval', MIN_SYNC_INTERVAL)
        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.YELLOW}[FARMING]{Col.RESET} {Col.WHITE}{masked}{Col.RESET} | {Col.YELLOW}⏳ Rate Limited{Col.RESET} | Next sync in {next_interval}s | Uptime: {uptime_str}")
    elif server_error:
        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.YELLOW}[FARMING]{Col.RESET} {Col.WHITE}{masked}{Col.RESET} | {Col.RED}⚠ Server Error{Col.RESET} | Will retry next cycle | Uptime: {uptime_str}")
    else:
        status_text = "Token Expired" if need_relogin else "✗ Failed"
        print(f"{Col.CYAN}[{get_time()}]{Col.RESET} {Col.YELLOW}[FARMING]{Col.RESET} {Col.WHITE}{masked}{Col.RESET} | {Col.RED}{status_text}{Col.RESET} | Will retry | Uptime: {uptime_str}")

if __name__ == "__main__":
    print(f"\n{Col.CYAN}=== NAMSO BOT: AUTO FARMING ==={Col.RESET}\n")

    print("1. Run With Proxy")
    print("2. Run Without Proxy")
    choice = input("Choose [1/2] -> ")

    use_proxy = (choice == '1')
    print()

    raw_accs = read_file_lines("accounts.txt")
    if not raw_accs:
        print(f"{Col.RED}File accounts.txt is empty!{Col.RESET}")
        sys.exit()

    raw_proxies = []
    if use_proxy:
        raw_proxies = read_file_lines("proxy.txt")
        if not raw_proxies:
            print(f"{Col.YELLOW}Warning: proxy.txt is empty.{Col.RESET}\n")
            use_proxy = False

    for i, line in enumerate(raw_accs):
        parts = line.split(':')
        if len(parts) >= 2:
            email = parts[0]
            password = parts[1]

            current_proxy = None
            if use_proxy and i < len(raw_proxies):
                current_proxy = raw_proxies[i]
                print(f"{Col.YELLOW}Account {i+1} using: {mask_proxy(current_proxy)}{Col.RESET}")

            result = perform_dashboard_login(email, password, current_proxy)

            if result:
                session_dash, dashboard_token = result
            else:
                session_dash, dashboard_token = None, None

            print(f"{Col.CYAN}--- [2] Extension Login ---{Col.RESET}")
            token_ext = perform_extension_auth(email, password, current_proxy)

            final_token = dashboard_token if dashboard_token else token_ext

            session_farm = None
            geo_info = {}
            if final_token:
                print(f"    {Col.GREEN}Login Successful!{Col.RESET}")
                session_farm = create_farming_session(final_token, current_proxy)
                print(f"    {Col.YELLOW}Setting up Node...{Col.RESET}")
                geo_info = setup_validator_node(session_farm)
                print(f"    {Col.GREEN}Ready! IP: {geo_info.get('ip')}{Col.RESET}\n")
            else:
                print(f"    {Col.RED}Login Failed.{Col.RESET}\n")

            user_data = {
                "email": email,
                "password": password,
                "proxy": current_proxy,
                "session": session_dash,
                "farm_session": session_farm,
                "geo_info": geo_info,
                "start_time": time.time(),
                "next_checkin": time.time(),
                "next_farm": time.time(),
                "optimal_interval": FARM_INTERVAL,
                "fail_count": 0
            }
            active_users.append(user_data)
        else:
            print(f"{Col.RED}Wrong format in accounts.txt{Col.RESET}")

    if not active_users:
        sys.exit()

    print(f"{Col.CYAN}=== Auto Loop ({len(active_users)} Accounts) ==={Col.RESET}")
    print(f"{Col.YELLOW}Base Interval: {FARM_INTERVAL} seconds{Col.RESET}")
    print(f"{Col.YELLOW}Note: Interval will adjust based on server response{Col.RESET}\n")

    try:
        while True:
            current_time = time.time()
            for user in active_users:
                if current_time >= user['next_farm']:
                    task_farming_and_monitor(user)
                    user['next_farm'] = current_time + user.get('optimal_interval', FARM_INTERVAL)

                if current_time >= user['next_checkin']:
                    task_checkin(user)
                    user['next_checkin'] = current_time + CHECKIN_INTERVAL

            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{Col.RED}Bot stopped by user.{Col.RESET}")
        sys.exit()
