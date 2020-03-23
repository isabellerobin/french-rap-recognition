import unittest
from src.cleaning.clean_dataset_exploration import *


class CleanDataSetExplorationTest(unittest.TestCase):
    def test_split_in_words(self):
        df = pd.DataFrame({"artist": ["a", "b", "c"], "lyrics": ["hello he test", "deux trois trois", "quatre"]})
        res = split_in_words(df)
        expected = ["hello", "he", "test", "deux", "trois", "trois", "quatre"]
        self.assertEqual(expected, res)

    def test_clean(self):
        self.assertEqual("mot valise", clean("mot-valise"))
        self.assertEqual("se passe", clean("s'passe"))
        self.assertEqual("se exclamer", clean("s'exclamer"))
        self.assertEqual("he ho", clean("he, ho"))
        self.assertEqual("he ho", clean("he ho ?"))


if __name__ == '__main__':
    unittest.main()
