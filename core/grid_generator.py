"""
grid_generator.py
-----------------
Generateur de grille de mots croises pour le jeu Les Mots Codes.

Genere une grille 2D de taille configurable (10x10, 13x13, 15x15...)
comportant :
- Des cases blanches contenant des lettres.
- Des cases noires (separateurs).
- Des intersections valides de mots francais tires du dictionnaire.
- Une couverture maximale de l'alphabet (idealement 26 lettres).
- La gestion des mots composes avec bordures en pointilles.
"""

from dataclasses import dataclass, field
import random
import sqlite3
import time
from typing import Optional

from utils.config import (
    DB_PATH,
    CELL_WHITE,
    CELL_BLACK,
    BORDER_SOLID,
    BORDER_DOTTED,
)


@dataclass
class PlacedWord:
    """Informations sur un mot place dans la grille."""
    word: str
    row: int
    col: int
    direction: str  # "H" pour horizontal, "V" pour vertical
    dot_after: str  # positions des pointilles (ex: "0")


@dataclass
class GeneratedGrid:
    """Resultat complet de la generation d'une grille."""
    width: int
    height: int
    solution: list[list[Optional[str]]]
    cell_types: list[list[str]]
    v_borders: list[list[str]]
    h_borders: list[list[str]]
    placed_words: list[PlacedWord] = field(default_factory=list)
    unique_letters: set[str] = field(default_factory=set)

    def is_white(self, row: int, col: int) -> bool:
        """Retourne True si la case (row, col) est une case blanche jouable."""
        return self.cell_types[row][col] == CELL_WHITE

    def get_letter(self, row: int, col: int) -> Optional[str]:
        """Retourne la lettre majuscule a la position (row, col) ou None."""
        return self.solution[row][col]


