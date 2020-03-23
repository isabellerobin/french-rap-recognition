# -*- coding: utf-8 -*-
import logging
import re
from collections import Counter
from pathlib import Path

import pandas as pd
from nltk.corpus import stopwords
import word2vec

import click
from dotenv import find_dotenv, load_dotenv
from typing import List

logger = logging.getLogger(__name__)

full_stop_words = set(stopwords.words('french'))
custom_french_stop_words = ["l", "le", "la", "les", "c", "ce", "ces", "d", "de", "des", "du", "à"]


@click.command()
def main(lyrics_file_path: str, most_common_n: int = None, most_common_filepath: str = "data/external/1gramstop10k.csv"):
    """
    Clean dataset for exploration purpose :
    - Check the most common words of French rap music (which are not common in French books - source https://github.com/gturret/frenchngrams/blob/master/1gramstop10k.csv)
    """
    lyrics_df = pd.read_csv(lyrics_file_path, sep="|", header=None, names=["artist", "song", "lyrics"])
    words = split_in_words(lyrics_df)
    most_common_words = most_common(words, most_common_filepath, most_common_n)
    frequencies_file = open("data/processed/frequencies.txt", "w")
    for item in most_common_words.items():
        frequencies_file.write(item)


def to_pretrained_embeddings(word_list):
    """
    Transform to vectors thanks to already trained embeddings found here http://fauconnier.github.io/ (in order to visualize)
    """
    model = word2vec.load("data/external/frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin")
    return [model[word] for word in word_list]


def most_common_french(file_path: str):
    most_common_1grams = pd.read_csv(file_path, header=None, names=["word", "frequency"])
    return most_common_1grams["word"].tolist()


def most_common(word_list, most_common_filepath, most_common_n=None):
    most_common_words = most_common_french(most_common_filepath)
    word_list_without_common = [word for word in word_list if word not in most_common_words]
    frequencies = Counter(word_list_without_common)
    return frequencies.most_common(most_common_n)


def split_in_words(lyrics_df) -> List[str]:
    words = []
    for i, row in lyrics_df.iterrows():
        cleaned_lyrics = clean(row["lyrics"])
        tokens = [token for token in re.split(" |'|\n", cleaned_lyrics)
                  if token not in full_stop_words and len(token) > 1]
        words.extend(tokens)
    return words


def clean(string: str) -> str:
    if isinstance(string, str):
        return string.lower().replace("\r", "").replace("-", " ").replace(",", "").replace("?", "").replace("!", "").replace("s'", "se ").strip()
    else:
        return string


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
