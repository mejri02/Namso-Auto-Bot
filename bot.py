import requests
import json
import time
import sys
import uuid
import random
import os
from datetime import datetime, timezone, timedelta
from fake_useragent import UserAgent

class Col:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    LIME = '\033[1;32m'
    RED = '\033[91m'
    ORANGE = '\033[38;5;208m'
    YELLOW = '\033[93m'
    GOLD = '\033[38;5;220m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    PINK = '\033[38;5;206m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    RESET = '\033[0m'

BANNER = f"""
{Col.PINK}{Col.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ███╗   ██╗ █████╗ ███╗   ███╗███████╗ ██████╗          ║
║  ████╗  ██║██╔══██╗████╗ ████║██╔════╝██╔═══██╗         ║
║  ██╔██╗ ██║███████║██╔████╔██║███████╗██║   ██║         ║
║  ██║╚██╗██║██╔══██║██║╚██╔╝██║╚════██║██║   ██║         ║
║  ██║ ╚████║██║  ██║██║ ╚═╝ ██║███████║╚██████╔╝         ║
║  ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝          ║
║                                                          ║
║  ᴠᴇʀsɪᴏɴ 2.0 | sᴏᴄᴋs5/ʜᴛᴛᴘ | ʀᴀɴᴅᴏᴍ ᴜᴀ | ᴀᴜᴛᴏ ғᴀʀᴍɪɴɢ    ║
╚══════════════════════════════════════════════════════════╝
{Col.RESET}
"""

FARM_INTERVAL = 60
CHECKIN_INTERVAL = 86400
active_users = []
MIN_SYNC_INTERVAL = 300
ua = UserAgent()

def print_banner():
    print(BANNER)

def read_file_lines(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def mask_email(email):
    if "@" in email:
        parts = email.split("@")
        user = parts[0]
        domain = parts[1]
        if len(user) > 3:
            masked = f"{user[:3]}{'*' * min(5, len(user)-3)}@{domain}"
        else:
            masked = f"{user}{'*' * (len(user)-1)}@{domain}"
        return f"{Col.CYAN}{masked}{Col.RESET}"
    return email

def mask_proxy(proxy):
    if not proxy:
        return f"{Col.GREEN}Direct{Col.RESET}"
    try:
        if "@" in proxy:
            host_port = proxy.split("@")[-1]
            if proxy.startswith('socks5://'):
                return f"{Col.YELLOW}socks5://***@{host_port}{Col.RESET}"
            elif proxy.startswith('http://'):
                return f"{Col.YELLOW}http://***@{host_port}{Col.RESET}"
            elif proxy.startswith('https://'):
                return f"{Col.YELLOW}https://***@{host_port}{Col.RESET}"
            else:
                return f"{Col.YELLOW}***@{host_port}{Col.RESET}"
        else:
            return f"{Col.YELLOW}{proxy}{Col.RESET}"
    except:
        return f"{Col.RED}Proxy Error{Col.RESET}"

def get_time():
    wib = timezone(timedelta(hours=7))
    current_time = datetime.now(wib).strftime('%H:%M:%S')
    return f"{Col.MAGENTA}[{current_time}]{Col.RESET}"

def get_random_useragent():
    return ua.random

def setup_proxy_session(session, proxy):
    if proxy:
        if proxy.startswith('socks5://'):
            proxy = proxy.replace('socks5://', '')
            if '@' in proxy:
                auth, hostport = proxy.split('@')
                user, password = auth.split(':')
                host, port = hostport.split(':')
                session.proxies = {
                    'http': f'socks5://{user}:{password}@{host}:{port}',
                    'https': f'socks5://{user}:{password}@{host}:{port}'
                }
            else:
                host, port = proxy.split(':')
                session.proxies = {
                    'http': f'socks5://{host}:{port}',
                    'https': f'socks5://{host}:{port}'
                }
        elif proxy.startswith('http://') or proxy.startswith('https://'):
            session.proxies.update({'http': proxy, 'https': proxy})
        else:
            session.proxies.update({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
    return session

def perform_dashboard_login(email, password, proxy):
    session = requests.Session()
    session = setup_proxy_session(session, proxy)
    
    headers = {
        "authority": "app.namso.network",
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://app.namso.network",
        "referer": "https://app.namso.network/",
        "user-agent": get_random_useragent()
    }
    session.headers.update(headers)
    
    url_login = "https://app.namso.network/login.php"
    
    masked_email = mask_email(email)
    masked_proxy = mask_proxy(proxy)
    
    print(f"{Col.BLUE}╔══════════════════════════════════════════════════════════╗{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.GOLD}Login Dashboard{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.WHITE}Email: {masked_email}{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.WHITE}Proxy: {masked_proxy}{Col.RESET}")
    print(f"{Col.BLUE}╚══════════════════════════════════════════════════════════╝{Col.RESET}")
    
    try:
        print(f"    {Col.YELLOW}↻ Authenticating...{Col.RESET}")
        session.post(url_login, json={"email": email, "password": password, "action": "validate_credentials"})
        session.post(url_login, json={"email": email, "action": "send_otp"})
        
        print(f"    {Col.GOLD}✉ OTP Sent to email{Col.RESET}")
        otp_code = input(f"    {Col.GOLD}↳ Enter OTP for {email.split('@')[0]}: {Col.RESET}")
        
        res3 = session.post(url_login, json={"email": email, "password": password, "otp": otp_code, "action": "login"})
        data = res3.json()
        
        if data.get("success") is True or data.get("status") == "success":
            print(f"    {Col.LIME}✓ Dashboard Login Successful!{Col.RESET}")
            dashboard_token = data.get('token') or data.get('access_token')
            return session, dashboard_token
        else:
            print(f"    {Col.RED}✗ Login Failed: {data.get('message', 'Unknown error')}{Col.RESET}")
            return None, None
    except Exception as e:
        print(f"    {Col.RED}✗ Error: {e}{Col.RESET}")
        return None, None

def perform_extension_auth(email, password, proxy):
    url = "https://sentry-api.namso.network/devv/api/connectAuth"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "chrome-extension://ccdooaopgkfbikbdiekinfheklhbemcd",
        "user-agent": get_random_useragent()
    }
    
    proxies_dict = None
    if proxy:
        proxies_dict = {'http': proxy, 'https': proxy}
    
    try:
        res = requests.post(url, json={"email": email, "password": password}, 
                           headers=headers, proxies=proxies_dict, timeout=15)
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
    session = setup_proxy_session(session, proxy)
    
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
        "sec-ch-ua": f'"Chromium";v="{random.randint(120, 130)}", "Google Chrome";v="{random.randint(120, 130)}", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": f'"{random.choice(["Windows", "macOS", "Linux"])}"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "sec-fetch-storage-access": "active",
        "user-agent": get_random_useragent()
    }
    session.headers.update(headers)
    return session

def setup_validator_node(session):
    base_info = {
        "device_id": str(uuid.uuid4()),
        "version": f"1.{random.randint(0, 5)}.{random.randint(0, 9)}",
        "uptime": 0
    }
    
    ip_address = None
    
    try:
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": get_random_useragent()
        }
        
        r = session.get("https://api.ipify.org?format=json", headers=headers, timeout=10)
        
        if r.status_code == 200:
            ip_address = r.json().get('ip')
            print(f"    {Col.LIME}[Validator] IP: {ip_address}{Col.RESET}")
    except Exception as e:
        print(f"    {Col.RED}[Validator] Error getting IP: {e}{Col.RESET}")
    
    if not ip_address:
        try:
            r = session.get("https://ipinfo.io/json", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                ip_address = data.get('ip')
                print(f"    {Col.LIME}[Validator] IP from ipinfo: {ip_address}{Col.RESET}")
        except:
            pass
    
    if not ip_address:
        print(f"    {Col.RED}[Validator] CRITICAL: No IP detected!{Col.RESET}")
        return {"ip": "0.0.0.0", "city": "Unknown", "country": "XX"}
    
    try:
        r = session.get(f"https://ipinfo.io/{ip_address}/json", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            base_info.update({
                "ip": data.get('ip', ip_address),
                "city": data.get('city', 'Unknown'),
                "region": data.get('region', 'Unknown'),
                "country": data.get('country', 'XX'),
                "loc": data.get('loc', '0,0'),
                "org": data.get('org', 'Unknown'),
                "timezone": data.get('timezone', 'UTC')
            })
            print(f"    {Col.LIME}[Validator] Location: {data.get('city')}, {data.get('country')}{Col.RESET}")
            return base_info
    except Exception as e:
        print(f"    {Col.RED}[Validator] Error: {e}{Col.RESET}")
    
    return {"ip": ip_address, "city": "Unknown", "country": "XX"}

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
            color = Col.LIME
            symbol = "✓"
            status = "Success"
            print(f"{get_time()} {Col.BLUE}[CHECK-IN]{Col.RESET} {masked} | {color}{symbol} {status}{Col.RESET}")
        elif "already" in str(msg).lower():
            color = Col.GOLD
            symbol = "⏭"
            status = "Already"
            next_checkin = user_data.get('next_checkin', time.time())
            remaining = int(next_checkin - time.time())
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            print(f"{get_time()} {Col.BLUE}[CHECK-IN]{Col.RESET} {masked} | {color}{symbol} {status} (Next in {hours}h {minutes}m){Col.RESET}")
        else:
            color = Col.RED
            symbol = "✗"
            status = "Failed"
            print(f"{get_time()} {Col.BLUE}[CHECK-IN]{Col.RESET} {masked} | {color}{symbol} {status}{Col.RESET}")
            
    except Exception as e:
        print(f"{get_time()} {Col.BLUE}[CHECK-IN]{Col.RESET} {masked} | {Col.RED}✗ Error{Col.RESET}")

def task_farming_and_monitor(user_data):
    farm_session = user_data['farm_session']
    masked = mask_email(user_data['email'])
    email = user_data['email']
    password = user_data['password']
    proxy = user_data['proxy']
    
    if not farm_session:
        print(f"{get_time()} {Col.ORANGE}[SYSTEM]{Col.RESET} {masked} | {Col.YELLOW}↻ Creating session...{Col.RESET}")
        new_token = perform_extension_auth(email, password, proxy)
        if new_token:
            user_data['farm_session'] = create_farming_session(new_token, proxy)
            farm_session = user_data['farm_session']
            user_data['geo_info'] = setup_validator_node(farm_session)
            user_data['start_time'] = time.time()
            print(f"{get_time()} {Col.ORANGE}[SYSTEM]{Col.RESET} {masked} | {Col.LIME}✓ Session created{Col.RESET}")
        else:
            print(f"{get_time()} {Col.ORANGE}[SYSTEM]{Col.RESET} {masked} | {Col.RED}✗ Session failed{Col.RESET}")
            return
    
    url_health = "https://sentry-api.namso.network/devv/api/healthCheck"
    url_task = "https://sentry-api.namso.network/devv/api/taskSubmit"
    
    farming_success = False
    shares = "N/A"
    points_today = "N/A"
    need_relogin = False
    
    try:
        health_res = farm_session.post(url_health, timeout=15)
        
        if health_res.status_code == 401:
            need_relogin = True
            raise Exception("Token expired")
        
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
            else:
                error_msg = data.get('error', 'Unknown')
                if 'too frequent' in error_msg.lower():
                    user_data['optimal_interval'] = MIN_SYNC_INTERVAL
                elif 'invalid session' in error_msg.lower() or 'session' in error_msg.lower():
                    need_relogin = True
                else:
                    print(f"    {Col.RED}[Error] {error_msg}{Col.RESET}")
        elif res_submit.status_code == 401:
            need_relogin = True
            raise Exception("Token expired")
        else:
            print(f"    {Col.RED}[Error] Status {res_submit.status_code}{Col.RESET}")
    
    except Exception as e:
        error_msg = str(e)
        if "401" not in error_msg and "Token" not in error_msg:
            print(f"    {Col.RED}[Error] {error_msg[:100]}{Col.RESET}")
    
    if not farming_success:
        user_data['fail_count'] = user_data.get('fail_count', 0) + 1
        
        if user_data['fail_count'] >= 2 or need_relogin:
            print(f"{get_time()} {Col.ORANGE}[SYSTEM]{Col.RESET} {masked} | {Col.RED}↻ Refreshing token...{Col.RESET}")
            new_token = perform_extension_auth(email, password, proxy)
            if new_token:
                user_data['farm_session'] = create_farming_session(new_token, proxy)
                user_data['geo_info'] = setup_validator_node(user_data['farm_session'])
                user_data['start_time'] = time.time()
                user_data['fail_count'] = 0
                print(f"{get_time()} {Col.ORANGE}[SYSTEM]{Col.RESET} {masked} | {Col.LIME}✓ Token refreshed{Col.RESET}")
    else:
        user_data['fail_count'] = 0
    
    elapsed = int(time.time() - user_data.get('start_time', time.time()))
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    uptime_str = f"{hours}h {minutes}m"
    
    if farming_success:
        shares_str = f"{shares:,.4f}" if isinstance(shares, (int, float)) else str(shares)
        points_str = f"{points_today:.2f}" if isinstance(points_today, (int, float)) else str(points_today)
        
        bar_length = 20
        filled = int(bar_length * (elapsed % 300) / 300)
        bar = f"{Col.GREEN}{'█' * filled}{Col.WHITE}{'░' * (bar_length - filled)}{Col.RESET}"
        
        print(f"{get_time()} {Col.GREEN}[FARM]{Col.RESET} {masked} | {Col.LIME}✓{Col.RESET} | "
              f"{Col.CYAN}SHARES: {shares_str}{Col.RESET} | "
              f"{Col.GOLD}TODAY: {points_str}{Col.RESET} | "
              f"{Col.MAGENTA}UPTIME: {uptime_str}{Col.RESET} | {bar}")
    else:
        if need_relogin:
            status = "Token Expired"
        else:
            status = "Failed"
        print(f"{get_time()} {Col.RED}[FARM]{Col.RESET} {masked} | {Col.RED}✗ {status}{Col.RESET} | "
              f"{Col.YELLOW}Retrying...{Col.RESET} | "
              f"{Col.MAGENTA}UPTIME: {uptime_str}{Col.RESET}")

def print_statistics(users):
    print(f"\n{Col.BLUE}╔══════════════════════════════════════════════════════════╗{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.GOLD}📊 BOT STATISTICS{Col.RESET}")
    print(f"{Col.BLUE}╠══════════════════════════════════════════════════════════╣{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.WHITE}Total Accounts: {Col.CYAN}{len(users)}{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.WHITE}Farming Interval: {Col.GREEN}{FARM_INTERVAL}s{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.WHITE}Check-in Interval: {Col.GOLD}24h{Col.RESET}")
    
    proxies = [u['proxy'] for u in users if u['proxy']]
    if proxies:
        print(f"{Col.BLUE}║ {Col.WHITE}Using Proxies: {Col.LIME}Yes ({len(proxies)} accounts){Col.RESET}")
        socks5_count = sum(1 for p in proxies if p.startswith('socks5://'))
        http_count = sum(1 for p in proxies if p.startswith('http://'))
        https_count = sum(1 for p in proxies if p.startswith('https://'))
        print(f"{Col.BLUE}║ {Col.WHITE}SOCKS5: {Col.CYAN}{socks5_count}{Col.RESET} | "
              f"{Col.WHITE}HTTP: {Col.CYAN}{http_count}{Col.RESET} | "
              f"{Col.WHITE}HTTPS: {Col.CYAN}{https_count}{Col.RESET}")
    else:
        print(f"{Col.BLUE}║ {Col.WHITE}Using Proxies: {Col.RED}No{Col.RESET}")
    print(f"{Col.BLUE}╚══════════════════════════════════════════════════════════╝{Col.RESET}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    try:
        from fake_useragent import UserAgent
    except ImportError:
        print(f"{Col.RED}Error: fake-useragent not installed!{Col.RESET}")
        print(f"{Col.YELLOW}Run: pip install fake-useragent{Col.RESET}")
        sys.exit(1)
    
    print(f"{Col.GOLD}Select Proxy Mode:{Col.RESET}")
    print(f"{Col.CYAN}[1]{Col.RESET} {Col.GREEN}With Proxy (SOCKS5/HTTP/HTTPS){Col.RESET}")
    print(f"{Col.CYAN}[2]{Col.RESET} {Col.YELLOW}Direct Connection{Col.RESET}")
    
    choice = input(f"\n{Col.GOLD}→ Select [1/2]: {Col.RESET}")
    
    use_proxy = (choice == '1')
    print()
    
    raw_accs = read_file_lines("accounts.txt")
    if not raw_accs:
        print(f"{Col.RED}✗ accounts.txt is empty!{Col.RESET}")
        sys.exit()
    
    raw_proxies = []
    if use_proxy:
        raw_proxies = read_file_lines("proxy.txt")
        if not raw_proxies:
            print(f"{Col.ORANGE}⚠ proxy.txt is empty, switching to direct connection{Col.RESET}")
            use_proxy = False
    
    print(f"{Col.BLUE}╔══════════════════════════════════════════════════════════╗{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.GOLD}🚀 INITIALIZING ACCOUNTS{Col.RESET}")
    print(f"{Col.BLUE}╚══════════════════════════════════════════════════════════╝{Col.RESET}\n")
    
    for i, line in enumerate(raw_accs):
        parts = line.split(':')
        if len(parts) >= 2:
            email = parts[0]
            password = parts[1]
            
            current_proxy = None
            if use_proxy and i < len(raw_proxies):
                current_proxy = raw_proxies[i]
            
            print(f"{Col.CYAN}[{i+1}/{len(raw_accs)}] {mask_email(email)}{Col.RESET}")
            
            result = perform_dashboard_login(email, password, current_proxy)
            if result:
                session_dash, dashboard_token = result
            else:
                session_dash, dashboard_token = None, None
            
            token_ext = perform_extension_auth(email, password, current_proxy)
            final_token = dashboard_token if dashboard_token else token_ext
            
            session_farm = None
            geo_info = {}
            if final_token:
                print(f"    {Col.LIME}✓ Login successful{Col.RESET}")
                session_farm = create_farming_session(final_token, current_proxy)
                geo_info = setup_validator_node(session_farm)
                print(f"    {Col.LIME}✓ Ready | IP: {geo_info.get('ip', 'Unknown')}{Col.RESET}\n")
            else:
                print(f"    {Col.RED}✗ Login failed{Col.RESET}\n")
            
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
    
    if not active_users:
        print(f"{Col.RED}✗ No valid accounts to process{Col.RESET}")
        sys.exit()
    
    print_statistics(active_users)
    
    print(f"\n{Col.BLUE}╔══════════════════════════════════════════════════════════╗{Col.RESET}")
    print(f"{Col.BLUE}║ {Col.GOLD}🚀 STARTING FARMING LOOP{Col.RESET}")
    print(f"{Col.BLUE}╚══════════════════════════════════════════════════════════╝{Col.RESET}\n")
    
    try:
        while True:
            current_time = time.time()
            for user in active_users:
                if current_time >= user['next_farm']:
                    task_farming_and_monitor(user)
                    interval = user.get('optimal_interval', FARM_INTERVAL)
                    user['next_farm'] = current_time + interval
                
                if user['session'] and current_time >= user['next_checkin']:
                    task_checkin(user)
                    user['next_checkin'] = current_time + CHECKIN_INTERVAL
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Col.RED}✗ Bot stopped.{Col.RESET}")
