#!/usr/bin/env python3
"""Merge the three sources into the one array the app reads.

Output schema matches the planner's: every entry is one *session*, with a
Finnish and an English title, a venue, coordinates, a start and an end in
minutes from midnight (a time past midnight is the same evening, so 01:30 is
25:30), a rank, and whatever flags the reader needs before setting out.
"""
import datetime as dt, html, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from curated import CURATED, DAY, NOTES_FI, NOTES_ZH, LINKS, PHOTOS

TZ = dt.timezone(dt.timedelta(hours=3))            # Helsinki, August
DAY0 = dt.datetime(2026, 8, 29, 0, 0, tzinfo=TZ)
DAY1 = dt.datetime(2026, 8, 30, 4, 0, tzinfo=TZ)
PLACE_CACHE = os.path.join(ROOT, 'raw', 'places.json')

# Venues the city's registry does not carry. Looked up rather than guessed: a
# nightclub pin that is one street out sends somebody to the wrong door.
MANUAL = {
    'coto':                (60.165424, 24.943127, 'COTÒ', 'Uudenmaankatu 3'),
    'barcelo':             (60.16416, 24.94035, 'Barcelo Tapas & Night Club', 'Uudenmaankatu 16'),
    'munkkiniemen ranta':  (60.19888, 24.86369, 'Munkkiniemenranta', 'Munkkiniemenranta'),
    'hallainvuori':        (60.22790, 25.04920, 'Hallainvuori', 'Hallainvuori'),
    'kruunuvuorenranta':   (60.16472, 25.01679, 'Kruunuvuorenranta', 'Kruunuvuorenranta'),
    'liisanpuistikko':     (60.17382, 24.96053, 'Liisanpuistikko', 'Liisanpuistikko'),
    'lehtisaari':          (60.17850, 24.85253, 'Lehtisaari', 'Lehtisaari'),
    'malja':               (60.16069, 24.92928, 'Malja', 'Hietalahdenranta 6'),
    'ham':                 (60.170155, 24.930195, 'HAM Helsingin taidemuseo', 'Eteläinen Rautatiekatu 8'),
    'sompasauna':          (60.180751, 24.998883, 'Sompasauna', 'Kansanpuistonpolku 5'),
}

# ---------------------------------------------------------------- helpers
def u(s):
    return html.unescape(str(s or '')).replace('–', '-').replace('’', "'").strip()

def txt(h):
    h = re.sub(r'<\s*br\s*/?>', '\n', h or '')
    h = re.sub(r'</p>', '\n\n', h)
    h = re.sub(r'<[^>]+>', ' ', h)
    t = html.unescape(h)
    return re.sub(r'\n\s*\n\s*', '\n\n', re.sub(r'[ \t\xa0]+', ' ', t)).strip()

def parse_iso(s):
    if not s:
        return None
    try:
        d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except Exception:
        return None
    if not 2000 < d.year < 2100:
        return None
    return d.replace(tzinfo=dt.timezone.utc) if d.tzinfo is None else d

def minutes(d):
    """Minutes from midnight, with the small hours counted as the same evening."""
    local = d.astimezone(TZ)
    m = local.hour * 60 + local.minute
    if local.date() > DAY0.date():
        m += 1440
    return m

def label(s, e):
    f = lambda m: f'{(m // 60) % 24:02d}:{m % 60:02d}'
    return f'{f(s)}-{f(e)}' if e and e != s else f(s)

# ---------------------------------------------------------------- places
def load_places():
    try:
        return json.load(open(PLACE_CACHE))
    except Exception:
        return {}

def resolve_place(query, cache):
    """Look a venue up in the city's own place registry, and remember it."""
    key = fold(query)
    if key in MANUAL:
        lat, lon, name, addr = MANUAL[key]
        return {'name': {'fi': name, 'en': name}, 'address': {'fi': addr, 'en': addr},
                'lon': lon, 'lat': lat}
    if key in cache:
        return cache[key]
    url = ('https://api.hel.fi/linkedevents/v1/place/?page_size=3&text='
           + urllib.parse.quote(query))
    hit = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'weekend-planner/1.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=45).read())['data']
            # The registry ranks by a loose full-text match, so a short query can
            # come back led by a street name that merely contains it -- "HAM" hit
            # "Uimastadion / Maauimala" on Hammarskjoldintie, two km off. Take the
            # first place whose own name matches, and only then fall back.
            best = None
            for p in data:
                pos = (p.get('position') or {}).get('coordinates')
                if not pos:
                    continue
                cand = {'name': p.get('name') or {}, 'address': p.get('street_address') or {},
                        'lon': pos[0], 'lat': pos[1]}
                names = [fold(v) for v in cand['name'].values() if v]
                if any(key in n or n in key for n in names):
                    hit = cand
                    break
                if best is None:
                    best = cand
            else:
                hit = best
                if hit:
                    print(f'  place fallback ({query}): no name match, using '
                          f'{hit["name"].get("fi") or hit["name"].get("en")}')
            break
        except Exception as exc:
            print(f'  place lookup retry ({query}): {exc}')
            time.sleep(2)
    cache[key] = hit
    return hit

