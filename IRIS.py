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
    elif not auto_open:
        print()
        if ask("Open all hits in browser","n").lower()=='y':
            for ip,_,_ in hits:
                try: webbrowser.open(f"http://{ip}",new=2); time.sleep(0.2)
                except: pass
            ok("Opened")
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