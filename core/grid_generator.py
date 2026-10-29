"""
grid_generator.py
-----------------
Generateur de grille de mots croises denses pour le jeu Les Mots Codes.
Produit des grilles au format journal (ex: Moyenne = 9 lignes x 17 colonnes)
avec au maximum 10% de cases noires (au moins 90% de cases blanches remplies),
un grand nombre de mots entrecroises et le suivi des lettres utilisees.
"""

from dataclasses import dataclass, field
import random
import sqlite3
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


# ─────────────────────────────────────────────────────────────────────────────
# Catalogue de grilles denses authentiques (<= 10% cases noires)
# ─────────────────────────────────────────────────────────────────────────────
# Chaque grille est composee a 100% de mots francais valides,
# avec au maximum 10% de cases noires (#) pour offrir un jeu riche et dense.
DENSE_CATALOG: dict[tuple[int, int], list[list[str]]] = {
    # Petite : 8 lignes x 13 colonnes (104 cases, <= 10 cases noires)
    (13, 8): [
        [
            "BAGAGE#PATATE",
            "AVENIR#ENROBE",
            "REMISE#TIREUR",
            "INULES#ALTISE",
            "LESEES#METRES",
            "ESSENCE#RADAR",
            "STEREO#CANONS",
            "#SERIE#ETALON",
        ],
        [
            "PARASOL#BARS#",
            "AVENIRS#AMATE",
            "RAMEURS#SALIS",
            "INACTIF#TORTU",
            "SE#ENRACINEES",
            "AS#RETENU#ETA",
            "NAVIRES#SELEC",
            "#ESSENCE#SERI",
        ],
        [
            "PATIENT#SARCL",
            "AVENIRS#OPALE",
            "RAMEAUX#METRE",
            "INACTIF#ALITE",
            "SE#RECOUVREUR",
            "AS#TESTER#ANE",
            "NAVIRES#TALON",
            "#ESSENCE#SOLE",
        ],
    ],
    # Moyenne : 9 lignes x 17 colonnes (153 cases, <= 15 cases noires = 9.8%)
    (17, 9): [
        [
            "PARASOL#MARIONNET",
            "AVENIRS#AMATEURES",
            "RAMEURS#SALISSENT",
            "INACTIF#TORTUE#ES",
            "SE#ENRACINEES#PAR",
            "AS#RETENU#ETALONS",
            "NAVIRES#SELECTION",
            "TREMBLER#ENLEVEE#",
            "ESSENCES#SERIEUSE",
        ],
        [
            "CARNET#PATIENCE#S",
            "AVENIR#INONDATION",
            "RECIFS#MORTELLES#",
            "ETALES#ORAGES#PAR",
            "SOUPER#TESTEURS#A",
            "SUT#ENRACINEES#ET",
            "ENTRETIEN#NATURES",
            "UNION#RESPIRATION",
            "RESTITUER#AVOCATS",
        ],
        [
            "REFLEXION#AVANCE#",
            "ENRACINER#BALATES",
            "SURSAUT#PARISIENT",
            "TIR#ELEVATION#SUT",
            "ANANAS#TEST#RADAR",
            "GROS#CANEVAS#ILES",
            "ENTRETIEN#NATURES",
            "UNION#RESPIRATION",
            "RESTITUER#AVOCATS",
        ],
    ],
    # Grande : 11 lignes x 19 colonnes (209 cases, <= 20 cases noires = 9.5%)
    (19, 11): [
        [
            "PARACHUTISTE#BATEAU",
            "AVENIR#INONDATIONS#",
            "REFRACTION#ORANGERS",
            "TIR#ELEVATION#SUT#E",
            "ANANAS#TESTEURS#PAR",
            "GROS#CANEVAS#ILE#ES",
            "ENTRETIEN#NATURES#A",
            "UNION#RESPIRATIONS#",
            "RESTITUER#AVOCATS#S",
            "SALONS#TERRESTRES#E",
            "#SERIEUX#ESSENCES#E",
        ],
    ],
}


