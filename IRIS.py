#!/usr/bin/env python3
"""IRIS - Intelligent Reconnaissance & Infiltration System | Strykey | v3.1.0 | Custom License"""

import sys, os, time, random, re, webbrowser
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, List

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from rich.text import Text
from rich import box

requests.packages.urllib3.disable_warnings()
console = Console()

IOT_KEYWORDS = [
    'login','admin','camera','webcam','dvr','nvr','ipcam','router','modem','iot',
    'device','control','dashboard','cctv','panel','interface','authentication',
    'username','password','stream','viewer','live','video','config','settings',
    'management','web interface','network','security','surveillance','monitor','access','remote'
]
CAMERA_SIGNATURES = [
    'ipcam','ip camera','network camera','webcamxp','blueiris','hikvision','dahua',
    'axis','vivotek','foscam','d-link','tp-link','xiaomi','wyze','arlo','nest','ring',
    'yi cam','video stream','mjpeg','rtsp','snapshot.cgi','videostream.cgi','dvr','nvr',
    'cctv','surveillance','video surveillance','cam_1','channel_1','live view','live.htm',
    'view.htm','image.jpg','tmpfs','webcam','netcam','viewer_index.shtml','h264','mpeg4',
    'video.cgi','mjpg','jpg/image.jpg','amcrest','reolink','annke','lorex','zmodo','swann',
    'geovision','mobotix','panasonic','samsung','sony','bosch','pelco','acti','arecont',
    'avigilon','camera web','videovigilancia','onvif','psia','gige','ptz','dome camera',
    'bullet camera','video encoder','video server','video recording','motion detection'
]
INTERESTING_PATTERNS = [
    'default password','admin/admin','change password','weak password','unauthorized access',
    'no authentication','public access','telnet','ftp server','ssh server','upnp','open port',
    'directory listing','index of /','parent directory','config.xml','config.ini',
    'configuration','setup.cgi','tomcat','apache','nginx','iis','server status','phpmyadmin',
    'adminer','cpanel','webmin','plesk','root@','user:pass','guest/guest','admin/password',
    'jenkins','grafana','kibana','elasticsearch','mongodb','redis','memcached','docker',
    'kubernetes','portainer','jupyter','airflow','gitlab','sonarqube','artifactory',
    'exposed','unsecured','backdoor','exploit','vulnerability'
]
SCAN_TIMEOUT, MIN_CONTENT, MAX_CONTENT, MIN_KW = 0.8, 50, 500000, 1

LOGO = (
    " ██╗ ██████╗  ██╗  ███████╗\n"
    " ██║ ██╔══██╗ ██║  ██╔════╝\n"
    " ██║ ██████╔╝ ██║  ███████╗\n"
    " ██║ ██╔══██╗ ██║       ██║\n"
    " ██║ ██║  ██║ ██║  ███████║\n"
    " ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚══════╝"
)
GLITCH_CHARS = list('▓▒░│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌')

def _strip(s): return re.sub(r'\033\[[0-9;]*m','',s)
def _c(code,t): return f"\033[{code}m{t}\033[0m"
def G(t): return _c("1;92",t)
def D(t): return _c("2;90",t)
def C(t): return _c("1;96",t)
def R(t): return _c("1;91",t)
def Y(t): return _c("1;93",t)
def W(t): return _c("97",  t)
def clr(): os.system('cls' if os.name=='nt' else 'clear')
def tw():
    try: return os.get_terminal_size().columns
    except: return 80
