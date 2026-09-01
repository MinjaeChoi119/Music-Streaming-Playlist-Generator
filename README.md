# OneClick

An Android app that turns a custom song queue into a **single link**. Tap it, and the whole queue plays.

Melon, the streaming service this targets, only lets you queue one track at a time from outside the app. Sharing a set list meant sending a list of song titles and asking the other person to add them one by one.

## How it works

1. You search for an artist. The app resolves the name to Melon's internal artist ID (`melon_extract_artist_id.py`).
2. It pages through that artist's catalogue 50 tracks at a time, pulling each song's title and ID out of the `playSong('<artist>',<songId>)` handler in the markup (`melon_extract_song_info_with_artist_id.py`).
3. You pick the songs you want, in the order you want them.
4. The app assembles the selected IDs into a `melonapp://` deep link that opens Melon and plays the entire queue.

Steps 1 and 2 came out of reverse-engineering how the site's own pages request data — there is no public API for this.

The link format differs by platform, so the app emits an Android link, an iOS link, and a PC link. A queue that repeats the same song is split into several segmented links for Android and PC, since a single link cannot carry the same ID twice; the iOS link is always emitted as one URL covering the full selection.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | The Kivy app — screens, selectable track list, link generation, clipboard handling, threaded requests |
| `melon_extract_artist_id.py` | Resolves an artist name to an artist ID |
| `melon_extract_song_info_with_artist_id.py` | Pages through an artist's songs, extracting titles and song IDs |
| `OneClick-1.2.apk` | Signed release build |

Network calls run on worker threads (`*_async` helpers with callbacks) so the UI never blocks while Melon is being paged.

## Trying it

Install `OneClick-1.2.apk` on an Android device (arm64-v8a or armeabi-v7a), or run it on the desktop:

```bash
pip install kivy requests beautifulsoup4
python main.py
```

The UI bundles a Korean font (`nanayang.ttf`) that is not committed here; drop any Korean-capable TTF in beside `main.py` under that name. Source comments are in Korean.

## Background

Built for a human-computer interaction course at Hanyang University in 2024, and evaluated in a user study as part of that course.
