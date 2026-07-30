"""
Search bbs.pinggu.org (经管之家) and read full thread content.
Auto-refreshes cookies if expired (Hermes Agent with Camofox).

Usage:
  python3 search-bbs-pinggu.py read <thread-url>     # Read thread with auto-refresh
  python3 search-bbs-pinggu.py login                  # Force re-login and refresh cookies
  python3 search-bbs-pinggu.py check                  # Check cookie validity
"""
import os, sys, re, json, time, html as html_mod
import urllib.request, urllib.parse

COOKIE_FILE = os.path.expanduser('~/.hermes/credentials/bbs-pinggu-cookies.txt')
LOGIN_FILE = os.path.expanduser('~/.hermes/credentials/bbs-pinggu-login.txt')
CAMOFOX_MANAGER = os.path.expanduser('~/.hermes/scripts/camofox-manager.sh')
CAMOFOX_PORT = 9377

# ─── Cookie helpers ───────────────────────────────────────────

def read_cookies():
    """Read cookies from file, return dict."""
    if not os.path.exists(COOKIE_FILE):
        return {}
    cookies = {}
    with open(COOKIE_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                cookies[k.strip()] = v.strip()
    return cookies

def write_cookies(cookies_str):
    """Write cookie string to file."""
    with open(COOKIE_FILE, 'w') as f:
        f.write(f"# bbs.pinggu.org login cookies (auto-refreshed)\n")
        f.write(f"# 最后更新: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for part in cookies_str.strip().split(';'):
            part = part.strip()
            if part and '=' in part:
                f.write(part + "\n")
    os.chmod(COOKIE_FILE, 0o600)

def cookies_valid():
    """Test if current cookies can read a thread. Returns bool."""
    cookies = read_cookies()
    if not cookies:
        return False
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(
            'https://bbs.pinggu.org/thread-7909828-1-1.html',
            headers={'User-Agent': 'Mozilla/5.0', 'Cookie': cookie_str}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        html = raw.decode('gbk', errors='replace')
        return bool(re.search(r'[\u4e00-\u9fff]{30,}', html))
    except Exception:
        return False

def camofox_api(method, path, body=None):
    """Call Camofox server API."""
    import http.client
    conn = http.client.HTTPConnection('localhost', CAMOFOX_PORT, timeout=30)
    b = json.dumps(body) if body else None
    conn.request(method, path, body=b, headers={'Content-Type': 'application/json'})
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f'Camofox {method} {path}: {resp.status}')
    return json.loads(data) if data else {}

def auto_refresh_cookies():
    """
    Log into bbs.pinggu.org via Camofox and extract fresh cookies.
    Returns True on success, False on failure.
    """
    if not os.path.exists(LOGIN_FILE):
        print("  ⏭️  Login file not found. Please re-export cookies manually:")
        print(f"     F12 → Application → Cookies → bbs.pinggu.org → write to {COOKIE_FILE}")
        return False

    # Read credentials
    creds = {}
    with open(LOGIN_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                creds[k.strip()] = v.strip()
    username = creds.get('username', '')
    password = creds.get('password', '')

    if not username or not password:
        print("  ❌ Login file has empty username or password")
        return False

    print("  🔄 Cookies expired. Auto-refreshing via Camofox...")
    import subprocess

    # Ensure Camofox is running
    subprocess.run(['bash', CAMOFOX_MANAGER, 'start'], capture_output=True)
    time.sleep(3)

    try:
        # Create tab and navigate to login page
        tab = camofox_api('POST', '/tabs', {
            'url': 'https://bbs.pinggu.org/member.php?mod=logging&action=login',
            'userId': 'cookie_refresher'
        })
        tab_id = tab.get('tabId')
        if not tab_id:
            raise RuntimeError('No tabId from Camofox')

        time.sleep(4)  # Wait for SPA to render

        # Evaluate JS: fill form, submit, wait, return cookies
        result = camofox_api('POST', f'/tabs/{tab_id}/evaluate', {
            'userId': 'cookie_refresher',
            'expression': f"""
(async () => {{
    await new Promise(r => setTimeout(r, 2000));
    let u = document.querySelector('input[name="username"], input[type="text"][placeholder*="账号"], input[type="text"][placeholder*="用户"]');
    let p = document.querySelector('input[name="password"], input[type="password"]');
    let btn = document.querySelector('button[type="submit"], .loginBtn, .loginBtn2, input[type="submit"], a[class*="login"]');
    if (!u || !p) return {{ error: 'login fields not found' }};
    u.value = '{username}'; u.dispatchEvent(new Event('input', {{bubbles:true}}));
    p.value = '{password}'; p.dispatchEvent(new Event('input', {{bubbles:true}}));
    if (btn) btn.click(); else p.dispatchEvent(new KeyboardEvent('keydown', {{key:'Enter'}}));
    await new Promise(r => setTimeout(r, 5000));
    return {{ cookies: document.cookie, url: window.location.href }};
}})()
"""
        })

        result_data = result.get('result', {})
        if isinstance(result_data, dict) and result_data.get('error'):
            print(f"  ❌ Login failed: {result_data['error']}")
            return False

        cookies_str = ''
        if isinstance(result_data, dict):
            cookies_str = result_data.get('cookies', '')

        if 'Z9M6_79fc_auth' not in cookies_str:
            print("  ❌ Login succeeded but no auth cookie found")
            return False

        write_cookies(cookies_str)

        # Verify
        if cookies_valid():
            print("  ✅ New cookies verified!")
            return True
        else:
            print("  ❌ New cookies failed verification")
            return False

    except Exception as e:
        print(f"  ❌ Auto-refresh error: {e}")
        return False

    finally:
        try:
            if tab_id:
                camofox_api('DELETE', f'/tabs/{tab_id}?userId=cookie_refresher')
        except Exception:
            pass
        subprocess.run(['bash', CAMOFOX_MANAGER, 'stop'], capture_output=True)

# ─── Thread reader ────────────────────────────────────────────

def extract_post_content(html_text):
    """Extract meaningful Chinese text from a bbs.pinggu.org thread page."""
    post_ids = re.findall(r'id="postmessage_(\d+)"', html_text)
    if not post_ids:
        return []
    first_id = post_ids[0]
    idx = html_text.find(f'id="postmessage_{first_id}"')
    if idx < 0:
        return []
    td_end = html_text.find('</td>', idx)
    if td_end < 0:
        td_end = idx + 10000
    segment = html_text[idx:td_end]
    blocks = re.findall(r'(?:[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]{4,}[^<]*?)(?=<|$)', segment)
    meaningful = []
    for b in blocks:
        clean = re.sub(r'\s+', ' ', b).strip()
        clean = html_mod.unescape(clean)
        if len(clean) > 20 and '赵安豆' not in clean and '微信' not in clean and 'invite' not in clean:
            meaningful.append(clean)
    return meaningful

def read_thread(url):
    """Read a bbs.pinggu.org thread, auto-refreshing cookies if needed."""
    # Step 1: Check cookies
    if not cookies_valid():
        if not auto_refresh_cookies():
            print("Error: Cannot read thread - cookies expired and auto-refresh failed.")
            return {'error': 'cookie_expired'}
    else:
        print("  ✅ Cookies valid")

    # Step 2: Read thread
    cookies = read_cookies()
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                     'Cookie': cookie_str}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
    except Exception as e:
        return {'error': str(e)}

    html_text = raw.decode('gbk', errors='replace')
    content = extract_post_content(html_text)
    title_match = re.search(r'<title>(.*?)</title>', html_text)
    title = html_mod.unescape(title_match.group(1)) if title_match else url

    return {
        'title': title,
        'url': url,
        'content': content,
        'total_paragraphs': len(content)
    }

# ─── Main ─────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  search-bbs-pinggu.py read <thread-url>   Read thread (auto-refresh cookies)")
        print("  search-bbs-pinggu.py check               Check cookie validity")
        print("  search-bbs-pinggu.py login               Force re-login")
        sys.exit(1)

    action = sys.argv[1]

    if action == 'check':
        valid = cookies_valid()
        print(f"Cookies valid: {valid}")
        sys.exit(0 if valid else 1)

    elif action == 'login':
        ok = auto_refresh_cookies()
        sys.exit(0 if ok else 1)

    elif action == 'read':
        url = sys.argv[2] if len(sys.argv) > 2 else input("URL: ")
        result = read_thread(url)
        if 'error' in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(f"\n== {result['title']} ==")
        print(f"URL: {result['url']}")
        print(f"Total paragraphs: {result['total_paragraphs']}")
        print("\n--- Content ---")
        for p in result['content'][:30]:
            print(f"\n{p[:300]}")
        if result['total_paragraphs'] > 30:
            print(f"\n... ({result['total_paragraphs'] - 30} more paragraphs)")
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