# ---------------------------------------------------------------- categories
KEYCAT = [
    (('elokuva', 'film', 'cinema', 'movies'), 'Cinema'),
    (('sirkus', 'circus'), 'Theatre'),
    (('tanssi', 'dance'), 'Dance'),
    (('teatteri', 'theatre', 'theater', 'nukketeatteri'), 'Theatre'),
    (('musiikki', 'music', 'konsertit', 'concerts', 'klubit'), 'Music'),
    (('kirjallisuus', 'literature', 'reading', 'runous', 'poetry', 'book clubs',
      'keskustelu', 'conversation', 'luennot', 'lectures'), 'Literature'),
    (('valokuva', 'photograph'), 'Visual arts'),
    (('nayttelyt', 'exhibitions', 'kuvataide', 'fine arts', 'taide', 'art',
      'museot', 'museums', 'muotoilu', 'design'), 'Visual arts'),
    (('tyopajat', 'workshops', 'osallistuminen', 'participation', 'pelit', 'games',
      'leikki', 'playing', 'liikunta', 'physical training', 'ulkoilu',
      'outdoor recreation', 'ruoka', 'food', 'hyvinvointi', 'well-being'), 'Participate'),
]

def fold(s):
    s = str(s or '').lower()
    for a, b in (('ä', 'a'), ('ö', 'o'), ('å', 'a'), ('ò', 'o'), ('é', 'e'), ('à', 'a')):
        s = s.replace(a, b)
    return s

def categorise(words, title=''):
    hay = [fold(w) for w in words] + [fold(title)]
    for keys, cat in KEYCAT:
        for k in keys:
            if any(k in h for h in hay):
                return cat
    return 'Participate'

# ---------------------------------------------------------------- sources
def from_linked_events(cache):
    rows = []
    for e in json.load(open(os.path.join(ROOT, 'raw', 'linkedevents.json'))):
        if e.get('super_event_type') in ('recurring', 'umbrella'):
            continue                                  # a series container, not a session
        st, en = parse_iso(e.get('start_time')), parse_iso(e.get('end_time'))
        if not st:
            continue
        en = en or st + dt.timedelta(hours=2)
        if en < DAY0 or st > DAY1:
            continue
        loc = e.get('location') or {}
        pos = (loc.get('position') or {}).get('coordinates')
        if not pos:
            continue
        name, desc = e.get('name') or {}, e.get('description') or {}
        short = e.get('short_description') or {}
        offers = e.get('offers') or [{}]
        free = any(o.get('is_free') for o in offers)
        kw = [(k.get('name') or {}).get('en') or (k.get('name') or {}).get('fi') or ''
              for k in (e.get('keywords') or [])]
        img = ((e.get('images') or [{}])[0] or {}).get('url') or ''
        # a run of more than a day is an exhibition you can drop into, not a session
        long_run = (en - st).days >= 1
        s_min = 12 * 60 if long_run else minutes(st)
        e_min = 20 * 60 if long_run else max(minutes(en), s_min + 30)
        lname = loc.get('name') or {}
        laddr = loc.get('street_address') or {}
        rows.append(dict(
            src='le', eid=e['id'],
            t=u(name.get('fi') or name.get('en')), te=u(name.get('en') or name.get('fi')),
            v=u(lname.get('fi') or lname.get('en')), ve=u(lname.get('en') or lname.get('fi')),
            a=u(laddr.get('fi') or laddr.get('en')),
            la=round(pos[1], 5), ln=round(pos[0], 5), s=s_min, e=e_min,
            d=txt(desc.get('en') or short.get('en') or desc.get('fi') or short.get('fi'))[:1400],
            df=txt(desc.get('fi') or short.get('fi') or desc.get('en'))[:1400],
            c=categorise(kw, name.get('fi', '')), cs=kw[:6], img=img,
            u=(e.get('info_url') or {}).get('fi') or f'https://tapahtumat.hel.fi/fi/events/{e["id"]}',
            ue=(e.get('info_url') or {}).get('en') or f'https://tapahtumat.hel.fi/en/events/{e["id"]}',
            price='free' if free else '', r=0, long_run=long_run))
    return rows

