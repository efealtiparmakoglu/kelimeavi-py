import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from kelimeavi import (Game, GameError, WORDS, find_word, grade_guess,
                       new_game, normalize, render)
from kelimeavi.cli import main


class NormalizationTests(unittest.TestCase):
    def test_case_folding(self):
        self.assertEqual(normalize("  KİTAP "), "kitap")
        self.assertEqual(normalize("Kitap"), "kitap")

    def test_dotted_and_dotless_i_agree(self):
        self.assertEqual(normalize("ILIK"), normalize("ılık"))

    def test_dictionary_lookup_is_case_insensitive(self):
        self.assertEqual(find_word("KİTAP", __import__("random").Random(1))[0],
                         "kitap")


class GradingTests(unittest.TestCase):
    def test_exact_word(self):
        self.assertEqual(grade_guess("kitap", "kitap"), [2, 2, 2, 2, 2])

    def test_partial_letters(self):
        # t is exact, a is present elsewhere, the rest absent
        self.assertEqual(grade_guess("kalem", "kitap"), [2, 1, 0, 0, 0])

    def test_present_but_misplaced(self):
        # the t is in the word, just in the wrong place
        self.assertEqual(grade_guess("zeyti", "kitap"), [0, 0, 0, 1, 1])

    def test_repeated_letters_are_not_double_counted(self):
        # "kitap" holds one k: five k's must not earn five marks
        grades = grade_guess("kkkkk", "kitap")
        self.assertEqual(sum(1 for grade in grades if grade == 2), 1, "only the exact k counts")
        self.assertEqual(sum(1 for grade in grades if grade == 1), 0, "no spare copies exist")

    def test_length_mismatch(self):
        self.assertEqual(grade_guess("kit", "kitap"), [0, 0, 0, 0, 0])

    def test_turkish_i_handling(self):
        grades = grade_guess("ırmak", "balık")
        self.assertEqual(grades[4], 2, "the k is exact")
        self.assertEqual(grades[0], 1, "the dotless ı matches the ı in balık")


class GameTests(unittest.TestCase):
    def test_new_game_from_seed_is_reproducible(self):
        first = new_game(seed=42)
        second = new_game(seed=42)
        self.assertEqual(first.word, second.word)
        self.assertEqual(first.letters, second.letters)

    def test_letters_are_a_scramble_of_the_word(self):
        game = new_game("kitap", seed=1)
        self.assertEqual(sorted(game.letters), sorted("kitap"))

    def test_unknown_word_rejected(self):
        with self.assertRaises(GameError):
            new_game("qwerty")

    def test_guessing_the_word_wins(self):
        game = new_game("kitap", seed=2)
        record = game.guess("kitap")
        self.assertEqual(record["grade"], [2, 2, 2, 2, 2])
        self.assertTrue(game.won)
        self.assertTrue(game.finished)

    def test_guesses_run_out(self):
        game = new_game("kitap", seed=2, max_guesses=2)
        game.guess("kalem")
        game.guess("zeytin")
        self.assertTrue(game.finished)
        self.assertFalse(game.won)
        self.assertEqual(game.remaining, 0)

    def test_repeated_guess_rejected(self):
        game = new_game("kitap", seed=2)
        game.guess("kalem")
        with self.assertRaises(GameError):
            game.guess("KALEM")

    def test_unknown_guess_rejected(self):
        game = new_game("kitap", seed=2)
        with self.assertRaises(GameError):
            game.guess("zzzzz")

    def test_empty_guess_rejected(self):
        game = new_game("kitap", seed=2)
        with self.assertRaises(GameError):
            game.guess("   ")

    def test_guessing_after_the_end_rejected(self):
        game = new_game("kitap", seed=2, max_guesses=1)
        game.guess("kalem")
        self.assertTrue(game.finished)
        with self.assertRaises(GameError):
            game.guess("kitap")

    def test_hint_is_the_answer(self):
        game = new_game("kitap", seed=2)
        self.assertEqual(game.hint(), "kitap")

    def test_render_shows_board_and_state(self):
        game = new_game("kitap", seed=3)
        game.guess("kalem")
        text = render(game)
        # the board shows the scrambled letters, the history the graded guess
        self.assertIn("[ok]", text.lower())
        self.assertIn("(?)", text)
        self.assertIn("kalan tahmin", text)


class DictionaryTests(unittest.TestCase):
    def test_dictionary_is_not_empty(self):
        self.assertGreater(len(WORDS), 50)

    def test_every_game_word_is_in_the_dictionary(self):
        for seed in range(50):
            word = new_game(seed=seed).word
            self.assertIn(word, WORDS)


class CliTests(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_plain_play(self):
        code, out, _ = self.run_main(["--kelime", "kitap", "--seed", "1",
                                     "--tahmin", "kitap"])
        self.assertEqual(code, 0)
        self.assertIn("kazandın", out)

    def test_json_output(self):
        code, out, _ = self.run_main(["--kelime", "kitap", "--seed", "1",
                                     "--tahmin", "kitap", "--json"])
        payload = json.loads(out)
        self.assertTrue(payload["kazandı"])
        self.assertEqual(payload["kelime"], "kitap")

    def test_unknown_word_is_an_error(self):
        code, _, err = self.run_main(["--kelime", "qwerty"])
        self.assertEqual(code, 1)
        self.assertIn("sözlükte yok", err)

    def test_dictionary_listing(self):
        code, out, _ = self.run_main(["--sozluk"])
        self.assertEqual(code, 0)
        self.assertIn("kitap", out)

    def test_help(self):
        code, _, err = self.run_main(["--help"])
        self.assertEqual(code, 2)
        self.assertIn("usage", err)


if __name__ == "__main__":
    unittest.main()
