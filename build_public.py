#!/usr/bin/env python3
"""Build the published copy of the planner from index.html.

Two things happen here.

The local build carries the full programme text so it works offline on a phone.
The published copy keeps only a short excerpt of each official description and
sends the reader to the festival's own page for the rest, so this site is a
finding aid rather than a mirror of somebody else's copy.

And the published copy is written once per language directory, so a link can
name the language it should open in — /en/, /fi/, /zh/ and /ch/ as an alias for
/zh/. These are real copies rather than redirects: the point of the feature is
the link you hand somebody, and a redirect rewrites that link into a query
string on the way through.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
EXCERPT = 300
LANG_DIRS = {'en': 'en', 'fi': 'fi', 'zh': 'zh', 'ch': 'zh'}


def trim(text):
    if not text or len(text) <= EXCERPT:
        return text
    cut = text[:EXCERPT]
    stop = max(cut.rfind('. '), cut.rfind('! '), cut.rfind('? '))
    if stop > 160:
        cut = cut[:stop + 1]
    return cut.rstrip() + ' …'


def main():
    src = open(os.path.join(ROOT, 'index.html')).read()
    m = re.search(r'^const EV=(\[.*\]);$', src, re.M)
    if not m:
        sys.exit('could not find the programme data in index.html')

    events = json.loads(m.group(1))
    for e in events:
        e['d'] = trim(e.get('d'))
        e['df'] = trim(e.get('df'))
    # A large JS object literal goes through the JavaScript parser; the same
    # bytes as a string go through JSON.parse, which is several times faster and
    # is the difference between a slow phone blocking for 350ms and for 130ms.
    blob = json.dumps(events, ensure_ascii=False, separators=(',', ':'))
    blob = (blob.replace('\\', '\\\\').replace("'", "\\'")
                .replace('\u2028', '\\u2028').replace('\u2029', '\\u2029'))
    page = src[:m.start(1)] + "JSON.parse('" + blob + "')" + src[m.end(1):]

    docs = os.path.join(ROOT, 'docs')
    os.makedirs(docs, exist_ok=True)
    written = []
    for path, html in [(os.path.join(docs, 'index.html'), page)] + [
            (os.path.join(docs, d, 'index.html'), page) for d in LANG_DIRS]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').write(html)
        written.append(os.path.relpath(path, ROOT))

    kb = os.path.getsize(os.path.join(docs, 'index.html')) / 1024
    print(f'{len(events)} sessions · {kb:.0f} KB each')
    for w in written:
        print(f'  {w}')


if __name__ == '__main__':
    main()
