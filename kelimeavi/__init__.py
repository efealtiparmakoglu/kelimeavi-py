"""kelimeavı — Turkish word game with Wordle-style grading."""
__version__ = "1.0.0"

from .game import (BOARD_SIZE, Game, GameError, MAX_GUESSES, WORDS, find_word,
                   grade_guess, new_game, normalize, render)

__all__ = [
    "__version__", "Game", "GameError", "WORDS", "BOARD_SIZE", "MAX_GUESSES",
    "new_game", "find_word", "grade_guess", "normalize", "render",
]