def from_festival(cache):
    data = json.load(open(os.path.join(ROOT, 'raw', 'festival.json')))
    fi, en = data.get('fi', {}), data.get('en', {})
    # the two language editions are separate posts; match them on image and place
    def key(p):
        im = ((p.get('image') or {}).get('default') or '').split('?')[0]
        l2 = p.get('location2') or {}
        return (im, str(l2.get('lat')), str(l2.get('lng')))
    enkey = {}
    for p in en.values():
        enkey.setdefault(key(p), p)
    rows = []
    for p in fi.values():
        shows = [s for s in (p.get('shows') or []) if s.get('date') == DAY]
        if not shows:
            continue
        l2 = p.get('location2') or {}
        try:
            lat, lon = float(l2['lat']), float(l2['lng'])
        except Exception:
            continue
        epost = enkey.get(key(p)) or {}
        tl = u(p.get('time'))
        dur = 90
        m = re.match(r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})', tl)
        if m:
            a = int(m.group(1)) * 60 + int(m.group(2))
            b = int(m.group(3)) * 60 + int(m.group(4))
            dur = (b - a) % 1440 or 90
        gc = p.get('debug_group_content') or {}
        img = ((p.get('image') or {}).get('sizes') or {}).get('480') or ''
        if img.startswith('/'):
            img = 'https://helsinkifestival.fi' + img
        for k, sh in enumerate(shows):
            tm = re.match(r'^(\d{1,2}):(\d{2})$', str(sh.get('time') or '').strip())
            if not tm:
                continue                       # an umbrella entry with no clock time
            s_min = int(tm.group(1)) * 60 + int(tm.group(2))
            rows.append(dict(
                src='hf', eid=f"hf{p['id']}.{k}",
                t=u(p['name']), te=u(epost.get('name') or p['name']),
                v=u(p.get('location')), ve=u(epost.get('location') or p.get('location')),
                a=u(l2.get('address')), la=round(lat, 5), ln=round(lon, 5),
                s=s_min, e=s_min + dur,
                d=txt(gc.get('en'))[:1400], df=txt(gc.get('fi'))[:1400],
                c=categorise([], p['name']), cs=['Helsinki Festival'], img=img,
                u=p['link'], ue=epost.get('link') or p['link'],
                price='', r=2, long_run=False))
    return rows

def from_curated(cache):
    rows = []
    for i, (t0, t1, name_en, name_fi, venue, price, rank, tags, note) in enumerate(CURATED):
        place = resolve_place(venue, cache)
        if not place:
            print(f'  !! no coordinates for {venue!r} ({name_en})')
            continue
        hh, mm = t0.split(':'); s_min = int(hh) * 60 + int(mm)
        hh, mm = t1.split(':'); e_min = int(hh) * 60 + int(mm)
        if e_min <= s_min:
            e_min += 1440
        pa = place['address']
        rows.append(dict(
            src='cur', eid=f'cur{i}',
            t=name_fi, te=name_en,
            v=venue, ve=venue,
            a=u(pa.get('fi') or pa.get('en')),
            la=round(place['lat'], 5), ln=round(place['lon'], 5), s=s_min, e=e_min,
            d='', df='', note=note, c=categorise(tags, name_en), cs=tags, img='',
            u=LINKS.get(name_en, ''), ue=LINKS.get(name_en, ''),
            price=price, r=rank, long_run=False, tags=tags))
    return rows

# ---------------------------------------------------------------- links
def verify_links(rows):
    """Check every official link and drop the ones that are not there.

    The fallback pattern for events with no info_url of their own does not hold
    for every source - Espoo's events are not on tapahtumat.hel.fi at all - so
    rather than trust the pattern, ask. A 403 is a site refusing a script, not a
    missing page, so those are kept.
    """
    import concurrent.futures as cf
    urls = sorted({u for r in rows for u in (r.get('u'), r.get('ue')) if u})
    status = {}

    def check(url):
        req = urllib.request.Request(url, method='HEAD', headers={
            'User-Agent': 'Mozilla/5.0 (compatible; weekend-planner link check)'})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return url, r.status
        except urllib.error.HTTPError as e:
            if e.code == 405:                      # HEAD refused; try a real GET
                try:
                    req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req2, timeout=25) as r2:
                        return url, r2.status
                except Exception:
                    return url, 0
            return url, e.code
        except Exception:
            return url, 0

    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        for url, code in pool.map(check, urls):
            status[url] = code

    dead = {u for u, c in status.items() if c in (404, 410)}
    for r in rows:
        for k in ('u', 'ue'):
            if r.get(k) in dead:
                r[k] = ''
    print(f'links: {len(urls)} checked, {len(dead)} dead and removed, '
          f'{sum(1 for r in rows if not r["ue"])} events now without one')


