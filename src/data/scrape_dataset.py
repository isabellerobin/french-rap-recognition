# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
from bs4 import BeautifulSoup
from requests import Response
from typing import List, Dict, Tuple, Optional
import urllib


@click.command()
def main():
    """ Scrape data (artists and songs lyrics) to data/external folder
    """
    logger = logging.getLogger(__name__)
    logger.info('scrape artists names')
    artist_file = open("artists.txt", "w")
    artists_list = scrape_artists()
    for artist in artists_list:
        artist_file.write(artist + "\n")
    artist_file.close()

    logger.info('scrape songs lyrics')
    lyrics_file = open("lyrics.xt", "w")
    lyrics_dict = scrape_artists_songs()
    for song_info, lyrics in lyrics_dict.items():
        lyrics_file.write(song_info[0] + " |" + song_info[1] + "|" + lyrics + "|| \n")


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


def scrape_artists_songs(artists: List[str]) -> Dict[Tuple[str], str]:
    """ Scrape Songs Lyrics
    """
    songs_map = {}
    for artist in artists:
        resp = artist_query(artist)
        artist_url = get_artist_page(resp.content)
        if artist_url:
            discography_resp = get_url_content(artist_url)
            soup = BeautifulSoup(discography_resp.content, "html.parser")
            albums = soup.find_all(lambda tag: tag.name == 'table')
            for album in albums:
                rows = album.find_all(lambda tag: tag.name == 'tr')
                song_suffix_list = [anchor["href"] for row in rows for anchor in row.find_all("a")]
                for song in song_suffix_list:
                    lyrics_url = "https://www.lyrics.com" + song
                    songs_map.put((artist, extract_song_title(song)), scrape_lyrics(lyrics_url))
    return songs_map


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


def get_url_content(url: str) -> Response:
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    return requests.get(url, headers=headers)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
