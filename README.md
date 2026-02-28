# IRIS
**Intelligent Reconnaissance & Infiltration System**

> This tool is provided for educational and research purposes only. Passive HTTP scanning of public IPs is legal in most jurisdictions. Accessing systems without authorization is not. Use responsibly.

IRIS is a multithreaded reconnaissance tool that probes random public IPs and surfaces exposed devices in real time. Cameras with no password, routers on default credentials, forgotten admin panels, live video streams, open DVRs. All of it is out there, sitting on the public internet, waiting. IRIS finds it.

If you want to understand what the internet actually looks like beneath the surface, this is probably the most direct way to do it. No account, no API key, no Shodan subscription. You run a scan, you see what's exposed. That's it.

![Python](https://img.shields.io/badge/python-3.7+-3572A5?style=flat-square)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/license-Custom-orange?style=flat-square)
![Version](https://img.shields.io/badge/version-3.1.0-brightgreen?style=flat-square)

## What it finds

IRIS sends a plain HTTP request to each IP and analyzes the response. It uses a database of 57 camera signatures, 32 IoT keywords and 49 vulnerability patterns to classify what comes back. Each hit is categorized:

**CAMERA** confirms a live camera or video stream. Hikvision, Dahua, Axis, Foscam, Reolink, Amcrest and 50+ other brands are in the database. When you get one of these you can usually open the IP directly in a browser and see the stream.

**FLAGGED** means multiple vulnerability patterns showed up at once. Default credentials, exposed config files, open directory listings. These are the interesting ones.

**AUTH_REQ** is a protected login page on an IoT device. Most of the time the credentials are still admin/admin or admin/password. IRIS flags it, you decide what to do with it.

**IOT** covers routers, modems, smart home devices, embedded web interfaces. Anything that responds like a networked device but doesn't fit the camera category.

**DETECTED** is a content or title match for a known device type that doesn't fall into the other categories.

Every hit is saved to a timestamped file automatically. You never lose results.

## Recommended setup

The best way to run IRIS is 10 000 IPs at 100 threads. That's the sweet spot.

100 threads keeps the scan stable without hammering your connection or running into timeout cascades. At that thread count you'll scan 10 000 IPs in roughly 3 to 5 minutes depending on your internet speed. In a single session you'll typically find anywhere from a handful to a few dozen hits depending on luck with the random IP pool.

If you want to go faster you can push threads up to 150 or 200. The results stay accurate, it just gets noisier on slow connections. Going above 200 threads starts producing more false timeouts than it's worth.

For a serious session, run 3 or 4 consecutive scans of 10 000 IPs. By the end you'll have scanned 40 000 random public IPs and have a solid list of exposed devices to browse through.

## Why this is actually the deep web

People talk about the deep web like it requires Tor and hidden services. The reality is that the most interesting stuff is sitting on the regular internet, completely public, just not indexed anywhere. Nobody is going to Google "Hikvision default password" and find your neighbor's outdoor camera. But it's there, responding to HTTP requests, accessible to anyone who looks.

IRIS looks. At scale. Across the entire IPv4 space, randomly. Every scan is different because the IPs are random. You never know if the next batch will include a warehouse camera in Eastern Europe, a router admin panel in Brazil, or a live feed from someone's front door in the US. That's what makes it compelling as an exploration tool rather than just a security scanner.

## Installation

```bash
git clone https://github.com/strykey/iris.git
cd iris
pip install -r requirements.txt
python iris.py
```

## Requirements

Python 3.7 or higher and an internet connection. Works on Linux, macOS and Windows.

```
requests
rich
```

That's the entire dependency list. No heavy frameworks, no system-level requirements.

## Usage

Run the script and you'll get the menu. Select Deep Scan, enter your target count (10 000 recommended) and thread count (100 recommended), and let it run. The progress bar shows hits in real time as they come in, color coded by category.

When the scan finishes you get a summary and a prompt to open all hits in your browser if you want. The results file is always saved regardless.

For the Batch Opener, just point it at any saved results file and it'll open every IP in a new tab with a configurable delay between them.

## Project structure

```
iris/
├── iris.py           # Main application
├── requirements.txt  # Dependencies
├── README.md         # This file
└── LICENSE           # Custom License
```
## Auto-updater

IRIS checks for updates automatically every time it starts. It downloads the latest version of the repo from GitHub, compares each file against your local copy using SHA-256 hashes, and replaces only the files that have changed. A backup of any overwritten file is saved in a `.backups/` folder next to the script before anything is touched. If an update is applied, IRIS restarts itself automatically so you are always running the latest version without doing anything manually. If you are offline or GitHub is unreachable, the check is skipped silently and IRIS starts normally.

### HTML scan report

At the end of every scan that finds at least one hit, IRIS automatically generates a `iris_report_TIMESTAMP.html` file in the same folder as the script. It opens in any browser and gives you a full breakdown of what was found.

The report includes a stats bar across the top with total IPs scanned, hits by category, hit rate and scan speed. Below that is a full table of every discovered target: IP as a clickable link, detection type, signature detail, country and city with flag, GPS coordinates, ISP, ASN, timezone, and tags for proxy / hosting / mobile networks. On the side you get a donut chart of the type distribution and a bar chart of the top countries represented in your hits.

There is a dark/light mode switch in the top right corner. The report works fully offline once generated, except for the country flags which load from an external CDN.

## Legal

This tool performs passive HTTP GET requests against public IP addresses. It does not exploit vulnerabilities, does not attempt authentication, and does not modify any remote system. It is equivalent to typing an IP address into a browser.

Accessing systems without authorization, even ones with no password, may be illegal depending on your jurisdiction. IRIS is a reconnaissance and research tool. The developers are not responsible for how you use it.

## Author

**Strykey**


*"The internet is bigger than what Google shows you."*


