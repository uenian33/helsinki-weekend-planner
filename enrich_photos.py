# -*- coding: utf-8 -*-
"""Find a picture for the events that arrived without one.

Three sources, tried in that order because that is the order of how sure we can
be that the picture is of the right thing:

  1. the event's own official page, read for an og:image -- that is the
     organiser's own picture of their own event;
  2. the city's service map, which carries an official photograph for a good
     number of venues;
  3. Wikimedia Commons, where the file title has to contain the venue's name
     before it is accepted, and the licence and photographer are recorded so the
     credit can be shown on the picture.

A venue photograph is not a photograph of the event, so those are marked and the
app captions them as such. A wrong picture is worse than none, which is why
nothing here matches on anything looser than the name.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en,fi;q=0.8'}


def fold(s):
    s = str(s or '').lower()
    for a, b in (('ä', 'a'), ('ö', 'o'), ('å', 'a'), ('é', 'e'), ('è', 'e')):
        s = s.replace(a, b)
    return s


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def og_image(page_url):
    """The picture a page offers to anyone linking to it."""
    try:
        html = get(page_url, 30).decode('utf-8', 'ignore')
    except Exception:
        return None
    for pat in (r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)'):
        m = re.search(pat, html, re.I)
        if m:
            u = m.group(1).strip()
            if u.startswith('//'):
                u = 'https:' + u
            elif u.startswith('/'):
                p = urllib.parse.urlparse(page_url)
                u = f'{p.scheme}://{p.netloc}{u}'
            if u.startswith('http') and not u.endswith('.svg'):
                return u
    return None


def servicemap_photo(venue):
    try:
        url = ('https://api.hel.fi/servicemap/v2/search/?type=unit&page_size=5&q='
               + urllib.parse.quote(venue))
        for r in json.loads(get(url))['results']:
            names = [fold(v) for v in (r.get('name') or {}).values() if v]
            if r.get('picture_url') and any(fold(venue) in n or n in fold(venue) for n in names):
                return r['picture_url'], ''
    except Exception:
        pass
    return None, ''


def commons_photo(venue):
    """Only a file whose own title names the venue, so nothing lands by accident."""
    try:
        url = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
               # the bare name: adding "Helsinki" pushed out venues that are
               # not in Helsinki, and Commons titles rarely carry the city
               '&gsrsearch=' + urllib.parse.quote(venue) +
               '&gsrnamespace=6&gsrlimit=8&prop=imageinfo'
               '&iiprop=url|extmetadata&iiurlwidth=1000&format=json')
        pages = json.loads(get(url)).get('query', {}).get('pages', {})
        for p in pages.values():
            title = fold(p.get('title', ''))
            if fold(venue) not in title:
                continue
            if any(w in title for w in ('locator', ' map', 'kartta', 'logo', 'vaakuna',
                                        'coat of arms', 'diagram', 'sign', 'plaque')):
                continue                      # not a photograph of the place
            ii = (p.get('imageinfo') or [{}])[0]
            if not ii.get('thumburl'):
                continue
            md = ii.get('extmetadata', {})
            artist = re.sub('<[^>]+>', '', md.get('Artist', {}).get('value', '')).strip()
            lic = md.get('LicenseShortName', {}).get('value', '')
            credit = ' · '.join(x for x in (artist[:38], lic) if x)
            return ii['thumburl'].split('?')[0], credit
    except Exception:
        pass
    return None, ''


def venue_site_photo(venue):
    """The venue's own site, found through the city's registry, read for its
    og:image. Last resort, and still the venue rather than the event."""
    try:
        url = ('https://api.hel.fi/servicemap/v2/search/?type=unit&page_size=5&q='
               + urllib.parse.quote(venue))
        for r in json.loads(get(url))['results']:
            names = [fold(v) for v in (r.get('name') or {}).values() if v]
            if not any(fold(venue) in n or n in fold(venue) for n in names):
                continue
            www = r.get('www') or {}
            site = www.get('fi') or www.get('en') or www.get('sv')
            if not site:
                continue
            img = og_image(site)
            if img:
                return img, ''
    except Exception:
        pass
    return None, ''


# Commons files whose title does not contain the venue's name as this data has
# it, checked by hand one at a time rather than matched on a prefix: a rule
# loose enough to catch "Annantalo Arts Centre" from "Annantalo" is also loose
# enough to put the wrong building on a card.
ALIAS = {
    'Annantalo Arts Centre':      'Annantalo',
    'Tullisaaren kartanonpuisto': 'Tullisaari',
    'Seikkailupuisto Huippu':     'Huipun kiipeilyradat',
}

# Organisers whose own site carries a picture the registry does not know about.
SITES = {
    'Kino Tapiola': 'https://espoocine.fi/',
    'Kulttuurikeskus Sofia': 'https://sofia.fi/',
}


def main():
    events = json.load(open(os.path.join(ROOT, 'raw', 'app_events.json')))
    missing = [e for e in events if not e.get('img')]
    print(f'{len(missing)} of {len(events)} sessions have no picture')

    # 1. the organiser's own page
    def from_link(e):
        link = e.get('ue') or e.get('u')
        return (e['i'], og_image(link)) if link else (e['i'], None)

    own = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for eid, url in pool.map(from_link, missing):
            if url:
                own[eid] = url
    print(f'  {len(own)} found an og:image on their own page')

    # 2 and 3. a photograph of the venue, for whatever is still bare
    venues = sorted({e['ve'] for e in missing if e['i'] not in own and e.get('ve')})

    def for_venue(v):
        u, c = servicemap_photo(v)
        if u:
            return v, u, c, 'servicemap'
        u, c = commons_photo(v)
        if u:
            return v, u, c, 'commons'
        if v in ALIAS:
            u, c = commons_photo(ALIAS[v])
            if u:
                return v, u, c, 'commons (alias)'
        u, c = venue_site_photo(v)
        if u:
            return v, u, c, 'venue site'
        if v in SITES:
            u = og_image(SITES[v])
            if u:
                return v, u, '', 'organiser'
        return v, None, '', ''

    found = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for v, u, c, src in pool.map(for_venue, venues):
            if u:
                found[v] = {'url': u, 'credit': c, 'src': src}
                print(f'  {src:<10} {v[:34]:<34} {c[:34]}')
    print(f'  {len(found)} of {len(venues)} venues have a photograph')

    out = os.path.join(ROOT, 'raw', 'found_photos.json')
    try:
        prev = json.load(open(out))
        own = {**prev.get('events', {}), **own}
        found = {**prev.get('venues', {}), **found}
    except Exception:
        pass
    json.dump({'events': own, 'venues': found}, open(out, 'w'), ensure_ascii=False, indent=1)
    still = len(missing) - len(own) - sum(1 for e in missing
                                          if e['i'] not in own and e.get('ve') in found)
    print(f'raw/found_photos.json written; {still} would still be without one')


if __name__ == '__main__':
    sys.exit(main())
