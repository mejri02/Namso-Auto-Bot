# Namso Auto Bot

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated bot for **Namso Network** that handles authentication, farming, monitoring, and daily check-ins with proxy support.

👉 **Join Namso Network here:** https://app.namso.network/dashboard/

---

## Features

- 🔐 **Auto Authentication** – Automatic dashboard and extension login with OTP support
- 🌾 **Auto Farming** – Continuous farming with health checks and task submissions
- 🔄 **Token Refresh** – Automatic token refresh when expired (401 errors)
- 📊 **Real-time Monitoring** – Live stats display (SHARES, Daily Points, Validator Status)
- ✅ **Daily Check-in** – Automated daily check-ins (24-hour interval)
- 🌐 **Proxy Support** – Optional proxy rotation for multiple accounts
- 🎨 **Colorful Console** – Easy-to-read colored output 
- ⚡ **Multi-Account** – Support for multiple accounts
- 🔄 **Random User Agents** – Anti-detection with random user agent rotation
- ⏱️ **Randomized Intervals** – Varied timing patterns to reduce detection risk

---

## Prerequisites

- Python 3.7 or higher
- Active Namso Network accounts
- Valid email access for OTP verification
- Basic understanding of proxies (optional)

---

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mejri02/Namso-Auto-Bot.git
cd Namso-Auto-Bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure your accounts and proxies (see **Configuration** below)

---

## Configuration

### accounts.txt

Add your Namso accounts in the following format (one per line):

```
email@example.com:password123
another@example.com:pass456
```

### proxy.txt (Optional)

Add your proxies in the following format (one per line):

```
http://username:password@ip:port
http://ip:port
socks5://username:password@ip:port
username:password@ip:port
ip:port:username:password
```

**Note:** Each account is assigned a proxy sequentially 
(Account 1 → Proxy 1, Account 2 → Proxy 2, etc.)

---

## Usage

Run the bot:
```bash
python bot.py
```

Choose your mode:
- Option 1: Run with smart proxy rotation
- Option 2: Run without proxy
- Option 3: Test proxies only

Enter OTP codes when prompted.
The bot will then start automatic farming and monitoring.

---

## Bot Intervals

- Base Farming Interval: **60 seconds** (±20% random variation)
- Daily Check-in Interval: **86400 seconds** (24 hours ±10%)

You can modify these values in `bot.py`:
```python
BASE_FARM_INTERVAL = 60
BASE_CHECKIN_INTERVAL = 86400
MIN_SYNC_INTERVAL = 300
```

---

## Console Output

Color-coded real-time status:

- 🟢 Green – Successful operations
- 🔴 Red – Errors or failures
- 🟡 Yellow – Warnings or pending actions
- 🔵 Cyan – Informational headers
- ⚪ White – Account identifiers

---

## Troubleshooting

**OTP Not Received**
- Check spam/junk folder
- Verify email in `accounts.txt`
- Wait a few minutes and retry

**Token Expired**
- Automatically refreshed
- If persistent, verify credentials

**Proxy Issues**
- Check proxy format
- Test proxies using Option 3
- Try running without proxy

---

## Security Notes

⚠️ Keep `accounts.txt` and `proxy.txt` private
⚠️ Never share credentials or tokens
⚠️ Use strong, unique passwords
⚠️ Update passwords regularly

---

## Disclaimer

This project is for **educational purposes only**.
Use at your own risk. The author is not responsible for bans, losses, or account actions.
Always follow Namso Network’s Terms of Service.

---

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License**.

---

Created and maintained by **@mejri02**

⭐ Star this repository if you find it useful!
