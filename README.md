# OneClick

A Kivy Android app that builds a Melon **one-click link** — a single link that drops a whole song queue into the Melon player — out of a set list you assemble in the app.

## Why

One-click links already existed and were in wide use: idol fandoms put together playlists for the artists they supported and distributed them as links. The convenience was for the person *receiving* the link. Producing one was the complicated part, and that work fell entirely on the person creating it.

So this project takes the **link creator** as its user, and tries to cut down the effort and the learning curve of making one of these links.

## How it works

1. **Search an artist by name.** The app resolves the name through Melon's search endpoint (`search/keyword/index.json`) and takes the artist ID from the first result.
2. **Pull the catalogue.** It pages through that artist's songs 50 at a time via `artist/songPaging.htm`, parses the returned markup with BeautifulSoup, and lifts each song's title and ID out of the `playSong('<artistId>',<songId>)` handler, along with album names.
3. **Pick songs, in order.** Tapping a track adds it to the playlist; the playlist screen shows the current selection and can reset it.
4. **Generate the links** from the playlist screen.

### Link generation

The links are `melonapp://` deep links, and the format differs between platforms, so the app emits an Android link, an iOS link and a PC link.

The Android Melon player will not accept the same song twice from one link. So the selection is split at every repeat: each segment becomes its own link, and the segments are listed in play order. Android and PC links are segmented this way; the iOS link is emitted as a single URL covering the whole selection.

On the URL screen each link is a button — pressing it opens Melon with that segment queued. A separate button shortens every link through the TinyURL API and shows them together in one read-only popup with a copy-to-clipboard button, so the finished links can be pasted somewhere and shared.

Artist lookup, song paging and URL shortening all run on worker threads with callbacks, so the UI never blocks. A `사용법` button opens a five-image walkthrough.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | The Kivy app — screens, selectable track list, segmentation, link generation, shortening, clipboard |
| `melon_extract_artist_id.py` | Resolves an artist name to an artist ID |
| `melon_extract_song_info_with_artist_id.py` | Pages through an artist's songs, extracting titles, song IDs and album names |
| `OneClick-1.2.apk` | Release build (arm64-v8a, armeabi-v7a) |

## User study

23 respondents; 87% had used a Melon one-click link before. Each respondent answered one survey about the existing manual method and one about OneClick, with the order counterbalanced — 56.5% took the existing-method survey first, 43.5% started with OneClick. Both surveys were Google Forms, distributed through blog posts that carried a written walkthrough for the manual method and the APK for the app.

Ratings were on a 1–5 scale. Means over the 23 responses:

| | Existing method | OneClick |
| --- | --- | --- |
| Usability — easy to understand how to use it | 2.13 | 4.17 |
| Usability — interface felt intuitive | 2.22 | 4.17 |
| Functionality — had every function that was needed | 3.65 | 4.26 |
| Satisfaction — met expectations | 3.70 | 4.35 |
| Satisfaction — would use it again | 3.30 | 4.26 |
| Satisfaction — would recommend it to someone else | 2.57 | 4.00 |

Yes/no items:

| | Existing method | OneClick |
| --- | --- | --- |
| Hit an error while creating the link | 8.7% yes | 0% yes |
| The generated link worked correctly | 91.3% yes | 100% yes |

The two conclusions drawn were improved usability, and a demand for extensibility.

## Running it

Install `OneClick-1.2.apk` on an Android device, or run it on the desktop:

```bash
pip install kivy requests beautifulsoup4
python main.py
```

The UI is drawn in a bundled Korean font (`nanayang.ttf`) that is not committed here — drop any Korean-capable TTF in beside `main.py` under that name. The walkthrough images (`image1.png`–`image5.png`) are not committed either, so the `사용법` popup will not render without them. Source comments are in Korean.

## Background

Built for a human-computer interaction course at Hanyang University in 2024.
