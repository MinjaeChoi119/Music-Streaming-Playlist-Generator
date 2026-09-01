import requests
import threading


def get_artist_id(artist_name):
    # Melon's keyword-search endpoint. {} is replaced with the artist name.
    search_url = "https://www.melon.com/search/keyword/index.json?query={}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    search_response = requests.get(search_url.format(artist_name), headers=headers)
    if search_response.status_code == 200:
        search_results = search_response.json()

        # Take the first artist hit. A production version would rank or
        # disambiguate the candidate list instead of assuming the top result.
        artists = search_results.get('ARTISTCONTENTS', [])
        if artists:
            artist_id = artists[0].get('ARTISTID')
            return artist_id
        else:
            print(f"No artist found for '{artist_name}'.")
    else:
        print(f"Search request failed. Status code: {search_response.status_code}")


def get_artist_id_async(artist_name, callback):
    """Run get_artist_id off the UI thread and hand the result to callback."""
    def run():
        try:
            artist_id = get_artist_id(artist_name)
            callback(True, artist_id)
        except Exception as e:
            print(f"Error fetching artist ID: {e}")
            callback(False, None)

    thread = threading.Thread(target=run)
    thread.start()
