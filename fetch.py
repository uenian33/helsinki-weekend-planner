#!/usr/bin/env python3
"""Pull the day's programme from the two open APIs into raw/.

Linked Events (api.hel.fi) is the backbone: it is what the city itself runs on,
it is what mitatanaan.fi is built from, and it carries coordinates, photographs
and text in three languages. Helsinki Festival publishes its own programme
separately. Everything else on a Saturday night — the clubs, the venue gigs,
the Venetsialaiset — is in curated.py, because no open API carries it.
"""
import json, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, 'raw')
DAY = '2026-08-30'


def get(url, tries=3):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'helsinki-weekend-planner/1.0', 'Accept': 'application/json'})
            return json.loads(urllib.request.urlopen(req, timeout=90).read())
        except Exception as exc:
            print(f'  retry {attempt + 1}: {exc}')
            time.sleep(3)
    raise SystemExit(f'gave up on {url}')


def linked_events():
    params = {'start': DAY, 'end': DAY, 'include': 'location,keywords',
              'page_size': '100', 'sort': 'start_time'}
    url = 'https://api.hel.fi/linkedevents/v1/event/?' + urllib.parse.urlencode(params)
    out = []
    while url:
        d = get(url)
        out.extend(d['data'])
        print(f'  linked events {len(out)} / {d["meta"]["count"]}')
        url = d['meta'].get('next')
    return out


def festival():
    out = {}
    for lang in ('fi', 'en'):
        for page in range(1, 10):
            d = get(f'https://helsinkifestival.fi/wp-json/events/v1/search?page={page}&language={lang}')
            for post in d['posts']:
                out.setdefault(lang, {})[str(post['id'])] = post
            if len(out.get(lang, {})) >= d['total']:
                break
        print(f'  festival {lang}: {len(out.get(lang, {}))}')
    return out


def main():
    os.makedirs(RAW, exist_ok=True)
    json.dump(linked_events(), open(os.path.join(RAW, 'linkedevents.json'), 'w'), ensure_ascii=False)
    json.dump(festival(), open(os.path.join(RAW, 'festival.json'), 'w'), ensure_ascii=False)
    print('raw/ written')


if __name__ == '__main__':
    main()
