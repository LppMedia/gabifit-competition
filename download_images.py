"""
download_images.py
Downloads profile pics and top post images locally so the HTML report works without CDN restrictions.
"""
import json, sys, os, requests, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

DATA = Path("data/raw")
IMG_DIR = Path("data/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)
(IMG_DIR / "profiles").mkdir(exist_ok=True)
(IMG_DIR / "posts").mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
    "Accept": "image/avif,image/webp,image/apng,*/*",
}

def safe_filename(name):
    return re.sub(r'[^\w\-_]', '_', name)

def download(url, dest_path):
    if not url or dest_path.exists():
        return str(dest_path) if dest_path.exists() else None
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return str(dest_path)
    except Exception as e:
        return None

# Load data
with open(DATA / "instagram_profiles.json", encoding='utf-8') as f:
    profiles = json.load(f)
with open(DATA / "instagram_posts.json", encoding='utf-8') as f:
    posts = json.load(f)

tasks = []

# Profile pictures
for p in profiles:
    username = p.get("username", "")
    pic_url = p.get("profilePicUrlHD") or p.get("profilePicUrl", "")
    if pic_url:
        dest = IMG_DIR / "profiles" / f"{safe_filename(username)}.jpg"
        tasks.append(("profile", username, pic_url, dest))

# Top 3 posts per user (sorted by likes)
from collections import defaultdict
posts_by_user = defaultdict(list)
for post in posts:
    posts_by_user[post.get("ownerUsername", "")].append(post)

for username, user_posts in posts_by_user.items():
    top_posts = sorted(user_posts, key=lambda p: p.get("likesCount", 0), reverse=True)[:3]
    for i, post in enumerate(top_posts):
        img_url = post.get("displayUrl", "")
        short_code = post.get("shortCode", f"post{i}")
        if img_url:
            dest = IMG_DIR / "posts" / f"{safe_filename(username)}_{safe_filename(short_code)}.jpg"
            tasks.append(("post", f"{username}/{short_code}", img_url, dest))

print(f"Downloading {len(tasks)} images with 8 threads...")

ok, fail = 0, 0
def do_download(task):
    kind, name, url, dest = task
    result = download(url, dest)
    return (kind, name, result)

with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(do_download, t): t for t in tasks}
    for future in as_completed(futures):
        kind, name, result = future.result()
        if result:
            ok += 1
            print(f"  OK  [{kind}] {name}")
        else:
            fail += 1
            print(f"  FAIL [{kind}] {name}")

print(f"\nDone: {ok} downloaded, {fail} failed")
print("Now run: python generate_report.py")
