# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.adapters import HTTPAdapter
from typing import List, Dict, Tuple, Optional
import urllib
import time

from urllib3 import Retry

logger = logging.getLogger(__name__)


@click.command()
def main():
    """ Scrape data (artists and songs lyrics) to data/external folder
    """
    logger.info('scrape artists names')
    artist_file = open("data/external/artists.txt", "w")
    artists_list = scrape_artists()
    for artist in artists_list:
        artist_file.write(artist + "\n")
    artist_file.close()

    logger.info('scrape songs lyrics')
    lyrics_file = open("data/external/lyrics.txt", "a")
    scrape_artists_songs(artists_list, lyrics_file)


def scrape_artists():
    """ Scrape Artists Names
    """
    resp = artists_google_query()
    if resp.status_code == 200:
        artists = parse_artists(resp.content)
    else:
        artists = []
    return artists


def artists_google_query():
    query = "hip hop francais artistes"
    query = query.replace(' ', '+')
    url = f"https://google.com/search?q={query}"
    return get_url_content(url)


def parse_artists(html_content: Response) -> List[str]:
    soup = BeautifulSoup(html_content, "html.parser")
    results = []
    for a in soup.find_all('a', class_='uais2d'):
        results.append(a["aria-label"])
    return results


def scrape_artists_songs(artists: List[str], lyrics_file):
    """ Scrape Songs Lyrics
    """
    for artist in artists:
        resp = artist_query(artist)
        artist_url = get_artist_page(resp.content)
        if artist_url:
            logger.debug(f"Parsing artist {artist} songs")
            discography_resp = get_url_content(artist_url)
            soup = BeautifulSoup(discography_resp.content, "html.parser")
            albums = soup.find_all(lambda tag: tag.name == 'table')
            for album in albums:
                time.sleep(1)
                logger.debug(f"Parsing album {album} from artist {artist}")
                rows = album.find_all(lambda tag: tag.name == 'tr')
                song_suffix_list = [anchor["href"] for row in rows for anchor in row.find_all("a")]
                for song_suffix in song_suffix_list:
                    try:
                        time.sleep(2)
                        scrape_song(artist, song_suffix, lyrics_file)
                    except Exception:
                        logger.error(f"Could not parse lyrics from song {extract_song_title(song_suffix)}")


def scrape_song(artist: str, song_suffix: str, lyrics_file):
    """
    Scrape lyrics thanks to its url suffix and write them in the lyrics file

    :param lyrics_file: file where lyrics should be written
    :param artist: artist who authored the song
    :param song_suffix: song lyrics url suffix
    :return: updated songs lyrics dict
    """
    song_title = extract_song_title(song_suffix)
    logger.debug(f"Parsing song {song_title}")
    lyrics_url = "https://www.lyrics.com" + song_suffix
    lyrics = scrape_lyrics(lyrics_url)
    lyrics_file.write(artist + " |" + song_title + "|" + lyrics + "|| \n")


def scrape_lyrics(url: str) -> str:
    resp = get_url_content(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    raw_lyrics = soup.find_all("pre")
    return clean(raw_lyrics)


def extract_song_title(url: str) -> str:
    raw_song_title = url.rsplit("/", 1)[-1]
    cleaned_song_title = urllib.parse.unquote(raw_song_title).replace("+", " ")
    return cleaned_song_title


def clean(raw_lyrics) -> str:
    cleaned_lyrics = raw_lyrics
    for anchor in cleaned_lyrics[0].find_all("a"):
        anchor.replaceWithChildren()
    lyrics = cleaned_lyrics[0].prettify()
    lyrics = lyrics.replace("<pre class=\"lyric-body\" data-lang=\"en\" dir=\"ltr\" id=\"lyric-body-text\">", "")
    lyrics = lyrics.replace("</pre>", "")
    return lyrics


def get_artist_page(resp: Response) -> Optional[str]:
    soup = BeautifulSoup(resp, "html.parser")
    table = soup.find(lambda tag: tag.name == 'table')
    #TODO: Add exception handling to catch error if artist does not exist
    rows = table.find_all(lambda tag: tag.name == 'tr')
    try:
        suffix = rows[0].find_all('a')[0]["href"]
        url = "https://www.lyrics.com/" + suffix
        return url
    except IndexError:
        return None


def artist_query(artist: str) -> Response:
    query = artist.replace(" ", "%20")
    url = f"https://www.lyrics.com/lyrics/{query}"
    return get_url_content(url)


def get_url_content(url: str) -> Optional[Response]:
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
    headers = {"user-agent": USER_AGENT}
    try:
        response = requests_retry_session().get(url, headers=headers)
    except Exception as err:
        logger.error(f"Attempt to connect to {url} failed", exc_info=True)
        return None
    else:
        logger.debug(f"Successful attempt to connect to {url}")
        return response


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