def ctr(text,w=0):
    w=w or tw(); plain=_strip(text); pad=max(0,(w-len(plain))//2)
    return ' '*pad+text
def wr(t): sys.stdout.write(t); sys.stdout.flush()
def wl(t=''): wr(t+'\n')

def glitch(line, intensity=0.3):
    return ''.join(random.choice(GLITCH_CHARS) if c!=' ' and random.random()<intensity else c for c in line)

def boot():
    clr(); w=tw(); lines=LOGO.split('\n')
    for _ in range(6):
        wl(D(''.join(random.choice('▓▒░ ') for _ in range(w)))); time.sleep(0.04)
    time.sleep(0.1); clr()
    for i in range(18):
        clr(); print()
        inten=max(0,0.65-i*0.037)
        for ln in lines:
            out=glitch(ln,inten) if inten>0 else ln
            wl(ctr(G(out) if i>=4 else D(out)))
        time.sleep(0.13)
    clr(); print()
    for ln in lines: wl(ctr(G(ln)))
    print()
    wl(ctr(C("Intelligent Reconnaissance & Infiltration System")))
    wl(ctr(D("v3.1.0  ·  Strykey  ·  2024–2026")))
    print()
    wl(ctr(D('─'*min(56,w-4)))); print()
    time.sleep(0.3)
    wl(ctr(G("IRIS online")))
    print(); time.sleep(0.4)

def banner():
    clr(); w=tw(); print()
    for ln in LOGO.split('\n'): wl(ctr(G(ln)))
    print()
    wl(ctr(C("Intelligent Reconnaissance & Infiltration System")))
    wl(ctr(D("v3.1.0  ·  Strykey  ·  2024–2026")))
    print()
    sep=D('─'*min(56,w-4))
    wl(ctr(sep))
    now=datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    wl(ctr(f"{D('◦')} {D('SESSION')} {G(now)}  {D('◦')}  {D('STATUS')} {G('ACTIVE')}"))
    wl(ctr(sep)); print()

def ask(prompt, default=''):
    wr(f"  {C('◈')} {W(prompt)}{D(f'  [{default}]') if default else ''}: ")
    r=input().strip()
    return r if r else default

def info(t):  wl(f"  {D('›')} {W(t)}")
def ok(t):    wl(f"  {G('✓')} {G(t)}")
def warn(t):  wl(f"  {Y('⚠')} {Y(t)}")
def err(t):   wl(f"  {R('✗')} {R(t)}")

def random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def scan_ip(ip: str) -> Tuple[str,bool,str,str]:
    try:
        r=requests.get(f"http://{ip}",timeout=SCAN_TIMEOUT,allow_redirects=False,
                       verify=False,headers={'User-Agent':'Mozilla/5.0'})
        s=r.status_code; body=r.text.lower(); cl=len(body); hdr=str(r.headers).lower()
        if s in [301,302,303,307,308,404,410,500,502,503,504]: return ip,False,f"HTTP_{s}","SKIP"
        if not(MIN_CONTENT<=cl<=MAX_CONTENT): return ip,False,"SIZE","SKIP"
        cc=sum(1 for sg in CAMERA_SIGNATURES if sg in body or sg in hdr)
        if cc: return ip,True,f"CAM×{cc}","CAMERA"
        ic=sum(1 for p in INTERESTING_PATTERNS if p in body)
        if ic>=2: return ip,True,f"FLAG×{ic}","FLAGGED"
        if s in [401,403]:
            if any(w in body for w in ['www-authenticate','login','authentication','username','password']):
                return ip,True,f"AUTH_{s}","AUTH_REQ"
            return ip,False,f"AUTH_{s}","SKIP"
        kc=sum(1 for k in IOT_KEYWORDS if k in body)
        if kc>=MIN_KW: return ip,True,f"IoT×{kc}","IOT"
        if any(sv in hdr for sv in ['boa','thttpd','mini_httpd','lighttpd','mongoose','goahead','micro_httpd']):
            return ip,True,"IOT_SRV","IOT"
        if any(w in body for w in ['camera','dvr','nvr','router','admin panel']) and s==200:
            return ip,True,"TITLE","DETECTED"
        return ip,False,"LOW","SKIP"
    except requests.exceptions.Timeout:        return ip,False,"TIMEOUT","SKIP"
    except requests.exceptions.ConnectionError: return ip,False,"REFUSED","SKIP"
    except:                                     return ip,False,"ERROR","SKIP"


def geolocate_hits(hits):
    ips = [ip for ip,_,_ in hits]
    geo = {}
    try:
        fields = "status,query,country,countryCode,regionName,city,isp,org,as,timezone,lat,lon,mobile,proxy,hosting"
        for i in range(0, len(ips), 100):
            batch = ips[i:i+100]
            r = requests.post(
                f"http://ip-api.com/batch?fields={fields}",
                json=batch, timeout=10,
                headers={"Content-Type":"application/json"}
            )
            for d in r.json():
                if d.get("status") == "success":
                    geo[d["query"]] = d
    except Exception:
        pass
    return geo

def generate_report(hits, total, elapsed, threads, ts):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path  = os.path.join(script_dir, f"iris_report_{ts}.html")
    dt_str     = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    geo = geolocate_hits(hits)

    label_colors = {
        "CAMERA":   "#ff4444",
        "FLAGGED":  "#ffcc00",
        "AUTH_REQ": "#ff8800",
        "IOT":      "#00ff88",
        "DETECTED": "#00ccff",
    }
    label_counts = {}
    for _, label, _ in hits:
        label_counts[label] = label_counts.get(label, 0) + 1

    country_counts = {}
    for ip,_,_ in hits:
        g = geo.get(ip,{})
        c = g.get("country","Unknown")
        country_counts[c] = country_counts.get(c,0)+1
    top_countries = sorted(country_counts.items(), key=lambda x:-x[1])[:8]

    rows_html = ""
    for ip, label, reason in hits:
        color = label_colors.get(label, "#ffffff")
        url   = f"http://{ip}"
        g     = geo.get(ip, {})
        flag  = g.get("countryCode","").lower()
        flag_img = f'<img src="https://flagcdn.com/16x12/{flag}.png" style="margin-right:5px;vertical-align:middle" onerror="this.style.display=\'none\'">' if flag else ""
        country  = g.get("country", "")
        city     = g.get("city", "")
        isp      = g.get("isp", "")
        org      = g.get("org","")
        asn      = g.get("as","")
        tz       = g.get("timezone","")
        lat      = g.get("lat","")
        lon      = g.get("lon","")
        mobile   = g.get("mobile",False)
        proxy    = g.get("proxy",False)
        hosting  = g.get("hosting",False)
        tags = ""
        if mobile:  tags += '<span class="tag tag-warn">MOBILE</span>'
        if proxy:   tags += '<span class="tag tag-danger">PROXY</span>'
        if hosting: tags += '<span class="tag tag-info">HOSTING</span>'

        geo_cell = ""
        if country:
            geo_cell = f'{flag_img}<b>{country}</b>'
            if city: geo_cell += f" / {city}"
        loc_cell = f'<span class="coords">{lat},{lon}</span>' if lat else ""
        isp_cell = f'<span class="isp-txt" title="{org}">{isp[:32]}</span>' if isp else ""
        as_cell  = f'<span class="as-txt">{asn[:20]}</span>' if asn else ""
        tz_cell  = f'<small>{tz}</small>' if tz else ""

        rows_html += f"""<tr>
          <td><a href="{url}" target="_blank" class="ip-link">{ip}</a></td>
          <td><span class="badge" style="background:{color}20;color:{color};border:1px solid {color}40">{label}</span></td>
          <td class="detail">{reason}</td>
          <td class="geo-cell">{geo_cell}<br>{loc_cell}</td>
          <td class="isp-cell">{isp_cell}<br>{as_cell}</td>
          <td>{tz_cell}</td>
          <td>{tags}</td>
          <td><a href="{url}" target="_blank" class="open-btn">OPEN</a></td>
        </tr>"""

    labels_js       = str(list(label_counts.keys()))
    values_js       = str(list(label_counts.values()))
    colors_js       = str([label_colors.get(l,"#888") for l in label_counts.keys()])
    country_labels  = str([c for c,_ in top_countries])
    country_values  = str([v for _,v in top_countries])
    hit_rate        = f"{len(hits)/total*100:.2f}" if total else "0"
    scan_rate       = f"{total/elapsed:.1f}" if elapsed else "0"
    cam_count       = label_counts.get("CAMERA",0)
    flag_count      = label_counts.get("FLAGGED",0)
    auth_count      = label_counts.get("AUTH_REQ",0)
    iot_count       = label_counts.get("IOT",0)+label_counts.get("DETECTED",0)
    proxy_ips       = sum(1 for ip,_,_ in hits if geo.get(ip,{}).get("proxy"))
    hosting_ips     = sum(1 for ip,_,_ in hits if geo.get(ip,{}).get("hosting"))

    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IRIS // {dt_str}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root[data-theme="dark"]{{
  --bg:#080b0d;--bg2:#0d1117;--bg3:#161b22;--bg4:#1c2128;
  --green:#00ff88;--cyan:#00ccff;--red:#ff4444;--yellow:#ffcc00;--orange:#ff8800;
  --dim:#3d4450;--dimtext:#6e7681;--text:#c9d1d9;--border:#21262d;
  --shadow:rgba(0,0,0,.4);--scan:rgba(0,255,136,.015)
}}
:root[data-theme="light"]{{
  --bg:#f6f8fa;--bg2:#ffffff;--bg3:#f0f2f5;--bg4:#e8eaed;
  --green:#1a7f37;--cyan:#0969da;--red:#cf222e;--yellow:#9a6700;--orange:#bc4c00;
  --dim:#d0d7de;--dimtext:#57606a;--text:#1f2328;--border:#d0d7de;
  --shadow:rgba(0,0,0,.08);--scan:transparent
}}
body{{background:var(--bg);color:var(--text);font-family:'Courier New',monospace;min-height:100vh;transition:background .3s,color .3s}}
.scanline{{position:fixed;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,var(--scan) 2px,var(--scan) 4px);pointer-events:none;z-index:9999}}

