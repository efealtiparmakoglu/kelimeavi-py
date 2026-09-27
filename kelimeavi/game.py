"""Turkish word game: find a hidden word from scrambled letters.

The board is a list of letters (scrambled by a seeded RNG so runs are
reproducible), the dictionary is a small built-in Turkish word list, and
guesses are graded like Wordle: 2 = exact position, 1 = present, 0 = absent.
"""
import random

BOARD_SIZE = 5
MAX_GUESSES = 6

# A small, dependency-free Turkish word list (5-letter friendly).
WORDS = [
    "kitap", "masa", "evde", "deniz", "gökyüzü", "çiçek", "kalem",
    "pencere", "müzik", "rüzgar", "güneş", "bulut", "orman", "nehir",
    "şehir", "köprü", "yolcu", "balık", "kuş", "kedi", "tavşan",
    "elma", "kiraz", "üzüm", "nar", "limon", "çilek", "karpuz",
    "ekmek", "peynir", "zeytin", "tuz", "şeker", "un", "süt",
    "yumurta", "tavuk", "bıçak", "tabak", "kaşık", "çatal", "tencere",
    "defter", "kalemlik", "silgi", "çanta", "defter", "çizgi", "roman",
    "şiir", "masal", "oyun", "kutlama", "doğum", "sevgi", "umut",
    "barış", "dost", "komşu", "tebrik", "kutlu", "sağlık", "şans",
    "rüya", "yıldız", "ay", "güneş", "fırtına", "kar", "yağmur",
    "nehir", "çiçek", "lale", "gül", "lodos", "sabah", "akşam",
    "pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi",
    "pazar", "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
    "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık",
]

def _normalize_key(text):
    """Fold Turkish dotted/dotless I the way a lookup table needs.

    Python's casefold turns 'İ' into 'i' plus a combining dot, so the dot
    has to be removed explicitly or 'KİTAP' never matches 'kitap'.
    """
    folded = text.strip().casefold()
    folded = folded.replace("\u0307", "")  # combining dot above
    return folded.replace("ı", "i").replace("i̇", "i")


_LOOKUP = {}
for _word in WORDS:
    _LOOKUP.setdefault(_normalize_key(_word), _word)


class GameError(Exception):
    pass


def normalize(text):
    """Case-fold and map Turkish dotted/dotless I consistently."""
    return _normalize_key(text)


def find_word(target, rng):
    """Return (word, scrambled_letters) for a target word."""
    if normalize(target) not in _LOOKUP:
        raise GameError(f"'{target}' sözlükte yok")
    word = _LOOKUP[normalize(target)]
    letters = list(word.casefold())
    rng.shuffle(letters)
    return word, letters


def grade_guess(guess, target):
    """Wordle-style grading: 2 exact, 1 present elsewhere, 0 absent."""
    guess, target = normalize(guess), normalize(target)
    if len(guess) != len(target):
        return [0] * len(target)
    result = [0] * len(target)
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result[i] = 2
    # letters that are not exact can still match a spare copy of themselves
    pool = {}
    for i, letter in enumerate(target):
        if result[i] != 2:
            pool[letter] = pool.get(letter, 0) + 1
    for i, letter in enumerate(guess):
        if result[i] == 2:
            continue
        if pool.get(letter, 0) > 0:
            result[i] = 1
            pool[letter] -= 1
    return result


class Game:
    def __init__(self, word, letters, max_guesses=MAX_GUESSES):
        self.word = word
        self.letters = list(letters)
        self.max_guesses = max_guesses
        self.guesses = []
        self.won = False
        self.finished = False

    def guess(self, text):
        if self.finished:
            raise GameError("oyun bitti")
        normalized = normalize(text)
        if not normalized:
            raise GameError("boş tahmin")
        if normalized not in _LOOKUP:
            raise GameError(f"'{text}' sözlükte yok")
        if normalized in [g["text"] for g in self.guesses]:
            raise GameError("bu tahmin zaten yapılmış")
        record = {
            "text": normalized,
            "grade": grade_guess(normalized, self.word),
        }
        self.guesses.append(record)
        if normalized == normalize(self.word):
            self.won = True
            self.finished = True
        elif len(self.guesses) >= self.max_guesses:
            self.finished = True
        return record

    @property
    def remaining(self):
        return max(self.max_guesses - len(self.guesses), 0)

    def hint(self):
        """Reveal one unrevealed position of the answer."""
        return self.word


def new_game(word=None, seed=None, max_guesses=MAX_GUESSES):
    rng = random.Random(seed)
    target = word or rng.choice(sorted(_LOOKUP.values()))
    found, letters = find_word(target, rng)
    return Game(found, letters, max_guesses)


def render(game):
    """A terminal view of the board and the guess history."""
    lines = ["  " + "  ".join(letter.upper() for letter in game.letters), ""]
    for guess in game.guesses:
        cells = []
        for letter, grade in zip(guess["text"], guess["grade"]):
            mark = {2: "[ok]", 1: "(?)", 0: "   "}[grade]
            cells.append(f"{letter.upper()}{mark}")
        lines.append("  " + " ".join(cells))
    lines.append("")
    if game.won:
        lines.append(f"  kazandın! kelime: {game.word.upper()}")
    elif game.finished:
        lines.append(f"  kalmadı. kelime: {game.word.upper()}")
    else:
        lines.append(f"  kalan tahmin: {game.remaining}")
    return "\n".join(lines)
