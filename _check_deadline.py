"""
Backfill script: Fetch halaman detail setiap beasiswa yang kosong deadline/IPK,
lalu extract dan update ke database.

Target:
  - deadline  (YYYY-MM-DD)
  - ipk_minimal (float)
"""
import sys, re, os
sys.path.insert(0, '.')
sys.path.insert(0, os.path.join('.', 'Logika Scraping'))

from models.database import get_connection
from normalizer import parse_tanggal_indonesia, extract_ipk
import requests
from time import sleep

BULAN_ID = {
    'januari': 1, 'january': 1, 'jan': 1,
    'februari': 2, 'february': 2, 'feb': 2,
    'maret': 3, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'mei': 5, 'may': 5,
    'juni': 6, 'june': 6, 'jun': 6,
    'juli': 7, 'july': 7, 'jul': 7,
    'agustus': 8, 'august': 8, 'agu': 8, 'ags': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'oktober': 10, 'october': 10, 'okt': 10, 'oct': 10,
    'november': 11, 'nov': 11, 'nop': 11,
    'desember': 12, 'december': 12, 'des': 12, 'dec': 12,
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0'
}


def extract_deadline_from_html(html, title=""):
    """Extract deadline from page HTML + title."""
    combined = title + " " + html

    # 1) Pattern: Deadline: DD Bulan YYYY
    patterns = [
        r'[Dd]eadline[:\s]+(\d{1,2})\s+(\w+)\s+(\d{4})',
        r'[Bb]atas\s+[Ww]aktu[:\s]+(\d{1,2})\s+(\w+)\s+(\d{4})',
        r'[Pp]endaftaran\s+(?:dibuka|ditutup|berakhir)[:\s]+.*?(\d{1,2})\s+(\w+)\s+(\d{4})',
        r'[Dd]itutup[:\s]+(\d{1,2})\s+(\w+)\s+(\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, combined)
        if match:
            day = int(match.group(1))
            month_str = match.group(2).lower().strip('.')
            year = int(match.group(3))
            if month_str in BULAN_ID and 1 <= day <= 31 and 2024 <= year <= 2030:
                month = BULAN_ID[month_str]
                return f"{year}-{month:02d}-{day:02d}"

    # 2) Try normalizer
    # Find text near "Deadline" keyword
    dl_context = re.search(
        r'(?:deadline|batas\s+waktu|pendaftaran\s+ditutup)[:\s]*(.*?)(?:\.|<|\\n|\n)',
        combined, re.IGNORECASE
    )
    if dl_context:
        dt = parse_tanggal_indonesia(dl_context.group(1))
        if dt:
            y = dt.year
            if 2024 <= y <= 2030:
                return dt.strftime('%Y-%m-%d')

    # 3) Title-only: look for date in parentheses
    paren = re.search(r'\(.*?(\d{1,2})\s+(\w+)\s+(\d{4}).*?\)', title)
    if paren:
        day = int(paren.group(1))
        month_str = paren.group(2).lower().strip('.')
        year = int(paren.group(3))
        if month_str in BULAN_ID and 1 <= day <= 31 and 2024 <= year <= 2030:
            month = BULAN_ID[month_str]
            return f"{year}-{month:02d}-{day:02d}"

    return None


def extract_ipk_from_html(html):
    """Extract IPK from page HTML using normalizer + extra patterns."""
    # Strip HTML tags for cleaner text
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)

    # Use normalizer
    ipk = extract_ipk(text)
    if ipk and 1.0 <= ipk <= 4.0:
        return ipk

    # Extra patterns
    extra = [
        r'(?:IPK|GPA|IP)\s*(?:min(?:imal|imum)?\.?\s*)?(\d+[.,]\d+)',
        r'(\d+[.,]\d+)\s*(?:IPK|GPA)',
    ]
    for pat in extra:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1).replace(',', '.'))
                if 1.0 <= val <= 4.0:
                    return val
            except ValueError:
                pass
    return None


def fetch_page(url):
    """Fetch page and return (title, html_body)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        html = resp.text

        title_m = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_m.group(1).strip() if title_m else ""

        return title, html
    except Exception as e:
        return "", ""


# ===== MAIN =====
conn = get_connection()
cur = conn.cursor()

# Get beasiswa that need backfill (no deadline OR no ipk)
cur.execute("""
    SELECT id, nama, url FROM beasiswa
    WHERE url IS NOT NULL AND url != ''
      AND ((deadline IS NULL OR deadline = '') OR (ipk_minimal IS NULL OR ipk_minimal = 0))
""")
rows = cur.fetchall()
print(f"=== BACKFILL: {len(rows)} beasiswa need data ===\n")

dl_updated = 0
ipk_updated = 0
dl_failed = 0
total = len(rows)

for i, r in enumerate(rows):
    bid, nama, url = r[0], r[1], r[2]
    short = nama[:55] if nama else "?"

    # Check current state
    cur.execute("SELECT deadline, ipk_minimal FROM beasiswa WHERE id = ?", (bid,))
    current = cur.fetchone()
    need_dl = not current[0]
    need_ipk = not current[1]

    if not need_dl and not need_ipk:
        continue

    title, html = fetch_page(url)
    if not html:
        print(f"  [{i+1}/{total}] SKIP (fetch failed): {short}")
        dl_failed += 1
        sleep(0.2)
        continue

    updates = {}

    # Deadline
    if need_dl:
        dl = extract_deadline_from_html(html, title)
        if dl:
            updates["deadline"] = dl

    # IPK
    if need_ipk:
        ipk = extract_ipk_from_html(html)
        if ipk:
            updates["ipk_minimal"] = ipk

    # Apply updates
    if updates:
        set_parts = []
        vals = []
        for k, v in updates.items():
            set_parts.append(f"{k} = ?")
            vals.append(v)
        vals.append(bid)
        cur.execute(f"UPDATE beasiswa SET {', '.join(set_parts)} WHERE id = ?", vals)

        info = ", ".join(f"{k}={v}" for k, v in updates.items())
        print(f"  [{i+1}/{total}] OK: {short} -> {info}")
        if "deadline" in updates:
            dl_updated += 1
        if "ipk_minimal" in updates:
            ipk_updated += 1
    else:
        parts = []
        if need_dl:
            parts.append("deadline")
            dl_failed += 1
        if need_ipk:
            parts.append("ipk")
        print(f"  [{i+1}/{total}] NO DATA ({', '.join(parts)}): {short}")

    sleep(0.3)

    # Commit every 20
    if i % 20 == 0:
        conn.commit()

conn.commit()

# === Final stats ===
cur.execute("SELECT COUNT(*) FROM beasiswa")
total_all = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM beasiswa WHERE deadline IS NOT NULL AND deadline != ''")
w_dl = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM beasiswa WHERE ipk_minimal IS NOT NULL AND ipk_minimal > 0")
w_ipk = cur.fetchone()[0]

print(f"\n{'='*50}")
print(f"HASIL BACKFILL")
print(f"{'='*50}")
print(f"Deadline updated  : {dl_updated}")
print(f"IPK updated       : {ipk_updated}")
print(f"Deadline not found: {dl_failed}")
print(f"")
print(f"Total beasiswa    : {total_all}")
print(f"With deadline     : {w_dl} ({w_dl/total_all*100:.1f}%)")
print(f"With IPK          : {w_ipk} ({w_ipk/total_all*100:.1f}%)")

conn.close()
