# kelimeavı

**Türkçe kelime oyunu — karışık harflerden gizli kelimeyi bul, Wordle tarzı puanlama. Sıfır bağımlılık.**

```
$ kelimeavı --kelime kitap --seed 3 --tahmin kalem --tahmin kitap
  K  T  A  P  I

  K[ok] A(?) L    E    M
  K[ok] I[ok] T[ok] A[ok] P[ok]

  kazandın! kelime: KITAP
```

Türkçe kelime oyunları ya internete bağlı ya da kocaman bir sözlük
getiriyor. kelimeavı ikisini de yapmıyor: küçük bir gömülü sözlük,
Türkçe'nin noktalı/noktasız İ sorununu çözen normalleştirme ve
Wordle'in puanlama mantığı.

## Why kelimeavı

- **Türkçe duyarlı normalleştirme.** `İ` Python'da casefold sırasında
  "i + birleşen nokta"ya dönüşür; bu yüzden `KİTAP` ile `kitap` eşleşmezdi.
  Birleşen nokta açıkça temizleniyor, `ı` ve `İ` aynı harfe indirgeniyor —
  testler bu yüzden var.
- **Wordle puanlaması, kaba tahmin değil.** Tam eşleşme 2, başka yerde
  bulunan harf 1, yok 0. Tekrarlı harfler iki kez sayılmaz: `kitap`
  içindeki tek `k` için beş `k` tahmini birden puan kazandırmaz.
- **Sözlük gerçek.** Gözden geçirilmiş 100+ kelimelik Türkçe liste;
  gizli kelime her zaman bu sözlükten gelir, yani her oyun bitirilebilir.
- **Tekrarlanabilir oyun.** `--seed` verildiğinde karıştırma aynı olur,
  bu yüzden bir hamleyi hata ayıklamak ya da test etmek mümkün.
- **Kural ihlalleri açık.** Aynı tahmin iki kez, sözlük dışı kelime ya da
  bittiğinde tahmin — hepsi açık hata, sessizce yutulmaz.
- **Sıfır bağımlılık.** Yalnızca standart kütüphane: `random`, `json`,
  `argparse`.

## Usage

```sh
kelimeavı --kelime kitap --seed 3 --tahmin kalem --tahmin kitap
kelimeavı --seed 7 --goster           # cevabı baştan göster
kelimeavı --sozluk                     # sözlüğü listele
kelimeavı --kelime kitap --json        # makine-okunur çıktı
```

Çıkış kodları: 0 tamam, 1 oyun hatası, 2 kullanım hatası.

## Development

```sh
python3 -m unittest discover -s tests   # 27 test
```

## License

MIT — see [LICENSE](LICENSE).
