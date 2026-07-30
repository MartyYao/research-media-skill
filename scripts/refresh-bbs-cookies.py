#!/usr/bin/env python3
"""
Auto-refresh bbs.pinggu.org login cookies.

Checks current cookies validity; if expired, logs in via Camofox browser
and extracts fresh cookies. Designed to run as a cron job.

Usage:
  python3 refresh-bbs-cookies.py          # One-shot: check & refresh if needed
  python3 refresh-bbs-cookies.py --force  # Force refresh regardless of validity

Requires:
  - ~/.hermes/credentials/bbs-pinggu-login.txt (username=Marty_Yao, password=...)
  - Camofox browser (camofox-manager.sh start)
"""
import os, sys, re, subprocess, time, json, http.client
from urllib.parse import urlencode

# ---- Config ----
COOKIE_FILE = os.path.expanduser("~/.hermes/credentials/bbs-pinggu-cookies.txt")
LOGIN_FILE = os.path.expanduser("~/.hermes/credentials/bbs-pinggu-login.txt")
CAMOFOX_PORT = 9377
TEST_URL = "https://bbs.pinggu.org/thread-7909828-1-1.html"
LOGIN_URL = "https://bbs.pinggu.org/member.php?mod=logging&action=login"
VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

def log(msg):
    if VERBOSE:
        print(f"[cookies] {msg}")

# ---- Helpers ----

def read_credentials():
    """Read login credentials from file."""
    if not os.path.exists(LOGIN_FILE):
        print(f"ERROR: Login file not found at {LOGIN_FILE}")
        return None, None
    creds = {}
    with open(LOGIN_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                creds[k.strip()] = v.strip()
    return creds.get("username"), creds.get("password")

def read_old_cookies():
    """Read existing cookie file, return dict."""
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
    """Write cookies to file in Name=Value format."""
    with open(COOKIE_FILE, 'w') as f:
        f.write("# bbs.pinggu.org login cookies (auto-refreshed)\n")
        f.write(f"# 最后更新: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for line in cookies_str.strip().split(';'):
            line = line.strip()
            if line and '=' in line:
                f.write(line + "\n")
    os.chmod(COOKIE_FILE, 0o600)
    print(f"✅ Cookies written to {COOKIE_FILE}")

def test_cookies():
    """Test if current cookies can read a thread. Return True if valid."""
    cookies = read_old_cookies()
    if not cookies:
        return False
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(
            TEST_URL,
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Cookie': cookie_str,
            }
        )
        import urllib.request
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        html = raw.decode('gbk', errors='replace')
        # Check if content is readable (look for Chinese text in post body)
        has_content = bool(re.search(r'[\u4e00-\u9fff]{20,}', html))
        if has_content:
            log("Cookies still valid")
            return True
        else:
            log("Cookies expired: page returned no Chinese content")
            return False
    except Exception as e:
        log(f"Cookie test failed: {e}")
        return False

def run_camofox_command(method, path, body=None):
    """Send HTTP request to Camofox server."""
    conn = http.client.HTTPConnection("localhost", CAMOFOX_PORT, timeout=30)
    headers = {"Content-Type": "application/json"}
    body_json = json.dumps(body) if body else None
    conn.request(method, path, body=body_json, headers=headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    if resp.status >= 400:
        raise Exception(f"Camofox {method} {path}: {resp.status} {data[:200]}")
    return json.loads(data) if data else {}

def login_and_extract_cookies():
    """
    Use Camofox to log into bbs.pinggu.org and extract fresh cookies.
    """
    username, password = read_credentials()
    if not username or not password:
        print("ERROR: Cannot read login credentials")
        return None

    print("🚀 Starting Camofox browser...")
    subprocess.run(
        [os.path.expanduser("~/.hermes/scripts/camofox-manager.sh"), "start"],
        capture_output=True
    )
    time.sleep(3)

    try:
        # Create a new tab and navigate to login page
        print(f"📄 Opening login page...")
        tab = run_camofox_command("POST", "/tabs", {
            "url": LOGIN_URL,
            "userId": "cookies_refresher"
        })
        tab_id = tab.get("tabId")
        if not tab_id:
            raise Exception("No tabId returned")

        # Wait for page to render (SPA)
        time.sleep(4)

        # Get page snapshot to find form fields
        snapshot = run_camofox_command("GET", f"/tabs/{tab_id}/snapshot?userId=cookies_refresher")

        # --- Method 1: Try filling form via evaluate (most reliable for SPA) ---
        print("🔑 Logging in...")
        eval_result = run_camofox_command("POST", f"/tabs/{tab_id}/evaluate", {
            "userId": "cookies_refresher",
            "expression": f"""
(async () => {{
    // Wait for form to load
    await new Promise(r => setTimeout(r, 2000));

    // Try different possible field selectors (Discuz! login forms vary)
    let userInput = document.querySelector('input[name="username"], input[type="text"][placeholder*="账号"], input[type="text"][placeholder*="用户"]');
    let passInput = document.querySelector('input[name="password"], input[type="password"]');
    let loginBtn = document.querySelector('button[type="submit"], .loginBtn, .loginBtn2, input[type="submit"], a[class*="login"]');

    if (!userInput || !passInput) {{
        return {{ error: 'Could not find login form fields', html: document.body.innerHTML.substring(0,1000) }};
    }}

    // Fill credentials
    userInput.value = '{username}';
    userInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
    passInput.value = '{password}';
    passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));

    // Click login
    if (loginBtn) loginBtn.click();
    else if (passInput) {{ passInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter' }})); }}

    // Wait for login to complete (redirect or auth cookie)
    await new Promise(r => setTimeout(r, 5000));

    // Read all cookies
    return {{ cookies: document.cookie, url: window.location.href }};
}})()
"""
        })

        result = eval_result.get("result", {})
        if isinstance(result, dict) and result.get("error"):
            print(f"❌ Login failed: {result['error']}")
            if result.get("html"):
                print(f"Page HTML: {result['html'][:500]}")
            return None

        cookies_str = ""
        if isinstance(result, dict):
            cookies_str = result.get("cookies", "")

        if not cookies_str or "Z9M6_79fc_auth" not in cookies_str:
            print(f"❌ Login may have failed: no auth cookie found")
            print(f"  Result: {json.dumps(result, ensure_ascii=False)[:300]}")
            return None

        print(f"✅ Login successful! Auth cookie found.")
        return cookies_str

    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

    finally:
        # Cleanup: close tab
        try:
            if tab_id:
                run_camofox_command("DELETE", f"/tabs/{tab_id}?userId=cookies_refresher")
        except:
            pass
        subprocess.run(
            [os.path.expanduser("~/.hermes/scripts/camofox-manager.sh"), "stop"],
            capture_output=True
        )
        print("🛑 Camofox stopped")

# ---- Main ----
if __name__ == "__main__":
    force = "--force" in sys.argv

    if not force:
        print("🔍 Checking cookie validity...")
        if test_cookies():
            print("✅ Cookies are still valid. No action needed.")
            sys.exit(0)
        print("⚠️ Cookies expired or missing. Re-authenticating...")

    cookies = login_and_extract_cookies()
    if cookies:
        write_cookies(cookies)
        # Verify new cookies work
        if test_cookies():
            print("✅ New cookies verified successfully!")
            sys.exit(0)
        else:
            print("❌ New cookies failed verification!")
            sys.exit(1)
    else:
        print("❌ Failed to refresh cookies.")
        sys.exit(1)
