"""
setup_dictionary.py
-------------------
Lit le fichier <langue>_words_raw.txt et construit la base SQLite
<langue>_words.db utilisee par core/dictionary.py pendant le jeu.

Ce script est a executer une seule fois par langue, ou apres une
mise a jour du dictionnaire source.

Usage :
    python3 tools/setup_dictionary.py
    python3 tools/setup_dictionary.py --lang english
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# -- Chemin racine du projet --------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def get_paths(lang: str) -> tuple[Path, Path]:
    """Retourne (raw_path, db_path) pour la langue donnee."""
    data_dir = ROOT_DIR / "data" / lang
    raw_path = data_dir / f"{lang}_words_raw.txt"
    db_path  = data_dir / f"{lang}_words.db"
    return raw_path, db_path


def parse_word(raw_line: str) -> tuple[str, int, str]:
    """
    Analyse une ligne du fichier raw et retourne :
        (word, length, dot_after)

    - word      : lettres uniquement, sans espace  (ex: "apriori")
    - length    : nombre de lettres                (ex: 7)
    - dot_after : positions des bordures pointillees, separees par ","
                  (ex: "0" pour "a priori" -> bordure apres l'index 0)
                  Chaine vide "" pour un mot simple.

    Exemples :
        "maison"   -> ("maison",   6, "")
        "a priori" -> ("apriori",  7, "0")
        "aide moi" -> ("aidemoi",  7, "3")   (bordure apres lettre index 3)
    """
    parts = raw_line.strip().split(" ")

    if len(parts) == 1:
        # Mot simple
        return parts[0], len(parts[0]), ""

    # Mot compose : calculer les positions des bordures pointillees
    # La bordure est situee apres la derniere lettre de chaque partie
    # sauf la derniere.
    dot_positions = []
    cursor = 0
    for part in parts[:-1]:
        cursor += len(part)
        dot_positions.append(str(cursor - 1))   # index 0-base de la derniere lettre de cette partie

    word   = "".join(parts)
    length = len(word)
    dot_after = ",".join(dot_positions)
    return word, length, dot_after


def create_schema(conn: sqlite3.Connection) -> None:
    """Cree la table et les index dans la base SQLite."""
    conn.executescript("""
        DROP TABLE IF EXISTS words;

        CREATE TABLE words (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            word      TEXT    NOT NULL,
            length    INTEGER NOT NULL,
            dot_after TEXT    NOT NULL DEFAULT ''
        );

        CREATE INDEX idx_length ON words(length);
        CREATE INDEX idx_word   ON words(word);
    """)
    conn.commit()


def populate(conn: sqlite3.Connection, raw_path: Path, min_len: int, max_len: int) -> int:
    """
    Lit le fichier raw ligne par ligne et insere les mots valides en base.
    Retourne le nombre de mots inseres.
    """
    batch     = []
    batch_size = 5000
    inserted  = 0

    with open(raw_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            word, length, dot_after = parse_word(line)

            if not (min_len <= length <= max_len):
                continue

            batch.append((word, length, dot_after))

            if len(batch) >= batch_size:
                conn.executemany(
                    "INSERT INTO words (word, length, dot_after) VALUES (?, ?, ?)",
                    batch
                )
                inserted += len(batch)
                batch.clear()

    # Dernier lot
    if batch:
        conn.executemany(
            "INSERT INTO words (word, length, dot_after) VALUES (?, ?, ?)",
            batch
        )
        inserted += len(batch)

    conn.commit()
    return inserted


def print_stats(conn: sqlite3.Connection) -> None:
    """Affiche quelques statistiques sur la base generee."""
    total = conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    compounds = conn.execute(
        "SELECT COUNT(*) FROM words WHERE dot_after != ''"
    ).fetchone()[0]

    print(f"  Total mots inseres  : {total:,}")
    print(f"  Mots composes       : {compounds:,}")
    print(f"  Mots simples        : {total - compounds:,}")
    print()

    # Distribution par longueur
    print("  Distribution par longueur :")
    rows = conn.execute(
        "SELECT length, COUNT(*) FROM words GROUP BY length ORDER BY length"
    ).fetchall()
    for length, count in rows:
        bar = "#" * (count // 2000)
        print(f"    {length:>2} lettres : {count:>7,}  {bar}")


# ----------------------------------------------------------------------------
# Point d'entree
# ----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Construit la base SQLite du dictionnaire pour une langue donnee."
    )
    parser.add_argument(
        "--lang",
        default="french",
        help="Langue a traiter (doit correspondre a un dossier dans data/). "
             "Defaut : french"
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=2,
        help="Longueur minimale des mots a inclure. Defaut : 2"
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=16,
        help="Longueur maximale des mots a inclure. Defaut : 16"
    )
    args = parser.parse_args()

    raw_path, db_path = get_paths(args.lang)

    # Verifications
    if not raw_path.exists():
        print(f"Erreur : fichier source introuvable : {raw_path}")
        print("Veuillez d'abord executer tools/build_raw_wordlist.py")
        sys.exit(1)

    # Suppression de l'ancienne base si elle existe
    if db_path.exists():
        db_path.unlink()
        print(f"Ancienne base supprimee : {db_path.name}")

    print(f"Construction de la base pour la langue : {args.lang}")
    print(f"  Source  : {raw_path}")
    print(f"  Sortie  : {db_path}")
    print(f"  Longueurs acceptees : {args.min_len} a {args.max_len} lettres")
    print()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")   # meilleures perfs en ecriture

    try:
        print("Creation du schema...")
        create_schema(conn)

        print("Insertion des mots...")
        inserted = populate(conn, raw_path, args.min_len, args.max_len)
        print(f"{inserted:,} mots inseres.")
        print()

        print("Statistiques :")
        print_stats(conn)

        print(f"Base generee avec succes : {db_path}")

    except Exception as exc:
        print(f"Erreur lors de la generation : {exc}")
        conn.close()
        db_path.unlink(missing_ok=True)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

