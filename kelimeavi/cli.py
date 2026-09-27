"""kelimeavı CLI."""
import argparse
import json
import sys

from . import __version__
from .game import GameError, new_game, render

USAGE = f"""kelimeavı {__version__} — Türkçe kelime oyunu

usage:
  kelimeavı [--kelime KEİME] [--seed N] [--tahmin S]...
  kelimeavı --json
  kelimeavı -h | --help

options:
  --kelime KEİME  belirli kelimeyle oyna (sözlükte olmalı)
  --seed N        karıştırma tohumu (tekrar oynanabilir)
  --tahmin S      tahmin ekle (birden çok kez verilebilir)
  --goster         cevabı doğrudan göster
  --json           makine-okunur çıktı
  --sozluk         sözlükteki kelimeleri listele

exit codes: 0 ok, 1 oyun hatası, 2 usage error
"""


def main(argv=None):
    parser = argparse.ArgumentParser(prog="kelimeavı", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--version", action="version",
                        version=f"kelimeavı {__version__}")
    parser.add_argument("--kelime")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--tahmin", action="append", default=[])
    parser.add_argument("--goster", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--sozluk", action="store_true")
    args = parser.parse_args(argv)

    if args.help:
        print(USAGE, file=sys.stderr)
        return 2

    if args.sozluk:
        from .game import WORDS
        if args.json:
            print(json.dumps(sorted(set(WORDS)), ensure_ascii=False, indent=2))
        else:
            print("  ".join(sorted(set(WORDS))))
        return 0

    try:
        game = new_game(args.kelime, args.seed)
        for guess in args.tahmin:
            game.guess(guess)
    except GameError as exc:
        print(f"kelimeavı: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({
            "kelime": game.word if (args.goster or game.finished) else None,
            "harfler": game.letters,
            "tahminler": game.guesses,
            "kazandı": game.won,
            "kalan": game.remaining,
        }, ensure_ascii=False, indent=2))
        return 0

    print(render(game))
    return 0 if (game.won or not game.finished or args.goster) else 1


if __name__ == "__main__":
    sys.exit(main())
