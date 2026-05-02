# 👻 GhostPrint

> **OSINT CLI Tool** - Find digital footprints from a single identifier

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![OSINT](https://img.shields.io/badge/Category-OSINT-red)

## 🔍 What is GhostPrint?

GhostPrint is a lightweight, fast OSINT (Open Source Intelligence) CLI tool that aggregates intelligence from a single identifier:

- 📧 **Email** → Breach databases, social profiles, domains
- 👤 **Username** → Cross-platform presence, profile links
- 📱 **Phone** → Carrier info, social accounts, breaches
- 🌐 **Domain** → Subdomains, DNS records, WHOIS, technologies

## ⚡ Features

- **Fast**: Async requests for concurrent checks
- **Modular**: Easy to add new sources
- **JSON/CSV Export**: For further analysis
- **No API keys required** (where possible)
- **Privacy-focused**: No data sent to third parties

## 🚀 Quick Start

```bash
# Install
pip install ghostprint

# Email investigation
ghostprint email user@example.com

# Username investigation
gghostprint username johndoe

# Phone investigation
gghostprint phone +33612345678

# Domain investigation
gghostprint domain example.com

# Export results
gghostprint email user@example.com --export json --output report.json
```

## 📦 Installation

```bash
# From PyPI (when published)
pip install ghostprint

# From source
git clone https://github.com/toufik/ghostprint.git
cd ghostprint
pip install -e .
```

## 🛠️ Modules

| Module | Description | Status |
|--------|-------------|--------|
| `breaches` | Check HaveIBeenPwned for breaches | ✅ |
| `social` | Profile discovery across platforms | ✅ |
| `metadata` | EXIF/data extraction from URLs | 🚧 |
| `dns` | DNS enumeration and records | ✅ |
| `whois` | WHOIS lookup | ✅ |

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

**⚠️ Disclaimer**: This tool is for educational and authorized testing purposes only. Always respect privacy and legal boundaries.