header{{border-bottom:1px solid var(--border);padding:20px 40px;display:flex;align-items:center;justify-content:space-between;background:var(--bg2);position:sticky;top:0;z-index:100;box-shadow:0 1px 8px var(--shadow)}}
.logo{{font-size:24px;font-weight:700;color:var(--green);letter-spacing:8px;text-shadow:0 0 20px rgba(0,255,136,.3)}}
[data-theme="light"] .logo{{text-shadow:none}}
.logo sub{{font-size:10px;color:var(--dimtext);letter-spacing:2px;display:block;margin-top:2px}}
.header-right{{display:flex;align-items:center;gap:20px}}
.meta{{text-align:right;font-size:11px;color:var(--dimtext);line-height:1.9}}
.meta b{{color:var(--text)}}

.theme-toggle{{background:var(--bg3);border:1px solid var(--border);border-radius:20px;padding:6px 14px;cursor:pointer;font-family:'Courier New',monospace;font-size:11px;color:var(--dimtext);display:flex;align-items:center;gap:6px;transition:.2s;letter-spacing:1px}}
.theme-toggle:hover{{border-color:var(--green);color:var(--green)}}

main{{padding:28px 40px;max-width:1500px;margin:0 auto}}

.stats-grid{{display:grid;grid-template-columns:repeat(8,1fr);gap:10px;margin-bottom:28px}}
.stat{{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:16px 12px;text-align:center;position:relative;overflow:hidden;transition:.2s;cursor:default}}
.stat:hover{{transform:translateY(-2px);box-shadow:0 4px 16px var(--shadow)}}
.stat::after{{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:var(--green)}}
.stat.red::after{{background:var(--red)}} .stat.yellow::after{{background:var(--yellow)}}
.stat.orange::after{{background:var(--orange)}} .stat.cyan::after{{background:var(--cyan)}}
.stat.dim::after{{background:var(--dimtext)}}
.stat-val{{font-size:26px;font-weight:700;color:var(--green);line-height:1;font-variant-numeric:tabular-nums}}
.stat.red .stat-val{{color:var(--red)}} .stat.yellow .stat-val{{color:var(--yellow)}}
.stat.orange .stat-val{{color:var(--orange)}} .stat.cyan .stat-val{{color:var(--cyan)}}
.stat.dim .stat-val{{color:var(--dimtext)}}
.stat-label{{font-size:9px;color:var(--dimtext);text-transform:uppercase;letter-spacing:2px;margin-top:5px}}

