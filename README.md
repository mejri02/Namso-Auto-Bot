# Namso Farming Bot v3.0

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.0-brightgreen)](https://github.com/mejri02/Namso-Auto-Bot)

An advanced automated bot for **Namso Network** that handles authentication, smart farming, RPS games, badge claiming, task completion, token refresh, health checks, and daily check-ins with full proxy support.

👉 **Join Namso Network here:** https://app.namso.network/dashboard/

> 🙏 **Support the project — use referral code: `EDFE26389CB9` when signing up!**

---

## ✨ What's New in v3.0

- 🔁 **Smart Token Refresh** – Uses the new `refreshConn` endpoint to silently refresh tokens without requiring a full re-authentication, falling back to full re-auth only if refresh fails
- 🔌 **Expanded API Endpoints** – Now leverages 16 dedicated sentry API endpoints including `syncState`, `proofGen`, `signMaker`, `consensusRep`, `networkPerf`, `queryTable`, and more
- 🖥️ **Server Config Fetching** – Pulls per-account server configuration via `fetchConfig` at startup for optimized node setup
- 🔢 **Robust Share Value Parsing** – New `parse_share_value()` function handles string-formatted share values (e.g. `"1,234.56 SHARE"`) without crashing
- 💾 **Refresh Token Persistence** – Refresh tokens are now saved to `sessions.dat` and restored on relaunch, reducing OTP prompts
- 🔄 **Smarter Re-auth Flow** – Health check failures now attempt a silent token refresh before falling back to full credential re-authentication
- ⏱️ **Per-Account Task Throttling** – Badges, tasks, and RPS checks are now individually timestamped per account to avoid redundant API calls each cycle
- 🎮 **RPS Games** – Full automated Rock Paper Scissors gameplay with win/loss/second-chance handling
- 🏆 **Badge Claiming** – Auto-detects and claims all eligible badges
- 📋 **Task Completion** – Auto-completes eligible tasks (skips social click tasks)
- 📊 **Quality Monitor** – Tracks valid vs invalid contributions with live quality percentage
- 🧠 **Adaptive Smart Sync** – Dynamically adjusts farming intervals based on reputation, server hints, and online validator count

---

## Features

- 🔐 **Auto Authentication** – Dashboard and extension login with OTP support
- 🌾 **Auto Farming** – Continuous farming with health checks and enhanced task submissions
- 🔁 **Token Refresh** – Silent refresh via `refreshConn`, full re-auth as fallback
- 🎮 **RPS Games** – Automated Rock Paper Scissors with second-chance retry on losses
- 🏆 **Badge Claiming** – Auto-detects and claims eligible badges
- 📋 **Task Completion** – Auto-completes eligible tasks
- 📊 **Real-time Monitoring** – Live stats (Shares, Points, Reputation, Quality %, Uptime)
- ✅ **Daily Check-in** – Automated daily check-ins with streak tracking
- 💾 **Session Saving** – Persistent sessions and refresh tokens to skip OTP on relaunch
- 🌐 **Proxy Support** – Optional proxy rotation with live connection testing
- ⚡ **Multi-Account** – Unlimited account support
- 🔄 **Random User Agents** – Anti-detection with rotating user agents
- 📍 **Geo Detection** – Auto-detects IP location for validator node setup

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

Both `|` and `:` separators are supported:
```
email@example.com|password123
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
(Account 1 → Proxy 1, Account 2 → Proxy 2, etc.). If there are fewer proxies than accounts, proxies are reused in rotation.

> ⚠️ Cloudflare may block datacenter proxies. Residential proxies are recommended for best results.

---

## Usage

Run the bot:
```bash
python bot.py
```

1. Choose whether to use proxies (`y/n`)
2. The bot loads credentials from `accounts.txt`
3. Existing sessions are checked first — if valid, OTP is skipped
4. Enter OTP codes when prompted for fresh logins
5. The bot runs initial tasks (check-in, badges, tasks, RPS) for all accounts
6. Continuous farming begins automatically

---

## Bot Intervals

| Parameter | Value | Description |
|---|---|---|
| `BASE_FARM_INTERVAL` | 60s | Base cycle interval |
| `CHECKIN_INTERVAL` | 86400s | Daily check-in (24 hours) |
| `MIN_SYNC_INTERVAL` | 300s | Minimum farming sync |
| `MAX_SYNC_INTERVAL` | 600s | Maximum farming sync |
| `ADAPTIVE_SYNC` | True | Smart interval adjustment |

The bot dynamically adjusts sync intervals based on:
- Your current reputation score
- Server-provided `next_sync` hints
- Number of online validators
- Recent farming success/failure rate

---

## API Endpoints

v3.0 uses 16 dedicated sentry API endpoints:

| Endpoint | Purpose |
|---|---|
| `connectAuth` | Initial authentication |
| `refreshConn` | Silent token refresh |
| `taskSubmit` | Farming task submission |
| `healthCheck` | Session health verification |
| `fetchStatus` | Node status retrieval |
| `fetchConfig` | Per-account server config |
| `syncState` | State synchronization |
| `proofGen` | Proof generation |
| `signMaker` | Request signing |
| `consensusRep` | Consensus reporting |
| `networkPerf` | Network performance |
| `queryTable` | Data queries |
| `sessionRefresh` | Session renewal |
| `secureChannel` | Secure comms |
| `payloadCheck` | Payload validation |
| `disconnect` | Clean disconnection |

---

## Console Output

Color-coded real-time status:

- 🟢 **Green** – Successful operations (farming, wins, claims)
- 🔴 **Red** – Errors or failures
- 🟡 **Yellow** – Warnings, rate limits, or pending actions
- 🔵 **Cyan** – Account identifiers
- 🟣 **Purple** – Task type labels (FARMING, CHECK-IN, RPS, etc.)
- 🟠 **Orange** – Intervals and proxy info
- ⚪ **White** – Values (shares, points)

### Example Output
```
[12:34:56] ● FARMING │ exa***@mail.com │ Online │ SHR: 1,234.5678 │ PTS: 89.50 │ REP: 91.2 │ QLTY: 98.5% │ ⏱ 2h 15m │ Next: 300s
[12:34:58] 🏆 BADGE CLAIMED │ exa***@mail.com │ Early Adopter
[12:35:00] 🎮 RPS │ exa***@mail.com │ WON MATCH │ +50 SHARE
[12:35:02] ✓ SYSTEM │ exa***@mail.com │ Token refreshed
```

---

## Stats Summary

Every 5 minutes the bot displays a full summary table including:
- Per-account: Shares, Points, Reputation, Quality %, Check-in Streak, Validator Count, Uptime
- Totals: Total Shares, Total Points, Average Reputation, Average Quality, Total Validators

---

## Troubleshooting

**OTP Not Received**
- Check spam/junk folder
- Verify email in `accounts.txt`
- Wait a few minutes and retry

**Session Expired**
- Delete `sessions.dat` to force a fresh login with OTP

**Token Expired / Re-auth Loop**
- Bot first attempts a silent refresh via `refreshConn`
- Falls back to full re-authentication if refresh fails
- If persistent, verify credentials in `accounts.txt`

**Proxy Issues**
- Check proxy format in `proxy.txt`
- Prefer residential proxies over datacenter proxies
- Try running without proxy (`n` at startup prompt)

**Low Validator Quality Warning**
- Quality below 80% triggers a warning
- Check your network stability and proxy reliability

**Share Value Parsing Errors**
- v3.0 includes robust parsing for string-formatted share values
- If you see parsing issues, ensure you're running the latest version

---

## Security Notes

⚠️ Keep `accounts.txt`, `proxy.txt`, and `sessions.dat` private  
⚠️ Never share credentials, tokens, or refresh tokens  
⚠️ Use strong, unique passwords  
⚠️ Add these files to `.gitignore` before pushing to any repository  

---

## Disclaimer

This project is for **educational purposes only**.  
Use at your own risk. The author is not responsible for bans, losses, or account actions.  
Always follow Namso Network's Terms of Service.

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

