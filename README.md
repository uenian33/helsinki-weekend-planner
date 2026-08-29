# Helsinki Weekend Planner — Saturday 29 August 2026

A time-scrubbed map of everything on in Helsinki today, ranked, in English,
Finnish and Chinese.

**Live: https://uenian33.github.io/helsinki-weekend-planner/**

The city publishes hundreds of things on a Saturday across half a dozen
incompatible listings, and a flat A–Z of them is useless at three in the
afternoon when you are deciding whether to leave the house. This turns the day
into three questions you can act on: *what is on right now near me*, *which of
it is worth rearranging the day for*, and *can I get from this one to that one
in time*.

## What it does

- **Timeline scrubber**, 09:00 to 04:00. Drag it and the map and list follow.
  The band behind it is the hourly rain probability, the shaded half is after
  sunset (20:34), the filled area is how many events are running, and the ember
  dots are the things that happen today and not again. Collapses to a pill.
- **Three sections**, at the foot of the screen: *All events*, *Highlights* —
  the same list with the rank floor raised, not a different one — and *My plan*.
- **The list is a clock.** Grouped by the hour a thing starts, because that is
  the question being asked at half past three. The rank travels with each row as
  its badge: R3 unmissable, R2 strong enough to reroute around, R1 good if you
  are passing. Ranked events carry a written note saying why they sit where they
  do. Multi-day runs have no start of their own, so they sit in one group at the
  end rather than burying an hour under 133 of them.
- **Real map**, light and dark, with a satellite layer.
- **My plan.** Add stops, set an arrival time for each, and the planner works out
  the walk between them — distinguishing a fixed performance, which ends when it
  ends, from an open-all-day venue, which is elastic. Four ready-made routes.
- **Where you are.** The locate button puts you on the map and writes the
  distance to every event onto its row — 460 m reads differently from 2.8 km at
  half past three. Permission is asked for on the tap, never on load.
- **Search** across name, venue, street and description, in any language.
- **Flags that matter on the day**: free entry, today only, outdoors with the
  hour's rain probability, sold out, which sitting of a repeated show this is,
  and *Exhibition* for a multi-day run whose hours here are approximate.

## Sharing a link

The link says which language it opens in, so you can hand a Finnish friend the
Finnish one without telling them to change a setting.

| Link | Opens in |
|---|---|
| `…/helsinki-weekend-planner/` | English, light theme |
| `…/helsinki-weekend-planner/en/` · `/fi/` · `/zh/` (or `/ch/`) | that language |
| `…/helsinki-weekend-planner/?lang=fi` | the same thing as a query |

A language in the link beats whatever the reader chose before, so a shared link
opens the way you sent it, and switching language in the app moves the URL with
it — a link saying `/zh/` never shows Finnish. With nothing specified it opens
in English: the browser's own language is deliberately not consulted, because
the default has to be predictable for whoever you hand the plain link to. The
language directories are real copies rather than redirects, since the point of
the feature is the link itself and a redirect rewrites it on the way through.

**Sharing an evening.** *Send this evening to a friend*, at the foot of My plan,
hands the route to the phone's share sheet where there is one and to the
clipboard where there is not: a readable list of stops plus a link carrying the
route, `…/zh/?plan=cur0_930,cur17_1050`. Opening it shows that evening without
touching the reader's own saved plan — the first edit they make is what adopts
it.

## Today, specifically

Twenty degrees, no rain until well after midnight, sunset at 20:34, wind 24–28
km/h. That is unusual enough to change the advice: today the outdoor answer is
the right answer, which in Helsinki it very often is not. Three of the five
unmissables are outdoors, and one of the ready-made routes exists only because
of the forecast.

## Where the data comes from

| Source | What it gives |
|---|---|
| [Linked Events](https://api.hel.fi/linkedevents/v1/) (`api.hel.fi`) | 185 sessions. The city's own open API — what `mitatanaan.fi` is built on. Coordinates, photographs, text in three languages. |
| [Helsinki Festival](https://helsinkifestival.fi/) | 4 sessions, from the festival's own programme API in both Finnish and English. |
| `curated.py` | 67 sessions no open API carries: the clubs, the venue gigs, the Venetsialaiset street parties, and the galleries' Saturday hours. |

256 sessions after merging. A run of several days is folded to one entry and
badged *Exhibition*, because 12:00–20:00 is the shape of a gallery Saturday, not
a promise. Venue coordinates come from the city's own place registry; the three
it does not carry were looked up rather than guessed, because a nightclub pin one
street out sends somebody to the wrong door.

The **ranks and the notes are editorial** — one person's opinion about one
Saturday, not the organisers'. Check the official listing before you set out.

## Rebuilding it

```
python3 fetch.py        # re-pull both APIs into raw/
python3 build_data.py   # merge the three sources into raw/app_events.json
python3 build_public.py # write docs/, which is what GitHub Pages serves
python3 serve.py 8732   # look at it locally
```

`index.html` is self-contained apart from map tiles and fonts. The published copy
under `docs/` quotes only a short excerpt of each official description and links
out for the rest, and carries the programme as a string for `JSON.parse` rather
than as an object literal, which is meaningfully faster on a phone.

## Layout

| | |
|---|---|
| `index.html` | the app, with the full text |
| `curated.py` | the events no API carries, and the notes in three languages |
| `fetch.py` · `build_data.py` · `build_public.py` | pull, merge, publish |
| `docs/` | what GitHub Pages serves |
| `raw/` | API responses and the place cache |

Built in Festarri's design language, repainted in five given colours — blush pop
#FFB8D1, soft blossom #E4B4C2, thistle #E7CEE3, ghost white #E0E1E9, light cyan
#DDFDFE. Blush pop is the most saturated of the five and light cyan is furthest
from it in hue, so those two carry the top two ranks and stay apart at a glance;
thistle takes the third and ghost white the rest. None of the five can carry
text, so each is a ground or a fill paired with an ink deepened from its own hue
until every pair clears 4.5:1 — the badges are 10px bold, which is small text,
and the first pass at those inks did not. Two category fills are derived from
the family, because five colours do not cover seven categories.

Collapsed, the sheet leaves a handle and one line and the map takes 85% of the
screen, which is the proportion Google Maps settled on for the same reason.