# ---------------------------------------------------------------- merge
def main():
    cache = load_places()
    rows = from_curated(cache) + from_festival(cache) + from_linked_events(cache)
    os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)
    json.dump(cache, open(PLACE_CACHE, 'w'), ensure_ascii=False)

    # A curated entry wins over the same thing arriving from an API, but it
    # should not lose the photograph that came with the copy it beat.
    seen, out, by_key = set(), [], {}
    for r in rows:
        keys = {(fold(r['te'])[:26], round(r['la'], 3), round(r['ln'], 3), r['s']),
                (fold(r['te'])[:12], round(r['la'], 3), round(r['ln'], 3), r['s'])}
        clash = keys & seen
        if clash:
            kept = by_key.get(next(iter(clash)))
            if kept is not None and not kept['img'] and r.get('img'):
                kept['img'] = r['img']
            continue
        seen |= keys
        for k in keys:
            by_key[k] = r
        tags = r.get('tags') or []
        r['io'] = 'out' if 'out' in tags else 'both'
        r['x'] = 1 if 'soldout' in tags else 0
        r['bk'] = 0
        r['lim'] = 1 if 'soldout' in tags else 0
        # The two flags the planner surfaces are the two a Saturday actually
        # turns on: does it cost anything, and does it exist only today.
        r['op'] = 1 if ('free' in tags or (r.get('price') or '').lower() == 'free') else 0
        # A run of several days has no session time of its own; 12:00-20:00 is
        # the shape of a Helsinki gallery Saturday, not a promise, so say so.
        r['ex'] = 1 if r.get('long_run') else 0
        r['rr'] = 1 if (not r.get('long_run') and r['src'] in ('cur', 'hf') and r['r'] >= 2) else 0
        r['tl'] = label(r['s'], r['e'])
        r['n'] = r['nn'] = 0
        r['i'] = r['eid']
        note = r.pop('note', '')
        r['qe'] = note
        r['qf'] = NOTES_FI.get(r['te'], '')
        r['qz'] = NOTES_ZH.get(r['te'], '')
        for k2 in ('long_run', 'tags'):
            r.pop(k2, None)
        out.append(r)

    # Anything still without a photograph gets one from the same event as the
    # APIs describe it, matched on title and place. A wrong photograph is worse
    # than none, so the match has to agree on both.
    pool = [r for r in rows if r.get('img')]
    filled = 0
    for r in out:
        if r['img']:
            continue
        a = fold(r['te'])
        for c in pool:
            b = fold(c['te'])
            if len(b) < 8 or len(a) < 8:
                continue
            if not (a[:18] in b or b[:18] in a):
                continue
            if abs(c['la'] - r['la']) > 0.004 or abs(c['ln'] - r['ln']) > 0.008:
                continue
            r['img'] = c['img']
            filled += 1
            break
    # Last resort: a photograph of the place, from the venue's own site. For a
    # Venetsialaiset on the rocks at Loyly the place *is* the picture; for a gig
    # it is not, so these are marked and captioned rather than passed off as the
    # event's own.
    try:
        venue_photos = json.load(open(os.path.join(ROOT, 'raw', 'venue_photos.json')))
    except Exception:
        venue_photos = {}
    vfilled = 0
    for r in out:
        if r['img']:
            continue
        for venue, url in venue_photos.items():
            if fold(venue) in fold(r['ve']) or fold(venue) in fold(r['v']):
                r['img'], r['vp'] = url, 1
                vfilled += 1
                break
    # A photograph named for one specific event wins over the venue fallback,
    # and carries its credit with it.
    for r in out:
        hit = PHOTOS.get(r['te'])
        if hit:
            r['img'], r['cr'], r['vp'] = hit[0], hit[1], 0
    # The row paints its picture at 66px; build_thumbs.py has written a 160px
    # copy of each one, and that is what the list loads.
    try:
        thumbs = json.load(open(os.path.join(ROOT, 'raw', 'thumbs.json')))
    except Exception:
        thumbs = {}
    for r in out:
        r.setdefault('vp', 0)
        r.setdefault('cr', '')
        r['th'] = thumbs.get(r['img'], '') if r.get('img') else ''
    print(f'photographs: {sum(1 for o in out if o["img"])} of {len(out)}'
          f' ({filled} matched to an API entry, {vfilled} venue photographs)')

    verify_links(out)
    out.sort(key=lambda o: (o['s'], -o['r']))
    json.dump(out, open(os.path.join(ROOT, 'raw', 'app_events.json'), 'w'),
              ensure_ascii=False, separators=(',', ':'))
    import collections
    print(f'{len(out)} sessions  ranks={dict(collections.Counter(o["r"] for o in out))}'
          f'  cats={dict(collections.Counter(o["c"] for o in out))}')
    print('sources:', dict(collections.Counter(o['src'] for o in out)))


if __name__ == '__main__':
    main()
