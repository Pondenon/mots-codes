"""
config.py — Configuration globale du projet Mots Codés.
Toutes les constantes et chemins sont centralisés ici.
Changer de langue = modifier uniquement CURRENT_LANGUAGE.
"""

from pathlib import Path

# ─────────────────────────────────────────────
# Racine du projet (dossier contenant main.py)
# ─────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# Langue active
# ─────────────────────────────────────────────
CURRENT_LANGUAGE = "french"   # changer ici pour switcher de langue

# ─────────────────────────────────────────────
# Chemins des données (dépendent de la langue)
# ─────────────────────────────────────────────
DATA_DIR    = ROOT_DIR / "data" / CURRENT_LANGUAGE
RAW_PATH    = DATA_DIR / f"{CURRENT_LANGUAGE}_words_raw.txt"
DB_PATH     = DATA_DIR / f"{CURRENT_LANGUAGE}_words.db"
PUZZLES_DIR = DATA_DIR / "puzzles"

# ─────────────────────────────────────────────
# Contraintes sur les mots
# ─────────────────────────────────────────────
MIN_WORD_LENGTH = 2   # longueur minimale acceptée dans le dictionnaire
MAX_WORD_LENGTH = 26  # longueur maximale acceptée dans le dictionnaire

# ─────────────────────────────────────────────
# Tailles de grille disponibles (colonnes, lignes)
# ─────────────────────────────────────────────
GRID_SIZES = {
"Petite":  (10, 10),
"Moyenne": (13, 13),
"Grande":  (15, 15),
}
DEFAULT_GRID_SIZE = "Moyenne"

# ─────────────────────────────────────────────
# Paramètres du jeu
# ─────────────────────────────────────────────
NUM_CODES   = 26   # un code par lettre de l'alphabet (1–26)
NUM_HINTS   = 3    # nombre de lettres révélées en indice au départ

# ─────────────────────────────────────────────
# Interface graphique
# ─────────────────────────────────────────────
APP_TITLE        = "Les Mots Codés"
WINDOW_MIN_WIDTH  = 900
WINDOW_MIN_HEIGHT = 650

# Palette de couleurs
COLOR_BG          = "#F5F0E8"   # fond général (beige chaud)
COLOR_CELL_EMPTY  = "#1A1A1A"   # case noire (séparateur)
COLOR_CELL_WHITE  = "#FFFFFF"   # case blanche (lettre)
COLOR_CELL_HINT   = "#D4E8FF"   # case indice (bleu clair)
COLOR_CELL_FILLED = "#E8F5E8"   # case remplie correctement (vert clair)
COLOR_ACCENT      = "#2C5F8A"   # bleu principal (titres, boutons)
COLOR_TEXT_DARK   = "#1A1A1A"   # texte foncé
COLOR_TEXT_LIGHT  = "#FFFFFF"   # texte sur fond foncé

# Polices
FONT_TITLE  = ("Helvetica", 20, "bold")
FONT_CELL   = ("Helvetica", 13, "bold")
FONT_CODE   = ("Helvetica", 11)
FONT_TIMER  = ("Courier",   16, "bold")
FONT_BUTTON = ("Helvetica", 11)

