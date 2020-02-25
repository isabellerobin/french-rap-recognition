# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import urllib
import requests
from bs4 import BeautifulSoup

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
    lyrics_dict = scrape_songs_lyrics()
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
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    return requests.get(url, headers=headers)


def parse_artists(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    results = []
    for a in soup.find_all('a', class_='uais2d'):
        results.append(a["aria-label"])
    return results


def scrape_songs_lyrics():
    """ Scrape Songs Lyrics
    """
    return {("Artist 1", "Song 1"): "Blabla"}


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
