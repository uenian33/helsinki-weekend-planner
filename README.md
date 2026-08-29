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
- **Ranks, not favourites.** R3 unmissable, R2 strong enough to reroute around,
  R1 good if you are passing, and the rest of the programme underneath. Ranked
  events carry a written note saying why they sit where they do.
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

Built in Festarri's design language, in a cooler cut than the one it was drawn
for: teal and off-white, with an ember accent for the things that only happen
today.
