"""
ShopClawMart Skills Scanner — Production Version
Automated daily scan for new/updated free downloadable skills.
"""

import sys, os, json, re, argparse
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

try:
    from scrapling.fetchers import Fetcher
    FETCHER = True
except ImportError:
    FETCHER = False

SCRIPT_DIR = Path(__file__).parent.resolve()
PREV_FILE  = SCRIPT_DIR / 'prev_listings.json'
CURR_FILE  = SCRIPT_DIR / 'current_listings.json'
LOG_FILE   = SCRIPT_DIR / 'scan_log.md'
BASE_URL   = 'https://www.shopclawmart.com'

# ─── Fetch ───────────────────────────────────────────────────────────────────
def fetch_page(path='/', timeout=20):
    url = BASE_URL + path
    try:
        if FETCHER:
            page = Fetcher.get(url, timeout=timeout)
            return page.html_content
        import subprocess
        r = subprocess.run([
            'curl.exe', '-s', '-L', '-A',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-H', 'Accept: text/html,application/xhtml+xml', url
        ], capture_output=True, timeout=timeout)
        return r.stdout.decode('utf-8', errors='ignore') if r.returncode == 0 else None
    except Exception as e:
        print(f'Fetch error: {e}')
        return None

# ─── Extract ──────────────────────────────────────────────────────────────────
def extract_listings():
    page = Fetcher.get(BASE_URL + '/listings', timeout=20)
    articles = page.css('article')
    
    listings = []
    seen = set()
    
    for art in articles:
        html = art.prettify()
        
        # Slug
        m = re.search(r'<a[^>]+href="/listings/([^"]+)"', html)
        if not m: continue
        slug = m.group(1)
        if slug in seen or len(slug) < 15: continue
        seen.add(slug)
        
        # Title
        tm = re.search(r'<h2[^>]*><a[^>]*>([^<]+)</a></h2>', html)
        title = tm.group(1).strip() if tm else slug
        
        # Category
        cm = re.search(r'<p class="text-sm text-ink-600">([^<]+)</p>', html)
        category = cm.group(1).strip() if cm else '?'
        
        # Price
        pm = re.search(r'<span[^>]*bg-tide[^>]*>\s*(\$[^<]+)\s*</span>', html)
        if pm:
            price = pm.group(1).strip()
            is_free = price in ('$0', '$0.00')
        else:
            price = 'Free'
            is_free = True
        
        if 'free' in title.lower(): is_free = True
        
        # Creator
        cr_m = re.search(r'alt="([^"]+)"[^>]+class="[^"]*rounded-full[^"]*object-cover', html)
        creator = cr_m.group(1).strip() if cr_m else '?'
        
        listings.append({
            'slug': slug, 'title': title, 'price': price,
            'category': category, 'creator': creator,
            'url': BASE_URL + '/listings/' + slug, 'free': is_free,
        })
    
    return listings

# ─── Diff ─────────────────────────────────────────────────────────────────────
def load_prev():
    if PREV_FILE.exists():
        return {l['slug']: l for l in json.loads(PREV_FILE.read_text(encoding='utf-8'))}
    return {}

def diff(current, prev):
    changes = {
        'scanned_at': datetime.now().isoformat(),
        'total': len(current), 'new': [], 'updated': [],
        'free_now': [], 'became_paid': [],
    }
    prev_slugs = set(prev.keys())
    for l in current:
        s = l['slug']
        if s not in prev_slugs:
            changes['new'].append(l)
        elif prev[s].get('price') != l.get('price'):
            changes['updated'].append({'old': prev[s], 'new': l})
        if l['free']:
            changes['free_now'].append(l)
        if s in prev_slugs and prev[s].get('free') and not l['free']:
            changes['became_paid'].append({'was': prev[s], 'now': l})
    return changes