.grid-main{{display:grid;grid-template-columns:1fr 340px;gap:20px;margin-bottom:20px}}
.grid-side{{display:flex;flex-direction:column;gap:16px}}

.card{{background:var(--bg2);border:1px solid var(--border);border-radius:6px;overflow:hidden}}
.card-header{{padding:10px 18px;border-bottom:1px solid var(--border);font-size:10px;text-transform:uppercase;letter-spacing:3px;color:var(--dimtext);display:flex;align-items:center;gap:8px}}
.card-header::before{{content:"";width:5px;height:5px;border-radius:50%;background:var(--green);flex-shrink:0}}
.chart-wrap{{padding:20px;height:220px;display:flex;align-items:center;justify-content:center}}

.table-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:12px;white-space:nowrap}}
thead tr{{border-bottom:2px solid var(--border)}}
th{{padding:8px 14px;text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:2px;color:var(--dimtext);font-weight:500;background:var(--bg3)}}
tbody tr{{border-bottom:1px solid var(--border);transition:.1s}}
tbody tr:hover{{background:var(--bg3)}}
td{{padding:10px 14px;vertical-align:middle}}
.ip-link{{color:var(--cyan);text-decoration:none;font-family:'Courier New',monospace;font-size:13px;font-weight:600}}
.ip-link:hover{{color:var(--green);text-decoration:underline}}
.badge{{font-size:9px;padding:3px 7px;border-radius:3px;font-family:'Courier New',monospace;letter-spacing:1px;font-weight:700;white-space:nowrap}}
.detail{{color:var(--dimtext);font-size:11px}}
.geo-cell{{font-size:11px;color:var(--text)}}
.coords{{font-size:10px;color:var(--dimtext)}}
.isp-cell{{font-size:11px;color:var(--dimtext)}}
.as-txt{{font-size:10px}}
.tag{{font-size:9px;padding:2px 5px;border-radius:2px;margin-right:3px;font-weight:700;letter-spacing:.5px}}
.tag-warn{{background:rgba(255,204,0,.15);color:var(--yellow);border:1px solid rgba(255,204,0,.3)}}
.tag-danger{{background:rgba(255,68,68,.15);color:var(--red);border:1px solid rgba(255,68,68,.3)}}
.tag-info{{background:rgba(0,204,255,.15);color:var(--cyan);border:1px solid rgba(0,204,255,.3)}}
.open-btn{{color:var(--green);text-decoration:none;font-size:9px;letter-spacing:2px;border:1px solid rgba(0,255,136,.2);padding:4px 8px;border-radius:3px;transition:.15s;white-space:nowrap}}
.open-btn:hover{{background:var(--green);color:#000}}

.params-grid{{padding:14px 18px;font-size:11px;line-height:2;color:var(--dimtext)}}
.param-row{{display:flex;justify-content:space-between}}
.param-row b{{color:var(--text)}}

.bar-item{{margin-bottom:10px}}
.bar-label{{font-size:10px;color:var(--dimtext);display:flex;justify-content:space-between;margin-bottom:3px}}
.bar-label b{{color:var(--text)}}
.bar-bg{{background:var(--bg3);border-radius:2px;height:6px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:2px;background:var(--green);transition:width .6s ease}}

footer{{border-top:1px solid var(--border);padding:18px 40px;text-align:center;font-size:10px;color:var(--dimtext);margin-top:32px;letter-spacing:1px}}
@media(max-width:1200px){{.stats-grid{{grid-template-columns:repeat(4,1fr)}}.grid-main{{grid-template-columns:1fr}}}}
@media(max-width:700px){{.stats-grid{{grid-template-columns:repeat(2,1fr)}};header{{padding:16px 20px}};main{{padding:20px}}}}
</style>
</head>
<body>
<div class="scanline"></div>
<header>
  <div>
    <div class="logo">IRIS <span style="color:var(--dimtext);">//</span> REPORT
      <sub>INTELLIGENT RECONNAISSANCE & INFILTRATION SYSTEM</sub>
    </div>
  </div>
  <div class="header-right">
    <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">☀ LIGHT</button>
    <div class="meta">
      <div><b>DATE</b>&nbsp;&nbsp;{dt_str}</div>
      <div><b>SESSION</b>&nbsp;&nbsp;{ts}</div>
      <div><b>AUTHOR</b>&nbsp;&nbsp;Strykey</div>
    </div>
  </div>
</header>

<main>
<div class="stats-grid">
  <div class="stat"><div class="stat-val">{total:,}</div><div class="stat-label">IPs Scanned</div></div>
  <div class="stat"><div class="stat-val">{len(hits)}</div><div class="stat-label">Hits Total</div></div>
  <div class="stat red"><div class="stat-val">{cam_count}</div><div class="stat-label">Cameras</div></div>
  <div class="stat yellow"><div class="stat-val">{flag_count}</div><div class="stat-label">Flagged</div></div>
  <div class="stat orange"><div class="stat-val">{auth_count}</div><div class="stat-label">Auth Req</div></div>
  <div class="stat cyan"><div class="stat-val">{iot_count}</div><div class="stat-label">IoT</div></div>
  <div class="stat dim"><div class="stat-val">{proxy_ips}</div><div class="stat-label">Proxy IPs</div></div>
  <div class="stat cyan"><div class="stat-val">{hit_rate}%</div><div class="stat-label">Hit Rate</div></div>
</div>

<div class="grid-main">
  <div class="card">
    <div class="card-header">Discovered targets</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>IP</th><th>Type</th><th>Signature</th>
          <th>Location</th><th>ISP / ASN</th><th>Timezone</th><th>Tags</th><th></th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
  </div>

  <div class="grid-side">
    <div class="card">
      <div class="card-header">Type distribution</div>
      <div class="chart-wrap"><canvas id="donut"></canvas></div>
    </div>

    <div class="card">
      <div class="card-header">Top countries</div>
      <div style="padding:16px 18px">
        {"".join(f'<div class="bar-item"><div class="bar-label"><span><b>{c}</b></span><span>{v}</span></div><div class="bar-bg"><div class="bar-fill" style="width:{int(v/max(vv for _,vv in top_countries)*100)}%"></div></div></div>' for c,v in top_countries) if top_countries else "<div style='padding:8px;color:var(--dimtext);font-size:11px'>No geo data</div>"}
      </div>
    </div>

    <div class="card">
      <div class="card-header">Scan parameters</div>
      <div class="params-grid">
        <div class="param-row"><span>TARGETS</span><b>{total:,}</b></div>
        <div class="param-row"><span>THREADS</span><b>{threads}</b></div>
        <div class="param-row"><span>TIMEOUT</span><b>0.8s</b></div>
        <div class="param-row"><span>ELAPSED</span><b>{elapsed:.2f}s</b></div>
        <div class="param-row"><span>SCAN RATE</span><b>{scan_rate} ip/s</b></div>
        <div class="param-row"><span>HIT RATE</span><b>{hit_rate}%</b></div>
        <div class="param-row"><span>GEO RESOLVED</span><b>{len(geo)}/{len(hits)}</b></div>
        <div class="param-row"><span>HOSTING IPs</span><b>{hosting_ips}</b></div>
      </div>
    </div>
  </div>
</div>
</main>

<footer>IRIS v3.1.0&nbsp;&nbsp;·&nbsp;&nbsp;Strykey&nbsp;&nbsp;·&nbsp;&nbsp;{dt_str}&nbsp;&nbsp;·&nbsp;&nbsp;{len(hits)} targets across {total:,} probed IPs</footer>

<script>
function toggleTheme(){{
  var r=document.documentElement, t=r.getAttribute("data-theme");
  var isDark=t==="dark";
  r.setAttribute("data-theme",isDark?"light":"dark");
  document.getElementById("themeBtn").textContent=isDark?"☾ DARK":"☀ LIGHT";
  updateCharts(isDark);
}}
var textColor=function(){{return getComputedStyle(document.documentElement).getPropertyValue("--dimtext").trim()}};
var borderColor=function(){{return getComputedStyle(document.documentElement).getPropertyValue("--border").trim()}};

var donutChart = new Chart(document.getElementById("donut"),{{
  type:"doughnut",
  data:{{
    labels:{labels_js},
    datasets:[{{data:{values_js},backgroundColor:{colors_js}.map(c=>c+"33"),borderColor:{colors_js},borderWidth:2,hoverOffset:6}}]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    plugins:{{
      legend:{{position:"bottom",labels:{{color:"#6e7681",font:{{family:"Courier New",size:10}},padding:10,boxWidth:10}}}},
      tooltip:{{backgroundColor:"#161b22",borderColor:"#21262d",borderWidth:1,titleColor:"#00ff88",bodyColor:"#c9d1d9",titleFont:{{family:"Courier New"}},bodyFont:{{family:"Courier New"}}}}
    }},
    cutout:"68%"
  }}
}});

function updateCharts(wasDark){{
  var nc=wasDark?"#57606a":"#6e7681";
  donutChart.options.plugins.legend.labels.color=nc;
  donutChart.update();
}}
</script>
</body></html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html_path

LSTYLE={"CAMERA":"bold red","FLAGGED":"bold yellow","AUTH_REQ":"yellow","IOT":"bright_green","DETECTED":"bright_green"}

def scan_module():
    console.rule("[bright_green]DEEP SCAN[/]  ·  [dim]IoT / Device Reconnaissance[/]")
    print()
    try:
        num_ips=int(ask("Targets","500"))
        threads=min(300,max(1,int(ask("Threads","150"))))
        auto_open=ask("Auto-open hits in browser","n").lower()=='y'
    except ValueError: err("Invalid input"); return
    print()
    ips=[random_ip() for _ in range(num_ips)]
    ok(f"{len(ips)} targets queued  ·  {threads} threads")
    print()
    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    fname=os.path.join(os.path.dirname(os.path.abspath(__file__)),f"iris_{ts}.txt")
    with open(fname,'w') as f:
        f.write(f"IRIS Deep Scan  ·  {datetime.now()}\n{'='*60}\n\n")
    ok(f"Logging → {os.path.basename(fname)}"); print()
    hits=[]; cams=[]; done=0; total=len(ips); t0=time.time()
    browser=None
    if auto_open:
        for b in ('firefox','chrome'):
            try: browser=webbrowser.get(b); break
            except: pass
        if not browser: browser=webbrowser
    hits_tbl=Table(box=box.MINIMAL,show_header=True,header_style="dim",expand=True,border_style="bright_black")
    hits_tbl.add_column("IP",style="cyan",no_wrap=True,width=18)
    hits_tbl.add_column("TYPE",width=10)
    hits_tbl.add_column("DETAIL",style="dim")
    prog=Progress(
        SpinnerColumn(style="bright_green"),
        TextColumn("[bright_green]{task.description}"),
        BarColumn(bar_width=None,style="bright_black",complete_style="bright_green"),
        TextColumn("[white]{task.percentage:>5.1f}%"),
        TextColumn("[dim]{task.completed}/{task.total}"),
        TextColumn("[bright_green]hits:{task.fields[hits]}[/]  [red]cam:{task.fields[cams]}[/]"),
        TextColumn("[dim]{task.fields[rate]} ip/s"),
        TimeElapsedColumn(),
        expand=True
    )
    tid=prog.add_task("scanning",total=total,hits=0,cams=0,rate=0)
    def layout():
        g=Table.grid(expand=True); g.add_column()
        g.add_row(prog)
        if hits: g.add_row(hits_tbl)
        return Panel(g,border_style="bright_black",title="[dim]IRIS · scanning[/]",title_align="left")
    with Live(layout(),console=console,refresh_per_second=8,vertical_overflow="crop") as live:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures={ex.submit(scan_ip,ip):ip for ip in ips}
            for fut in as_completed(futures):
                ip,is_hit,reason,label=fut.result(); done+=1
                elapsed=time.time()-t0; rate=int(done/elapsed) if elapsed>0 else 0
                if is_hit:
                    hits.append((ip,label,reason))
                    if label=="CAMERA": cams.append(ip)
                    hits_tbl.add_row(ip,f"[{LSTYLE.get(label,'white')}]{label}[/]",reason)
                    with open(fname,'a') as f: f.write(f"http://{ip}  [{label}]  {reason}\n")
                    if auto_open and browser:
                        try:
                            (browser.open_new_tab if hasattr(browser,'open_new_tab')
                             else lambda u:browser.open(u,new=2))(f"http://{ip}")
                        except: pass
                prog.update(tid,completed=done,hits=len(hits),cams=len(cams),rate=rate)
                live.update(layout())
    elapsed=time.time()-t0
    print()
    console.rule("[dim]results[/]")
    rt=Table(box=box.SIMPLE,show_header=False,border_style="bright_black")
    rt.add_column(style="dim",width=14); rt.add_column(style="white")
    rt.add_row("SCANNED",   f"[white]{total}[/]")
    rt.add_row("HITS",      f"[bright_green]{len(hits)}[/]")
    rt.add_row("CAMERAS",   f"[red]{len(cams)}[/]" if cams else "[dim]0[/]")
    rt.add_row("FILTERED",  f"[dim]{total-len(hits)}[/]")
    rt.add_row("RATE",      f"[cyan]{total/elapsed:.1f} ip/s[/]")
    rt.add_row("ELAPSED",   f"[cyan]{elapsed:.2f}s[/]")
    rt.add_row("SAVED",     f"[dim]{os.path.basename(fname)}[/]" if hits else "[dim] [/]")
    console.print(Panel(rt,border_style="bright_black",title="[dim]scan summary[/]",title_align="left"))
    if not hits:
        warn("No targets found")
        try: os.remove(fname)
        except: pass
    else:
        html_path=generate_report(hits,total,elapsed,threads,ts)
        ok(f"Report: {os.path.basename(html_path)}")
        if not auto_open:
            print()
            if ask("Open all hits in browser","n").lower()=='y':
                for ip,_,_ in hits:
                    try: webbrowser.open(f"http://{ip}",new=2); time.sleep(0.2)
                    except: pass
                ok("Opened")
        print()
        if ask("Open HTML report","y").lower()=='y':
            webbrowser.open(f"file://{html_path}")
    print(); wr(f"  {D('Press ENTER…')}"); input()

def opener_module():
    console.rule("[bright_green]BATCH OPENER[/]  ·  [dim]Mass Target Browser[/]")
    print()
    path=ask("Target file path")
    try:
        with open(path) as f:
            raw=[l.strip() for l in f if l.strip() and not l.startswith(('=','#'))]
        urls=[u if u.startswith(('http://','https://')) else f'http://{u}' for u in raw]
        if not urls: warn("No valid URLs"); print(); wr(f"  {D('Press ENTER…')}"); input(); return
        ok(f"Loaded {len(urls)} targets")
        delay=float(ask("Delay between opens (s)","1.0"))
        print(); console.rule(style="bright_black")
        for i,url in enumerate(urls,1):
            wl(f"  {D(f'[{i:>4}/{len(urls)}]')}  {C('►')}  {W(url)}")
            webbrowser.open_new_tab(url); time.sleep(delay)
        print(); ok(f"Opened {len(urls)} targets")
    except FileNotFoundError: err(f"Not found: {path}")
    except Exception as e: err(str(e))
    print(); wr(f"  {D('Press ENTER…')}"); input()

def about_module():
    console.rule("[bright_green]ABOUT[/]  ·  [dim]IRIS System[/]")
    print()
    t=Table(box=box.SIMPLE,show_header=False,border_style="bright_black",expand=False)
    t.add_column(style="cyan dim",width=10); t.add_column(style="white")
    for k,v in [
        ("IRIS",    "Intelligent Reconnaissance & Infiltration System"),
        ("VERSION", "3.1.0"),
        ("AUTHOR",  "Strykey"),
        ("LICENSE", "Custom — see LICENSE file"),
        ("ENGINE",  "Multithreaded HTTP probe + IoT fingerprinting"),
        ("TARGETS", "Public IPs cameras, DVRs, NVRs, routers, exposed services"),
        ("THREADS", "Up to 300 concurrent workers"),
        ("CAM DB",  f"{len(CAMERA_SIGNATURES)} signatures"),
        ("IOT DB",  f"{len(IOT_KEYWORDS)} keywords  ·  {len(INTERESTING_PATTERNS)} patterns"),
    ]: t.add_row(k,v)
    console.print(Panel(t,border_style="bright_black",title="[dim]system info[/]",title_align="left"))
    print()
    wl(f"  {D('IRIS maps the exposed surface of the internet  ')}")
    wl(f"  {D('unsecured devices, open admin panels, forgotten streams.')}")
    wl(f"  {D('Use responsibly. Unauthorized access is illegal.')}")
    print(); wr(f"  {D('Press ENTER…')}"); input()

def menu():
    t=Table(box=box.SIMPLE_HEAD,show_header=False,border_style="bright_black",expand=False)
    t.add_column(style="cyan",width=4,justify="center")
    t.add_column(style="bold white",width=16)
    t.add_column(style="dim")
    for k,n,d in [
        ("1","DEEP SCAN",    "Mass IoT/device recon across random public IPs"),
        ("2","BATCH OPENER", "Open a saved hit list in your browser"),
        ("3","ABOUT",        "System info & database stats"),
        ("4","EXIT",         "Terminate session"),
    ]: t.add_row(f"[{k}]",n,d)
    console.print(Panel(t,border_style="bright_black",
                        title="[dim]menu[/]",title_align="left",
                        subtitle=f"[dim]{datetime.now().strftime('%H:%M:%S')}[/]"))

def run():
    boot()
    while True:
        banner(); menu()
        wr(f"{G('iris')} {D('@')} {C('shadow')} {D('›')} ")
        c=input().strip()
        if   c=='1': scan_module()
        elif c=='2': opener_module()
        elif c=='3': about_module()
        elif c in ('4','q','exit','quit'):
            clr(); print(); wl(ctr(G("[ SESSION TERMINATED ]"))); wl(ctr(D("IRIS v3.1.0"))); print(); sys.exit(0)
        else: err("Unknown command"); time.sleep(0.7)

if __name__=="__main__":
    try: run()
    except KeyboardInterrupt:
        print(); print()
        wl(ctr(Y("[ INTERRUPTED ]"))); wl(ctr(D("Cleaning up…"))); print(); sys.exit(0)
