"""
Script utilitaire (usage unique) :
Lit les CSV du repo French-Dictionary et produit french_words_raw.txt
— un mot valide par ligne, sans doublons, sans accents, sans chiffres.

Mots composés (ex: "a priori") :
  Les espaces sont conservés dans le fichier raw pour les traiter
  ensuite dans setup_dictionary.py (mur en pointillés dans la grille).

Usage :
    python3 tools/build_raw_wordlist.py
"""

import csv
import re
import unicodedata
from pathlib import Path

# ── Chemins ──────────────────────────────────────────────────────────────────
DICT_DIR = Path.home() / "Downloads" / "French-Dictionary-master" / "dictionary"
OUTPUT   = Path(__file__).resolve().parent.parent / "data" / "french" / "french_words_raw.txt"

# Fichiers CSV à fusionner
CSV_FILES = ["noun.csv", "verb.csv", "adj.csv", "adv.csv"]

# Regex : lettres a-z uniquement (accents deja supprimes avant verif)
# Accepte les mots simples ET les mots composes avec UN espace interne
VALID_SIMPLE   = re.compile(r"^[a-z]{2,16}$")
VALID_COMPOUND = re.compile(r"^[a-z]{1,15} [a-z]{1,15}$")

# Pronoms personnels / reflechis a exclure de tous les mots composes.
# On garde les prepositions ("a", "de", "en", "ex", "ad") qui font partie
# d'expressions figees comme "a priori", "en masse", "ex aequo", "ad hoc".
PRONOUN_BLACKLIST = {
    "je", "tu", "on", "nous", "vous", "ils", "elles",
    "me", "te", "se", "lui", "leur", "moi", "toi", "soi",
}

# ── Fonctions ─────────────────────────────────────────────────────────────────

def remove_accents(word: str) -> str:
    """
    Supprime tous les accents/diacritiques des lettres françaises.
    Ex : 'à priori' → 'a priori', 'éléphant' → 'elephant'
    """
    nfd = unicodedata.normalize("NFD", word)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

def normalize(word: str) -> str:
    """Lowercase + suppression des accents."""
    return remove_accents(word.strip().lower())

def is_valid_simple(word: str) -> bool:
    """Retourne True si le mot est un mot simple valide (lettres a-z, 2-16 chars)."""
    return bool(VALID_SIMPLE.match(word)) and 2 <= len(word) <= 16

def is_valid_compound(word: str) -> bool:
    """Retourne True si le mot est un compose valide sans pronom."""
    if not VALID_COMPOUND.match(word):
        return False
    letters_only = word.replace(" ", "")
    return 2 <= len(letters_only) <= 16

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    simple_words   = set()
    compound_words = set()

    for filename in CSV_FILES:
        filepath = DICT_DIR / filename
        if not filepath.exists():
            print(f"  Fichier introuvable : {filepath}")
            continue

        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = normalize(row.get("form", ""))
                if not word:
                    continue

                if " " in word:
                    parts = word.split(" ")
                    pronoun_parts     = [p for p in parts if p in PRONOUN_BLACKLIST]
                    non_pronoun_parts = [p for p in parts if p not in PRONOUN_BLACKLIST]

                    if pronoun_parts:
                        # Compose avec pronom : on recupere uniquement les parties valides
                        # comme mots simples (ex: "vous connaissez" -> "connaissez")
                        for part in non_pronoun_parts:
                            if is_valid_simple(part):
                                simple_words.add(part)
                    else:
                        # Compose sans pronom : expression figee a garder telle quelle
                        if is_valid_compound(word):
                            compound_words.add(word)
                else:
                    if is_valid_simple(word):
                        simple_words.add(word)

        print(f"  {filename} — simples : {len(simple_words):,}  composés : {len(compound_words):,}")

    # Format de sortie :
    #   mots simples   → "maison"
    #   mots composés  → "a priori"  (l'espace est le marqueur de mur pointillé)
    all_words = sorted(simple_words) + sorted(compound_words)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(all_words))

    print(f"\n Fichier généré : {OUTPUT}")
    print(f"   {len(simple_words):,} mots simples")
    print(f"   {len(compound_words):,} mots composés (avec espace → mur pointillé en jeu)")
    print(f"   {len(all_words):,} mots au total")

if __name__ == "__main__":
    main()