# ─── Report ──────────────────────────────────────────────────────────────────
def make_report(changes):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    n_new = len(changes['new'])
    n_free = len(changes['free_now'])
    n_upd = len(changes['updated'])
    n_paid = len(changes['became_paid'])
    
    md = ''
    md += '# ShopClawMart Skills Scan Report\n\n'
    md += f'**Scanned:** {now}  \n'
    md += f'**Total:** {changes["total"]} | **New:** {n_new} | **Updated:** {n_upd} | **Free:** {n_free}\n\n'
    md += '---\n\n'
    
    if n_new:
        md += '## NEW Listings (' + str(n_new) + ')\n\n'
        for l in changes['new']:
            tag = ' [FREE]' if l['free'] else ''
            md += '- **[' + l['category'] + ']** *' + l['title'] + '* — ' + l['price'] + tag + '\n'
            md += '  ' + l['url'] + '\n'
            md += '  by ' + l['creator'] + '\n\n'
    
    if n_free:
        md += '## Free Skills (' + str(n_free) + ')\n\n'
        for l in changes['free_now']:
            md += '- *' + l['title'] + '* ([' + l['category'] + '])\n'
            md += '  by ' + l['creator'] + ' | ' + l['url'] + '\n\n'
    
    if n_upd:
        md += '## Price Changes (' + str(n_upd) + ')\n\n'
        for u in changes['updated']:
            md += '- *' + u['new']['title'] + '*: `' + u['old'].get('price','?') + '` -> `' + u['new'].get('price','?') + '`\n'
    
    if n_paid:
        md += '## Became Paid (' + str(n_paid) + ')\n\n'
        for u in changes['became_paid']:
            md += '- ~~*' + u['was']['title'] + '*~~ Now: ' + u['now']['price'] + '\n'
    
    if n_new or n_upd:
        md += '\n---\n*Auto-generated - ShopClawMart scanner*\n'
    
    return md

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--diff', action='store_true', help='Show only changes')
    ap.add_argument('--deep', action='store_true', help='Fetch detail pages')
    args = ap.parse_args()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('[' + now + '] ShopClawMart scan starting...')
    
    print('  Fetching /listings page...')
    html = fetch_page('/listings')
    if not html:
        print('  FAILED to fetch /listings!')
        return
    
    print('  HTML: ' + str(len(html)) + ' bytes')
    print('  Extracting listings...')
    listings = extract_listings()
    print('  Found ' + str(len(listings)) + ' listings')
    
    if args.deep:
        free_listings = [l for l in listings if l['free']]
        if free_listings:
            print('  Deep scan: ' + str(len(free_listings)) + ' detail pages...')
            for l in free_listings:
                detail = fetch_page('/listings/' + l['slug'])
                if detail:
                    dm = re.search(r'<p[^>]*class="[^"]*prose[^"]*"[^>]*>(.*?)</p>', detail[:5000], re.DOTALL)
                    if dm:
                        import re as re_mod
                        l['description'] = re_mod.sub(r'<[^>]+>', '', dm.group(1)).strip()[:300]
    
    prev = load_prev()
    changes = diff(listings, prev)
    
    print('')
    print('='*55)
    print('  Total: ' + str(changes['total']) + ' | New: ' + str(len(changes['new'])) + ' | Free: ' + str(len(changes['free_now'])))
    
    if changes['new']:
        print('')
        print('  NEW LISTINGS:')
        for l in changes['new']:
            print('    [' + l['category'] + '] ' + l['title'][:60])
    
    if changes['free_now']:
        print('')
        print('  FREE SKILLS (' + str(len(changes['free_now'])) + '):')
        for l in changes['free_now']:
            print('    - ' + l['title'][:55])
            print('      ' + l['url'])
    
    # Save
    CURR_FILE.write_text(json.dumps(listings, indent=2, ensure_ascii=False), encoding='utf-8')
    PREV_FILE.write_text(json.dumps(listings, indent=2, ensure_ascii=False), encoding='utf-8')
    LOG_FILE.write_text(make_report(changes), encoding='utf-8')
    
    print('')
    print('  Saved to:')
    print('    ' + str(CURR_FILE))
    print('    ' + str(LOG_FILE))
    print('')
    print('  Done!')

if __name__ == '__main__':
    main()