class GridGenerator:
    """
    Moteur de generation de grille de mots croises.

    Charge les mots et leurs index en memoire pour un placement
    rapide et efficace base sur le croisement progressif de mots.
    """

    def __init__(self, db_path=DB_PATH) -> None:
        self.words_by_len: dict[int, list[tuple[str, str]]] = {}
        self.index_by_char: dict[tuple[int, int, str], set[int]] = {}
        self.all_words_set: set[str] = set()

        self._load_from_db(db_path)

    def _load_from_db(self, db_path) -> None:
        """Charge le dictionnaire en memoire et construit l'index inverse."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT word, length, dot_after FROM words").fetchall()
        conn.close()

        for word, length, dot_after in rows:
            if length not in self.words_by_len:
                self.words_by_len[length] = []

            idx = len(self.words_by_len[length])
            self.words_by_len[length].append((word, dot_after))
            self.all_words_set.add(word)

            for pos, ch in enumerate(word):
                key = (length, pos, ch)
                if key not in self.index_by_char:
                    self.index_by_char[key] = set()
                self.index_by_char[key].add(idx)

    def generate(
        self,
        width: int = 13,
        height: int = 13,
        min_distinct_letters: int = 24,
        max_attempts: int = 100,
    ) -> Optional[GeneratedGrid]:
        """
        Genere une grille de mots croises valide.

        Parameters
        ----------
        width :
            Nombre de colonnes de la grille.
        height :
            Nombre de lignes de la grille.
        min_distinct_letters :
            Nombre minimal de lettres uniques differentes souhaitees.
        max_attempts :
            Nombre maximal de tentatives de generation.

        Returns
        -------
        GeneratedGrid ou None si aucune grille n'a pu etre generee.
        """
        target_words = 12 if width <= 10 else (20 if width <= 13 else 26)
        min_letters = min(min_distinct_letters, 26)

        best_result = None
        best_letter_count = 0

        for _ in range(max_attempts):
            result = self._try_generate_once(width, height, target_words)
            if result is None:
                continue

            letters_count = len(result.unique_letters)
            if letters_count >= min_letters:
                return result

            if letters_count > best_letter_count:
                best_letter_count = letters_count
                best_result = result

        return best_result

    def _try_generate_once(
        self,
        width: int,
        height: int,
        target_words: int,
    ) -> Optional[GeneratedGrid]:
        """Effectue une tentative de construction de grille."""
        grid: list[list[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]
        placed_words: list[PlacedWord] = []
        used_letters: set[str] = set()

        # Bordures horizontales et verticales
        v_borders = [[BORDER_SOLID for _ in range(width - 1)] for _ in range(height)]
        h_borders = [[BORDER_SOLID for _ in range(width)] for _ in range(height - 1)]

        # 1. Placement du mot central de depart
        start_len = random.randint(min(5, width - 2), min(9, width - 1))
        cands = self.words_by_len.get(start_len, [])
        if not cands:
            return None

        first_word, first_dot = random.choice(cands)
        start_row = height // 2
        start_col = (width - start_len) // 2

        for i, ch in enumerate(first_word):
            grid[start_row][start_col + i] = ch
            used_letters.add(ch)

        placed_words.append(
            PlacedWord(
                word=first_word,
                row=start_row,
                col=start_col,
                direction="H",
                dot_after=first_dot,
            )
        )
        self._apply_dots(v_borders, h_borders, start_row, start_col, "H", first_dot)

        # 2. Cycles de croisements
        max_iterations = 450
        for _ in range(max_iterations):
            if len(placed_words) >= target_words:
                break

            base = random.choice(placed_words)
            cross_idx = random.randint(0, len(base.word) - 1)
            cr = base.row if base.direction == "H" else base.row + cross_idx
            cc = base.col + cross_idx if base.direction == "H" else base.col

            new_dir = "V" if base.direction == "H" else "H"
            max_possible_len = min(9, height if new_dir == "V" else width)
            if max_possible_len < 3:
                continue

            new_len = random.randint(3, max_possible_len)
            new_pos = random.randint(0, new_len - 1)

            nr = cr - new_pos if new_dir == "V" else cr
            nc = cc if new_dir == "V" else cc - new_pos

            # Verification des limites de la grille
            if new_dir == "V" and (nr < 0 or nr + new_len > height):
                continue
            if new_dir == "H" and (nc < 0 or nc + new_len > width):
                continue

            # Verification des extremites (doivent etre libres ou limites)
            if new_dir == "V":
                if nr > 0 and grid[nr - 1][nc] is not None:
                    continue
                if nr + new_len < height and grid[nr + new_len][nc] is not None:
                    continue
            else:
                if nc > 0 and grid[nr][nc - 1] is not None:
                    continue
                if nc + new_len < width and grid[nr][nc + new_len] is not None:
                    continue

            # Verification de l'absence de collisions laterales involontaires
            valid_placement = True
            constraints: dict[int, str] = {}

            for i in range(new_len):
                r = nr + i if new_dir == "V" else nr
                c = nc if new_dir == "V" else nc + i

                if grid[r][c] is not None:
                    constraints[i] = grid[r][c]
                else:
                    if new_dir == "V":
                        left_ch = grid[r][c - 1] if c > 0 else None
                        right_ch = grid[r][c + 1] if c < width - 1 else None
                        if left_ch is not None or right_ch is not None:
                            valid_placement = False
                            break
                    else:
                        top_ch = grid[r - 1][c] if r > 0 else None
                        bot_ch = grid[r + 1][c] if r < height - 1 else None
                        if top_ch is not None or bot_ch is not None:
                            valid_placement = False
                            break

            if not valid_placement:
                continue

            # Recherche des mots candidats satisfaisant les contraintes
            cand_set: Optional[set[int]] = None
            for pos, ch in constraints.items():
                s = self.index_by_char.get((new_len, pos, ch), set())
                cand_set = s if cand_set is None else (cand_set & s)
                if not cand_set:
                    break

            if not cand_set:
                continue

            # Privilegier les mots introduisant de nouvelles lettres
            cand_list = list(cand_set)
            cand_list.sort(
                key=lambda idx: sum(
                    2 if ch not in used_letters else 0
                    for ch in self.words_by_len[new_len][idx][0]
                ),
                reverse=True,
            )

            chosen = None
            existing_word_strings = {pw.word for pw in placed_words}
            for idx in cand_list[:20]:
                word_candidate, dot_candidate = self.words_by_len[new_len][idx]
                if word_candidate not in existing_word_strings:
                    chosen = (word_candidate, dot_candidate)
                    break

            if chosen is None:
                continue

            chosen_word, chosen_dot = chosen
            for i, ch in enumerate(chosen_word):
                r = nr + i if new_dir == "V" else nr
                c = nc if new_dir == "V" else nc + i
                grid[r][c] = ch
                used_letters.add(ch)

            placed_words.append(
                PlacedWord(
                    word=chosen_word,
                    row=nr,
                    col=nc,
                    direction=new_dir,
                    dot_after=chosen_dot,
                )
            )
            self._apply_dots(v_borders, h_borders, nr, nc, new_dir, chosen_dot)

        if len(placed_words) < max(8, target_words // 2):
            return None

        # 3. Preparation de la grille finale (cases blanches vs cases noires)
        solution: list[list[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]
        cell_types: list[list[str]] = [[CELL_BLACK for _ in range(width)] for _ in range(height)]

        for r in range(height):
            for c in range(width):
                if grid[r][c] is not None:
                    solution[r][c] = grid[r][c].upper()
                    cell_types[r][c] = CELL_WHITE

        return GeneratedGrid(
            width=width,
            height=height,
            solution=solution,
            cell_types=cell_types,
            v_borders=v_borders,
            h_borders=h_borders,
            placed_words=placed_words,
            unique_letters={ch.upper() for ch in used_letters},
        )

    def _apply_dots(
        self,
        v_borders: list[list[str]],
        h_borders: list[list[str]],
        row: int,
        col: int,
        direction: str,
        dot_after: str,
    ) -> None:
        """Applique les bordures pointillees pour un mot compose."""
        if not dot_after:
            return

        for part in dot_after.split(","):
            part = part.strip()
            if not part.isdigit():
                continue
            idx = int(part)

            if direction == "H":
                r = row
                c = col + idx
                if 0 <= r < len(v_borders) and 0 <= c < len(v_borders[0]):
                    v_borders[r][c] = BORDER_DOTTED
            else:
                r = row + idx
                c = col
                if 0 <= r < len(h_borders) and 0 <= c < len(h_borders[0]):
                    h_borders[r][c] = BORDER_DOTTED

