# IRIS
### Intelligent Reconnaissance & Inspection Scanner

![Python](https://img.shields.io/badge/python-3.7+-3572A5?style=flat-square)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/license-Custom-orange?style=flat-square)
![Version](https://img.shields.io/badge/version-3.1.0-brightgreen?style=flat-square)

> **For educational and research purposes only.**
> Passive HTTP scanning of public IPs is legal in most jurisdictions.
> Accessing systems without authorization is not. Use responsibly.

IRIS is a multithreaded network research tool that scans random public IPv4 addresses and maps exposed HTTP services in real time. Think of it as a personal, lightweight version of what [Shodan](https://shodan.io) or [Censys](https://censys.io) do at a much larger scale. It sends a plain GET request to each IP, reads the response, and tells you what kind of device answered.

No account. No API key. Just raw network I/O and a signature database.

---

## Table of Contents

- [What it finds](#what-it-finds)
- [Why this exists](#why-this-exists)
- [Installation](#installation)
- [Usage](#usage)
- [Scan Report](#scan-report)
- [Auto-updater](#auto-updater)
- [Project structure](#project-structure)
- [Legal](#legal)

---

## What it finds

IRIS classifies every response into one of five categories based on response headers and page content. No authentication is ever attempted, no stream is accessed, no system is modified.

| Category | What it means |
|:---:|:---|
| `CAMERA` | Response matches a known camera signature (Hikvision, Dahua, Axis, Foscam, Reolink, Amcrest and 50+ others). Detection only, no stream is opened. |
| `IOT` | Router, modem, smart home hub or embedded web interface with a recognizable signature. |
| `AUTH_REQ` | Device responds with an authentication page. IRIS logs it exists. No login is attempted. |
| `FLAGGED` | Multiple exposure indicators in a single response (open directory listing, exposed config endpoint, etc). Logged for research only. |
| `DETECTED` | Content or title match for a known device type that does not fit the other categories. |

All results are automatically saved to a timestamped file at the end of each scan.

---

## Why this exists

Internet-wide scanning is a well-studied area of network security research. Tools like [Shodan](https://shodan.io), [Censys](https://censys.io) and [ZMap](https://zmap.io) have been doing this for years and are used by universities, security teams and governments to understand the attack surface of the public internet.

IRIS started as a learning project to understand how that kind of scanning works from the inside:

- How to handle multithreaded network I/O in Python at scale
- How HTTP response fingerprinting and signature matching works
- How exposed services are actually distributed across the IPv4 space
- How to build a clean reporting pipeline from raw scan data

The output is the same kind of information you would get from a free Shodan query. The goal is understanding the internet, not accessing anything on it.

---

## Installation

```bash
git clone https://github.com/strykey/iris.git
cd iris
pip install -r requirements.txt
python iris.py
```

**Requirements**

```
requests
rich
```

Python 3.7 or higher. Works on Linux, macOS and Windows. Two dependencies, that's it.

---

## Usage

Run the script and you get a menu. Pick **Deep Scan**, enter a target IP count and a thread count, and let it run. Results show up in real time, color coded by category.

**Recommended starting point:** 10 000 IPs at 100 threads. That's a good balance between coverage and stability on a typical home connection and takes around 3 to 5 minutes.

```
[ Deep Scan ]
  Target IPs   : 10000
  Threads      : 100
  Estimated    : ~4 min
```

When the scan finishes, results are saved automatically and you get a prompt to open everything in the browser via the Batch Opener.

---

## Scan Report

At the end of every scan that finds at least one hit, IRIS generates a `iris_report_TIMESTAMP.html` file. Open it in any browser.

The report includes:

- **Stats bar** at the top: total IPs scanned, hits by category, hit rate, scan speed
- **Full results table**: IP (clickable), detection type, signature detail, country, city, ISP, ASN, timezone, proxy/hosting/mobile tags
- **Donut chart** of detection type distribution
- **Bar chart** of top countries in the results
- **Dark / light mode toggle** in the top right corner

The report works fully offline once generated.

---

## Auto-updater

Every time IRIS starts, it checks GitHub for a newer version by comparing local file hashes (SHA-256) against the latest release. Only files that actually changed get replaced. Any overwritten file is backed up to `.backups/` first. If you are offline or GitHub is unreachable, the check is skipped silently and IRIS starts normally.

---

## Project structure

```
iris/
├── iris.py           # Main application
├── requirements.txt  # Dependencies
├── README.md         # This file
└── LICENSE           # License
```

---

## Legal

IRIS performs passive HTTP GET requests against public IP addresses. It does not exploit vulnerabilities, does not attempt authentication, and does not modify any remote system. It is equivalent to typing an IP address into your browser's address bar.

Passive scanning of public IP ranges is legal in most jurisdictions. Laws vary by country and users are responsible for complying with the rules that apply to their location.

Accessing any system without the owner's authorization, including systems with no password set, may be illegal under laws including the Computer Fraud and Abuse Act (US), the Computer Misuse Act (UK), and the French Code penal Art. 323-1. IRIS detects and catalogs. What you do with the results is on you.

---

## Author

**Strykey**

*"The internet is bigger than what Google shows you."*
