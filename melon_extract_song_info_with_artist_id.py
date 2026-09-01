import requests
from bs4 import BeautifulSoup
import re
import threading


class Scrape:
    """Walks an artist's song list on Melon, 50 tracks per request."""

    def __init__(self, artist_id, header):
        self.ajax_url = "https://www.melon.com/artist/songPaging.htm"
        self.artist_id = artist_id
        self.header = header
        self.titles = []
        self.songids = []
        self.albums = []

    def fetch_data(self, start_index=1):
        url = f"{self.ajax_url}?startIndex={start_index}&pageSize=50&listType=A&orderBy=ISSUE_DATE&artistId={self.artist_id}"
        response = requests.get(url, headers=self.header)
        return BeautifulSoup(response.text, 'html.parser')

    def extract_song_info(self):
        start_index = 1
        while True:
            soup = self.fetch_data(start_index=start_index)
            current_song_tags = soup.select('a.fc_gray')
            current_album_tags = soup.find_all('a', class_='fc_mgray')

            for link in current_album_tags:
                # An href containing goAlbumDetail marks an album link.
                if 'goAlbumDetail' in link['href']:
                    self.albums.append(link.text)

            if not current_song_tags and start_index != 1:
                break

            new_titles_extracted = False
            for tag in current_song_tags:
                title = tag.text.strip()
                href_attr = tag.get('href', '')
                # The song ID is the second argument of playSong('<artist>',<songId>)
                match = re.search(r"playSong\('\d+',(\d+)\);", href_attr)
                if match:
                    songid = match.group(1)
                    if title and songid:
                        self.titles.append(title)
                        self.songids.append(songid)
                        new_titles_extracted = True

            # No new titles on this page means the list is exhausted.
            if not new_titles_extracted:
                break
            start_index += 50


def melon_artist_songs(artist_id, header):
    """Return a populated Scrape instance for the given artist."""
    melon = Scrape(artist_id, header)
    melon.extract_song_info()
    return melon


def melon_artist_songs_async(artist_id, header, callback):
    """Run melon_artist_songs off the UI thread and hand the result to callback."""
    def run():
        try:
            melon = melon_artist_songs(artist_id, header)
            callback(True, melon)
        except Exception as e:
            print(f"Error fetching song info: {e}")
            callback(False, None)

    thread = threading.Thread(target=run)
    thread.start()