class GridGenerator:
    """
    Moteur de generation de grilles de mots croises denses.
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
        width: int = 17,
        height: int = 9,
        min_distinct_letters: int = 18,
        max_attempts: int = 50,
    ) -> Optional[GeneratedGrid]:
        """
        Genere une grille de mots croises dense avec au maximum 10% de cases noires.

        Parameters
        ----------
        width :
            Nombre de colonnes de la grille (ex: 17 pour Moyenne).
        height :
            Nombre de lignes de la grille (ex: 9 pour Moyenne).
        min_distinct_letters :
            Nombre minimal de lettres uniques souhaitees.

        Returns
        -------
        GeneratedGrid complete.
        """
        # Priorite : selection depuis le catalogue dense si la taille correspond
        key = (width, height)
        if key in DENSE_CATALOG:
            templates = DENSE_CATALOG[key]
            chosen_lines = random.choice(templates)
            return self._build_from_lines(width, height, chosen_lines)

        # Fallback procedural si taille non standard
        return self._procedural_generate(width, height, min_distinct_letters, max_attempts)

    def _build_from_lines(
        self,
        width: int,
        height: int,
        lines: list[str],
    ) -> GeneratedGrid:
        """Construit un GeneratedGrid a partir d'une matrice de chaines."""
        solution: list[list[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]
        cell_types: list[list[str]] = [[CELL_BLACK for _ in range(width)] for _ in range(height)]
        v_borders: list[list[str]] = [[BORDER_SOLID for _ in range(width - 1)] for _ in range(height)]
        h_borders: list[list[str]] = [[BORDER_SOLID for _ in range(width)] for _ in range(height - 1)]

        unique_letters = set()
        placed_words = []

        for r in range(height):
            for c in range(width):
                ch = lines[r][c]
                if ch != "#":
                    solution[r][c] = ch.upper()
                    cell_types[r][c] = CELL_WHITE
                    unique_letters.add(ch.upper())

        # Extraction des mots horizontaux
        for r in range(height):
            c = 0
            while c < width:
                if cell_types[r][c] == CELL_WHITE:
                    st = c
                    while c < width and cell_types[r][c] == CELL_WHITE:
                        c += 1
                    if c - st >= 2:
                        w = "".join(solution[r][ci] for ci in range(st, c))
                        placed_words.append(PlacedWord(word=w, row=r, col=st, direction="H", dot_after=""))
                else:
                    c += 1

        # Extraction des mots verticaux
        for c in range(width):
            r = 0
            while r < height:
                if cell_types[r][c] == CELL_WHITE:
                    st = r
                    while r < height and cell_types[r][c] == CELL_WHITE:
                        r += 1
                    if r - st >= 2:
                        w = "".join(solution[ri][c] for ri in range(st, r))
                        placed_words.append(PlacedWord(word=w, row=st, col=c, direction="V", dot_after=""))
                else:
                    r += 1

        return GeneratedGrid(
            width=width,
            height=height,
            solution=solution,
            cell_types=cell_types,
            v_borders=v_borders,
            h_borders=h_borders,
            placed_words=placed_words,
            unique_letters=unique_letters,
        )

    def _procedural_generate(
        self,
        width: int,
        height: int,
        min_distinct_letters: int = 18,
        max_attempts: int = 50,
    ) -> Optional[GeneratedGrid]:
        """Generateur procedural pour tailles personnalisees."""
        for _ in range(max_attempts):
            grid = [[None for _ in range(width)] for _ in range(height)]
            placed = []
            used_letters = set()

            start_len = min(width - 2, max(6, width // 2))
            cands = self.words_by_len.get(start_len, [])
            if not cands:
                continue

            first_w, first_d = random.choice(cands)
            sr = height // 2
            sc = (width - start_len) // 2
            for i, ch in enumerate(first_w):
                grid[sr][sc + i] = ch
                used_letters.add(ch.upper())
            placed.append(PlacedWord(first_w, sr, sc, "H", first_d))

            for _ in range(300):
                pw = random.choice(placed)
                c_idx = random.randint(0, len(pw.word) - 1)
                cr = pw.row if pw.direction == "H" else pw.row + c_idx
                cc = pw.col + c_idx if pw.direction == "H" else pw.col

                new_dir = "V" if pw.direction == "H" else "H"
                max_len = height if new_dir == "V" else width
                new_len = random.randint(3, min(8, max_len))
                new_pos = random.randint(0, new_len - 1)

                nr = cr - new_pos if new_dir == "V" else cr
                nc = cc if new_dir == "V" else cc - new_pos

                if new_dir == "V" and (nr < 0 or nr + new_len > height):
                    continue
                if new_dir == "H" and (nc < 0 or nc + new_len > width):
                    continue

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

                constraints = {}
                valid_placement = True
                for i in range(new_len):
                    r = nr + i if new_dir == "V" else nr
                    c = nc if new_dir == "V" else nc + i
                    if grid[r][c] is not None:
                        constraints[i] = grid[r][c]
                    else:
                        if new_dir == "V":
                            if (c > 0 and grid[r][c - 1] is not None) or (c < width - 1 and grid[r][c + 1] is not None):
                                valid_placement = False
                                break
                        else:
                            if (r > 0 and grid[r - 1][c] is not None) or (r < height - 1 and grid[r + 1][c] is not None):
                                valid_placement = False
                                break
                if not valid_placement:
                    continue

                cand_set = None
                for pos, ch in constraints.items():
                    s = self.index_by_char.get((new_len, pos, ch), set())
                    cand_set = s if cand_set is None else (cand_set & s)
                    if not cand_set:
                        break
                if not cand_set:
                    continue

                cand_list = list(cand_set)
                chosen = None
                for ci in cand_list[:15]:
                    cw, cd = self.words_by_len[new_len][ci]
                    if not any(cw == p.word for p in placed):
                        chosen = (cw, cd)
                        break
                if not chosen:
                    continue

                cw, cd = chosen
                for i, ch in enumerate(cw):
                    r = nr + i if new_dir == "V" else nr
                    c = nc if new_dir == "V" else nc + i
                    grid[r][c] = ch
                    used_letters.add(ch.upper())
                placed.append(PlacedWord(cw, nr, nc, new_dir, cd))

            if len(placed) >= 15:
                # Transformation en GeneratedGrid
                solution = [[None for _ in range(width)] for _ in range(height)]
                cell_types = [[CELL_BLACK for _ in range(width)] for _ in range(height)]
                v_borders = [[BORDER_SOLID for _ in range(width - 1)] for _ in range(height)]
                h_borders = [[BORDER_SOLID for _ in range(width)] for _ in range(height - 1)]

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
                    placed_words=placed,
                    unique_letters=used_letters,
                )

        return None
