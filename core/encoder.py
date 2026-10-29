"""
encoder.py
----------
Attribue les codes numeriques (de 1 a N) aux lettres presentes dans la grille
et selectionne intelligemment les indices de depart :
- Exclut systematiquement les voyelles (A, E, I, O, U, Y).
- Choisit une combinaison de 3, 4 (ou 5) consonnes couvrant entre 18% et 22%
  des cases blanches a remplir de la grille.
"""

from dataclasses import dataclass
from itertools import combinations
import random
from typing import Optional

from core.grid_generator import GeneratedGrid
from utils.config import (
    HINT_MIN_COVERAGE,
    HINT_MAX_COVERAGE,
    VOWELS,
)


@dataclass
class EncodedPuzzle:
    """Structure contenant toutes les donnees du puzzle encode."""
    grid: GeneratedGrid
    letter_to_code: dict[str, int]
    code_to_letter: dict[int, str]
    encoded_grid: list[list[Optional[int]]]
    initial_hints: dict[int, str]
    num_codes: int


class PuzzleEncoder:
    """
    Encodeur de grille pour le jeu Les Mots Codes.
    """

    @classmethod
    def encode(cls, grid: GeneratedGrid) -> EncodedPuzzle:
        """
        Encode une grille generee et selectionne les indices de depart
        selon les regles d'optimisation (consonnes uniquement, 18-22% de couverture).

        Parameters
        ----------
        grid :
            Grille generee par GridGenerator.

        Returns
        -------
        EncodedPuzzle contenant les correspondances (1 a N) et la grille chiffree.
        """
        available_letters = sorted(grid.unique_letters)
        num_codes = len(available_letters)

        numbers = list(range(1, num_codes + 1))
        random.shuffle(numbers)

        letter_to_code: dict[str, int] = {}
        code_to_letter: dict[int, str] = {}

        for letter, code in zip(available_letters, numbers):
            letter_to_code[letter] = code
            code_to_letter[code] = letter

        encoded_grid: list[list[Optional[int]]] = [
            [None for _ in range(grid.width)] for _ in range(grid.height)
        ]

        for r in range(grid.height):
            for c in range(grid.width):
                if grid.is_white(r, c):
                    letter = grid.get_letter(r, c)
                    if letter is not None and letter in letter_to_code:
                        encoded_grid[r][c] = letter_to_code[letter]

        # Selection des consonnes d'indices
        chosen_consonants = cls._select_hint_consonants(grid)

        initial_hints: dict[int, str] = {
            letter_to_code[l]: l for l in chosen_consonants
        }

        return EncodedPuzzle(
            grid=grid,
            letter_to_code=letter_to_code,
            code_to_letter=code_to_letter,
            encoded_grid=encoded_grid,
            initial_hints=initial_hints,
            num_codes=num_codes,
        )

    @staticmethod
    def _select_hint_consonants(grid: GeneratedGrid) -> list[str]:
        """
        Trouve une combinaison de 3, 4 ou 5 consonnes dont l'utilisation cumulée
        occupe entre 18% et 22% des cases blanches jouables de la grille.
        Les voyelles (A, E, I, O, U, Y) sont rigoureusement exclues.
        """
        # 1. Calcul du nombre total de cases blanches a remplir
        total_white = sum(
            1 for r in range(grid.height) for c in range(grid.width)
            if grid.is_white(r, c)
        )
        if total_white == 0:
            return []

        # 2. Frequence d'apparition de chaque lettre
        frequencies: dict[str, int] = {}
        for r in range(grid.height):
            for c in range(grid.width):
                let = grid.get_letter(r, c)
                if let:
                    frequencies[let] = frequencies.get(let, 0) + 1

        # 3. Filtrer pour ne garder que les consonnes presentes dans la grille
        consonants = [
            l for l in grid.unique_letters
            if l.upper() not in VOWELS and l in frequencies
        ]

        # Si trop peu de consonnes dans la grille (cas extremement rare)
        if len(consonants) <= 3:
            return consonants

        # 4. Recherche de combinaisons de 3, 4 ou 5 consonnes
        # Cible ideale : 20% des cases blanches
        ideal_ratio = 0.20
        valid_combos = []
        all_combos = []

        for k in (3, 4, 5):
            if len(consonants) < k:
                continue
            for combo in combinations(consonants, k):
                occurrences = sum(frequencies[c] for c in combo)
                ratio = occurrences / total_white
                diff = abs(ratio - ideal_ratio)

                all_combos.append((list(combo), occurrences, ratio, diff))

                if HINT_MIN_COVERAGE <= ratio <= HINT_MAX_COVERAGE:
                    valid_combos.append((list(combo), occurrences, ratio, diff))

        if valid_combos:
            # Trier par proximite avec la cible de 20% et choisir parmi les meilleures
            valid_combos.sort(key=lambda item: item[3])
            best_pool = valid_combos[:min(10, len(valid_combos))]
            selected = random.choice(best_pool)
            return selected[0]

        # Fallback de repli : la combinaison la plus proche de 20%
        if all_combos:
            all_combos.sort(key=lambda item: item[3])
            return all_combos[0][0]

        return consonants[:3]
