"""
Search bbs.pinggu.org (经管之家) and read full thread content.
Requires: login cookies in ~/.hermes/credentials/bbs-pinggu-cookies.txt

Usage:
  python3 search-bbs-pinggu.py read <thread-url>     # Read thread with cookies
  python3 search-bbs-pinggu.py search <query>        # Show search hint
"""
import os, urllib.request, urllib.parse, re, sys, json, html as html_mod

# Default cookie file path - user must create this file
# See README.md or SKILL.md for how to export cookies from browser
COOKIE_FILE = os.path.expanduser('~/.hermes/credentials/bbs-pinggu-cookies.txt')

def read_cookies():
    cookies = {}
    if not os.path.exists(COOKIE_FILE):
        print(f"Error: Cookie file not found at {COOKIE_FILE}")
        print("Please follow the setup guide in README.md to configure your login cookies.")
        sys.exit(1)
    with open(COOKIE_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                cookies[k] = v
    return cookies

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
    
    # Extract Chinese text blocks, skip CSS/invite/ads
    blocks = re.findall(r'(?:[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]{4,}[^<]*?)(?=<|$)', segment)
    
    meaningful = []
    for b in blocks:
        clean = re.sub(r'\s+', ' ', b).strip()
        clean = html_mod.unescape(clean)
        # Filter out short fragments, CSS-like content, invite spam
        if len(clean) > 20 and '赵安豆' not in clean and '微信' not in clean and 'invite' not in clean:
            meaningful.append(clean)
    
    return meaningful

def read_thread(url):
    """Read a bbs.pinggu.org thread with login cookies."""
    cookies = read_cookies()
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Cookie': cookie_str,
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
    except Exception as e:
        return {'error': str(e)}
    
    html_text = raw.decode('gbk', errors='replace')
    content = extract_post_content(html_text)
    
    # Get title
    title_match = re.search(r'<title>(.*?)</title>', html_text)
    title = html_mod.unescape(title_match.group(1)) if title_match else url
    
    return {
        'title': title,
        'url': url,
        'content': content,
        'total_paragraphs': len(content)
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  search-bbs-pinggu.py read <thread-url>")
        print("  search-bbs-pinggu.py search <query>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'read':
        url = sys.argv[2] if len(sys.argv) > 2 else input("URL: ")
        result = read_thread(url)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\n== {result['title']} ==")
            print(f"URL: {result['url']}")
            print(f"Total paragraphs: {result['total_paragraphs']}")
            print("\n--- Content ---")
            for p in result['content'][:30]:
                print(f"\n{p[:300]}")
            if result['total_paragraphs'] > 30:
                print(f"\n... ({result['total_paragraphs'] - 30} more paragraphs)")
    
    elif action == 'search':
        query = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else input("Query: ")
        print(f"Search for: {query}")
        print("Note: Search is performed through Camofox browser via Baidu.")
        print("1. Start Camofox: ./scripts/camofox-manager.sh start")
        print("2. Open browser: https://www.baidu.com/s?wd=site%3Abbs.pinggu.org+<keyword>")
        print("3. Extract thread URLs from results")
        print("4. Read with: python3 search-bbs-pinggu.py read <thread-url>")
        print("5. Stop Camofox: ./scripts/camofox-manager.sh stop")
    
    else:
        print(f"Unknown action: {action}")
