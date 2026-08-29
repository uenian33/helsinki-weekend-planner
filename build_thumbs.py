# -*- coding: utf-8 -*-
"""Make the list thumbnails, because the originals are the wrong size by two
orders of magnitude.

Every row shows its picture at 66x66 css pixels, but the pictures the APIs
hand out are the full press images -- the median is around 1500px on a side
and the largest is 2400px wide. That is roughly 136 times the pixels the row
actually paints, and a phone pays for it on every one it scrolls past: the
decode is what makes the list stutter, not the layout.

So they are fetched once here, cropped square, and written out at 160px as
WebP into docs/thumbs/. The detail sheet still shows the original, one at a
time, where the size is the point.
"""
import hashlib
import io
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'docs', 'thumbs')
SIDE = 160
UA = {'User-Agent': 'weekend-planner/1.0 (+https://uenian33.github.io/helsinki-weekend-planner/)'}


def name_for(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16] + '.webp'


def make(url):
    """Fetch one picture and write its square thumbnail. Returns (url, name)."""
    dest = os.path.join(OUT, name_for(url))
    if os.path.exists(dest):
        return url, os.path.basename(dest)
    try:
        req = urllib.request.Request(url, headers=UA)
        raw = urllib.request.urlopen(req, timeout=45).read()
        im = Image.open(io.BytesIO(raw))
        im.load()
        if im.mode not in ('RGB', 'L'):
            im = im.convert('RGB')
        # cover, not contain: the row is a square and a letterboxed thumbnail
        # reads as a mistake
        w, h = im.size
        side = min(w, h)
        im = im.crop(((w - side) // 2, (h - side) // 2,
                      (w - side) // 2 + side, (h - side) // 2 + side))
        im = im.resize((SIDE, SIDE), Image.LANCZOS)
        im.save(dest, 'WEBP', quality=74, method=5)
        return url, os.path.basename(dest)
    except Exception as exc:
        print(f'  skipped ({str(exc)[:44]}): {url[:64]}')
        return url, None


def main():
    os.makedirs(OUT, exist_ok=True)
    events = json.load(open(os.path.join(ROOT, 'raw', 'app_events.json')))
    urls = sorted({e['img'] for e in events if e.get('img')})
    print(f'{len(urls)} distinct pictures')
    thumbs = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for url, name in pool.map(make, urls):
            if name:
                thumbs[url] = name
    json.dump(thumbs, open(os.path.join(ROOT, 'raw', 'thumbs.json'), 'w'),
              ensure_ascii=False, indent=1)
    total = sum(os.path.getsize(os.path.join(OUT, n)) for n in set(thumbs.values()))
    print(f'{len(thumbs)} thumbnails, {total/1024:.0f} KB in total '
          f'({total/max(1,len(thumbs))/1024:.1f} KB each)')
    if len(thumbs) < len(urls):
        print(f'{len(urls)-len(thumbs)} could not be fetched and keep the original')


if __name__ == '__main__':
    sys.exit(main())
