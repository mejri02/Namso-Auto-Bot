```markdown
# Namso Auto Bot

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated bot for Namso Network that handles authentication, farming, monitoring, and daily check-ins with proxy support.

**Namso Dashboard:** https://app.namso.network/dashboard/

**Referral Code:** `EDFE26389CB9` (Use this when signing up to support the developer!)

## Features

- 🔐 **Auto Authentication** - Automatic dashboard and extension login with OTP support
- 🌾 **Auto Farming** - Continuous farming with health checks and task submissions
- 🔄 **Token Refresh** - Automatic token refresh when expired (401 errors)
- 📊 **Real-time Monitoring** - Live stats display (SHARES, Daily Points, Validator Status)
- ✅ **Daily Check-in** - Automated daily check-ins (24-hour interval)
- 🌐 **Proxy Support** - Optional proxy rotation for multiple accounts
- 🎨 **Colorful Console** - Easy-to-read colored output
- ⚡ **Multi-Account** - Support for unlimited accounts
- 🔄 **Random User Agents** - Anti-detection with random user agent rotation
- ⏱️ **Randomized Intervals** - Varied timing patterns to avoid detection

## Prerequisites

- Python 3.7 or higher
- Active Namso Network accounts (Use referral code: `EDFE26389CB9`)
- Valid email access for OTP verification
- Basic understanding of proxies (optional)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mejri02/Namso-Auto-Bot.git
cd Namso-Auto-Bot
```

1. Install required packages:

```bash
pip install -r requirements.txt
```

1. Configure your accounts and proxies (see Configuration section)

Configuration

accounts.txt

Add your Namso accounts in the following format (one per line):

```
email@example.com:password123
another@example.com:pass456
```

proxy.txt (Optional)

Add your proxies in the following format (one per line):

```
http://username:password@ip:port
http://ip:port
socks5://username:password@ip:port
username:password@ip:port
ip:port:username:password
```

Note: Each account will be assigned to a proxy in order (Account 1 → Proxy 1, Account 2 → Proxy 2, etc.)

Usage

1. Run the bot:

```bash
python bot.py
```

1. Choose your mode:
   · Option 1: Run with smart proxy rotation (tests and rotates proxies)
   · Option 2: Run without proxy (direct connection)
   · Option 3: Test proxies only (verify proxy functionality)
2. Enter OTP codes when prompted for each account
3. The bot will start automatic farming and monitoring

Bot Intervals

· Base Farming Interval: 60 seconds (with ±20% random variation)
· Check-in Interval: 86400 seconds (24 hours with ±10% random variation)

You can modify these values in the bot.py file:

```python
BASE_FARM_INTERVAL = 60       # Base farming interval in seconds
BASE_CHECKIN_INTERVAL = 86400 # Base check-in interval in seconds
MIN_SYNC_INTERVAL = 300       # Minimum sync interval when rate limited
```

Console Output

The bot displays real-time information with color-coded status:

· 🟢 Green: Successful operations (Online, Login Success)
· 🔴 Red: Errors or failures (Token Expired, Server Errors)
· 🟡 Yellow: Warnings or pending actions (Rate Limit, OTP Request)
· 🔵 Cyan: Information headers and timestamps
· ⚪ White: Account identifiers

Status Indicators

· ✓ Online: Farming is active and working properly
· ⏳ Rate Limited: Too many requests, temporary cooldown
· ⚠ Server Error: Namso server issues (500 errors)
· Token Expired: Session token needs refresh (auto-handled)
· Proxy Rotated: Proxy IP has been changed (anti-detection)

Features Breakdown

1. Dashboard Login

· Validates credentials with random user agents
· Sends OTP to registered email
· Authenticates with OTP code
· Maintains session for monitoring

2. Extension Authentication

· Automatic token generation with proxy support
· Bearer token authorization
· Auto-refresh on expiration with randomized delays
· Seamless reconnection

3. Farming Operations

· Health check pings with varied timing
· Task submission with anti-detection patterns
· Smart error handling and retry logic
· Automatic recovery from failures

4. Proxy Management

· Multiple proxy format support
· Proxy testing before use
· Automatic rotation (every hour)
· Failure detection and removal

5. Anti-Detection Features

· Random user agents for each request
· Randomized intervals (±20% variation)
· Human-like random delays
· Shuffled account processing order

Troubleshooting

OTP Not Received

· Check spam/junk folder
· Ensure email is correct in accounts.txt
· Wait a few minutes and try again

Token Expired Errors

· Bot automatically refreshes tokens
· If persistent, check account credentials
· Verify account is not banned

Proxy Connection Issues

· Verify proxy format is correct
· Use Option 3 to test proxies
· Try without proxy (Option 2)

Mining Stopped

· Check account status on Namso dashboard
· Verify validator requirements are met
· Review account activity limits

Multi-Account Detection

· Use different proxies for each account
· Enable random user agents (already enabled)
· Consider reducing number of accounts if issues persist

Security Notes

· ⚠️ Keep accounts.txt and proxy.txt private
· ⚠️ Never share your credentials or tokens
· ⚠️ Use strong, unique passwords for each account
· ⚠️ Consider using application-specific passwords
· ⚠️ Regularly update your passwords

Disclaimer

This bot is for educational purposes only. Use at your own risk. The author (@mejri02) is not responsible for any account actions, bans, or losses incurred from using this bot. Always follow Namso Network's terms of service.

Supporting the Developer

If you find this bot helpful, please:

1. Use my referral code when signing up: EDFE26389CB9
2. Star ⭐ this repository
3. Share with friends who might find it useful

Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

License

This project is open source and available under the MIT License.

Support

If you encounter issues or have questions:

· Open an issue on GitHub
· Check existing issues for solutions
· Provide detailed error logs when reporting

Changelog

Version 2.0.0

· Added random user agent support
· Implemented smart proxy rotation
· Added randomized intervals for anti-detection
· Improved error handling and recovery
· Added proxy testing mode

Version 1.0.0

· Initial release
· Multi-account support
· Basic proxy integration
· Auto token refresh
· Real-time monitoring
· Daily check-in automation

---

Star ⭐ this repository if you find it helpful!

Created and maintained by @mejri02

Namso Dashboard: https://app.namso.network/dashboard/

Referral Code: EDFE26389CB9

```
