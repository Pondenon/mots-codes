"""
dictionary.py
-------------
Interface entre la base SQLite et le reste de l'application.
Fournit des methodes propres pour interroger le dictionnaire
sans que les autres modules aient a connaitre SQL.

Usage :
    from core.dictionary import Dictionary
    d = Dictionary()
    word, dot_after = d.get_random_word(length=7)
    word, dot_after = d.get_word_with_letter_at(length=7, letter='P', position=2)
"""

import sqlite3
import random
from pathlib import Path
from typing import Optional

from utils.config import DB_PATH, MIN_WORD_LENGTH, MAX_WORD_LENGTH


# Type alias pour plus de clarte
WordEntry = tuple[str, str]   # (word, dot_after)  ex: ("apriori", "0")


class DictionaryError(Exception):
    """Erreur levee quand le dictionnaire est inaccessible ou vide."""


class Dictionary:
    """
    Gestionnaire du dictionnaire de mots.

    Ouvre une connexion SQLite en lecture seule et expose
    les requetes necessaires au generateur de grille.

    Attributes
    ----------
    db_path : Path
        Chemin vers la base SQLite.
    _conn : sqlite3.Connection
        Connexion ouverte en mode lecture seule.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        if not db_path.exists():
            raise DictionaryError(
                f"Base de donnees introuvable : {db_path}\n"
                "Lancez d'abord : python3 tools/setup_dictionary.py"
            )
        # URI mode = lecture seule, plus sur pendant le jeu
        uri = db_path.as_uri() + "?mode=ro"
        self._conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def get_random_word(
        self,
        length: int,
        exclude: Optional[set[str]] = None,
    ) -> Optional[WordEntry]:
        """
        Retourne un mot aleatoire de la longueur demandee.

        Parameters
        ----------
        length :
            Nombre de lettres voulu (sans compter les espaces des composes).
        exclude :
            Ensemble de mots a exclure (deja places dans la grille).

        Returns
        -------
        (word, dot_after) ou None si aucun mot disponible.
        """
        self._validate_length(length)
        exclude = exclude or set()

        placeholders = ",".join("?" * len(exclude)) if exclude else ""
        not_in_clause = f"AND word NOT IN ({placeholders})" if exclude else ""

        query = f"""
            SELECT word, dot_after
            FROM words
            WHERE length = ?
            {not_in_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """
        params = [length] + list(exclude)
        row = self._conn.execute(query, params).fetchone()
        return (row["word"], row["dot_after"]) if row else None

    def get_word_with_letter_at(
        self,
        length: int,
        letter: str,
        position: int,
        exclude: Optional[set[str]] = None,
    ) -> Optional[WordEntry]:
        """
        Retourne un mot aleatoire de la longueur donnee ayant
        une lettre specifique a une position donnee.

        Parameters
        ----------
        length :
            Nombre de lettres du mot.
        letter :
            Lettre requise (ex: 'P'). Insensible a la casse.
        position :
            Index 0-base de la lettre dans le mot (ex: 2 pour la 3e lettre).
        exclude :
            Mots a exclure.

        Returns
        -------
        (word, dot_after) ou None si aucun mot correspondant.
        """
        self._validate_length(length)
        if not (0 <= position < length):
            raise DictionaryError(
                f"Position {position} invalide pour un mot de longueur {length}."
            )

        exclude = exclude or set()
        letter = letter.lower()

        # substr() en SQLite est 1-indexe
        sql_pos = position + 1

        placeholders = ",".join("?" * len(exclude)) if exclude else ""
        not_in_clause = f"AND word NOT IN ({placeholders})" if exclude else ""

        query = f"""
            SELECT word, dot_after
            FROM words
            WHERE length = ?
              AND substr(word, ?, 1) = ?
            {not_in_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """
        params = [length, sql_pos, letter] + list(exclude)
        row = self._conn.execute(query, params).fetchone()
        return (row["word"], row["dot_after"]) if row else None

    def get_words_with_letters_at(
        self,
        length: int,
        constraints: dict[int, str],
        exclude: Optional[set[str]] = None,
    ) -> Optional[WordEntry]:
        """
        Retourne un mot satisfaisant plusieurs contraintes de lettres a la fois.
        Utile pour le generateur de grille quand plusieurs mots se croisent.

        Parameters
        ----------
        length :
            Nombre de lettres du mot.
        constraints :
            Dictionnaire {position: lettre} (ex: {2: 'P', 5: 'R'}).
        exclude :
            Mots a exclure.

        Returns
        -------
        (word, dot_after) ou None si aucun mot correspondant.
        """
        self._validate_length(length)
        exclude = exclude or set()

        conditions = []
        params: list = [length]

        for pos, letter in constraints.items():
            if not (0 <= pos < length):
                raise DictionaryError(
                    f"Position {pos} invalide pour un mot de longueur {length}."
                )
            conditions.append(f"substr(word, ?, 1) = ?")
            params += [pos + 1, letter.lower()]

        constraint_clause = " AND ".join(conditions)
        if constraint_clause:
            constraint_clause = "AND " + constraint_clause

        placeholders = ",".join("?" * len(exclude)) if exclude else ""
        not_in_clause = f"AND word NOT IN ({placeholders})" if exclude else ""
        params += list(exclude)

        query = f"""
            SELECT word, dot_after
            FROM words
            WHERE length = ?
            {constraint_clause}
            {not_in_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """
        row = self._conn.execute(query, params).fetchone()
        return (row["word"], row["dot_after"]) if row else None

    def word_exists(self, word: str) -> bool:
        """Retourne True si le mot existe dans la base (verification en jeu)."""
        row = self._conn.execute(
            "SELECT 1 FROM words WHERE word = ? LIMIT 1",
            (word.lower(),)
        ).fetchone()
        return row is not None

    def available_lengths(self) -> list[int]:
        """Retourne la liste des longueurs de mots disponibles dans la base."""
        rows = self._conn.execute(
            "SELECT DISTINCT length FROM words ORDER BY length"
        ).fetchall()
        return [r["length"] for r in rows]

    def count(self, length: Optional[int] = None) -> int:
        """
        Retourne le nombre de mots dans la base.
        Si length est fourni, compte uniquement les mots de cette longueur.
        """
        if length is not None:
            row = self._conn.execute(
                "SELECT COUNT(*) as n FROM words WHERE length = ?", (length,)
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) as n FROM words"
            ).fetchone()
        return row["n"]

    def close(self) -> None:
        """Ferme la connexion a la base de donnees."""
        self._conn.close()

    # ------------------------------------------------------------------
    # Context manager (with Dictionary() as d:)
    # ------------------------------------------------------------------

    def __enter__(self) -> "Dictionary":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Helpers prives
    # ------------------------------------------------------------------

    def _validate_length(self, length: int) -> None:
        if not (MIN_WORD_LENGTH <= length <= MAX_WORD_LENGTH):
            raise DictionaryError(
                f"Longueur {length} hors limites "
                f"({MIN_WORD_LENGTH}–{MAX_WORD_LENGTH})."
            )

