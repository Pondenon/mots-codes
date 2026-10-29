"""
config.py
---------
Configuration globale et palettes de themes (Mode Clair et Mode Sombre)
pour le jeu Les Mots Codes.
"""

from pathlib import Path

# ─────────────────────────────────────────────
# Racine du projet
# ─────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# Langue active
# ─────────────────────────────────────────────
CURRENT_LANGUAGE = "french"

# ─────────────────────────────────────────────
# Chemins des donnees
# ─────────────────────────────────────────────
DATA_DIR    = ROOT_DIR / "data" / CURRENT_LANGUAGE
RAW_PATH    = DATA_DIR / f"{CURRENT_LANGUAGE}_words_raw.txt"
DB_PATH     = DATA_DIR / f"{CURRENT_LANGUAGE}_words.db"
PUZZLES_DIR = DATA_DIR / "puzzles"

# ─────────────────────────────────────────────
# Contraintes sur les mots
# ─────────────────────────────────────────────
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 16

# ─────────────────────────────────────────────
# Tailles de grille (colonnes, lignes)
# Format journal : Moyenne = 9 lignes x 17 colonnes
# ─────────────────────────────────────────────
GRID_SIZES = {
    "Petite":  (13, 8),   # 8 lignes x 13 colonnes (104 cases)
    "Moyenne": (17, 9),   # 9 lignes x 17 colonnes (153 cases, <= 10% cases noires)
    "Grande":  (19, 11),  # 11 lignes x 19 colonnes (209 cases)
}
DEFAULT_GRID_SIZE = "Moyenne"

# ─────────────────────────────────────────────
# Regles pour les indices de depart
# ─────────────────────────────────────────────
HINT_MIN_COVERAGE = 0.18  # 18% minimum des cases blanches a remplir
HINT_MAX_COVERAGE = 0.22  # 22% maximum des cases blanches a remplir
VOWELS = set("AEIOUY")   # Voyelles exclues des indices

# ─────────────────────────────────────────────
# Types de cellules et bordures
# ─────────────────────────────────────────────
CELL_BLACK    = "black"   # case noire (separateur)
CELL_WHITE    = "white"   # case blanche (lettre a deviner)

BORDER_SOLID  = "solid"   # bordure normale
BORDER_DOTTED = "dotted"  # bordure pointillee pour mots composes

# ─────────────────────────────────────────────
# Fenetre principale
# ─────────────────────────────────────────────
APP_TITLE         = "Les Mots Codes"
WINDOW_MIN_WIDTH  = 1080
WINDOW_MIN_HEIGHT = 740

# ─────────────────────────────────────────────
# Polices
# ─────────────────────────────────────────────
FONT_TITLE   = ("Helvetica", 22, "bold")
FONT_SUBTITLE = ("Helvetica", 11)
FONT_CELL    = ("Helvetica", 13, "bold")
FONT_CODE    = ("Helvetica", 11)
FONT_TIMER   = ("Courier", 17, "bold")
FONT_BUTTON  = ("Helvetica", 11, "bold")

# ─────────────────────────────────────────────
# Palettes de couleurs : Mode Clair et Mode Sombre
# ─────────────────────────────────────────────
THEME_LIGHT = {
    "name": "light",
    # Fond et conteneurs (Slate / Paper moderne et propre)
    "bg": "#F8FAFC",              # Slate 50 (fond tres propre, non jauni)
    "card_bg": "#FFFFFF",         # Blanc pur pour les cartes
    "card_border": "#E2E8F0",     # Bordure fine Slate 200
    # Textes
    "text_dark": "#0F172A",       # Slate 900 (noir d'encre haute lisibilite)
    "text_muted": "#64748B",      # Slate 500 (texte secondaire)
    "text_light": "#FFFFFF",      # Blanc
    # Accent & navigation
    "accent": "#1D4ED8",          # Bleu royal intense
    "accent_hover": "#1E40AF",
    # Boutons avec fort contraste (texte blanc en gras sur aplats francs)
    "btn_primary_bg": "#1D4ED8",  # Bleu intense
    "btn_primary_fg": "#FFFFFF",  # Blanc pur
    "btn_success_bg": "#15803D",  # Vert emeraude franc
    "btn_success_fg": "#FFFFFF",
    "btn_danger_bg": "#B91C1C",   # Rouge carmin franc
    "btn_danger_fg": "#FFFFFF",
    "btn_secondary_bg": "#475569", # Slate 600
    "btn_secondary_fg": "#FFFFFF",
    "btn_theme_bg": "#334155",
    "btn_theme_fg": "#FFFFFF",
    # Grille de mots croises
    "cell_black": "#0F172A",      # Case noire profonde
    "cell_white": "#FFFFFF",      # Case blanche jouable
    "cell_selected": "#FEF08A",   # Case active (jaune soleil doux)
    "cell_hint": "#DBEAFE",       # Case indice revele (bleu azur clair)
    "cell_filled": "#DCFCE7",     # Grille resolue (vert menthe)
    "border_solid": "#94A3B8",    # Bordures nettes de grille Slate 400
    "border_dotted": "#475569",   # Pointilles distincts Slate 600
}

THEME_DARK = {
    "name": "dark",
    # Fond et conteneurs (Bleu nuit profond)
    "bg": "#0B0F19",              # Bleu nuit profond
    "card_bg": "#151E2E",         # Cartes bleu nuit
    "card_border": "#2A374D",     # Bordures subtiles
    # Textes
    "text_dark": "#F8FAFC",       # Blanc pur
    "text_muted": "#94A3B8",      # Slate 400 clair
    "text_light": "#FFFFFF",      # Blanc
    # Accent & navigation
    "accent": "#38BDF8",          # Cyan lumineux
    "accent_hover": "#0284C7",
    # Boutons avec fort contraste
    "btn_primary_bg": "#2563EB",  # Bleu cobalt lumineux
    "btn_primary_fg": "#FFFFFF",  # Blanc pur
    "btn_success_bg": "#16A34A",  # Vert lumineux
    "btn_success_fg": "#FFFFFF",  # Blanc pur
    "btn_danger_bg": "#DC2626",   # Rouge vif
    "btn_danger_fg": "#FFFFFF",
    "btn_secondary_bg": "#334155", # Slate 700
    "btn_secondary_fg": "#F8FAFC",
    "btn_theme_bg": "#1E293B",
    "btn_theme_fg": "#F8FAFC",
    # Grille de mots croises
    "cell_black": "#020617",      # Noir absolu
    "cell_white": "#1E293B",      # Gris ardoise pour cases jouables
    "cell_selected": "#854D0E",   # Ambre dore pour case active
    "cell_hint": "#1E3A8A",       # Bleu indigo nuit pour indices
    "cell_filled": "#14532D",     # Vert victoire
    "border_solid": "#475569",    # Bordures de grille Slate 600
    "border_dotted": "#94A3B8",   # Pointilles clairs bien visibles
}

# Constantes de repli
COLOR_BG           = THEME_LIGHT["bg"]
COLOR_CELL_BLACK   = THEME_LIGHT["cell_black"]
COLOR_CELL_WHITE   = THEME_LIGHT["cell_white"]
COLOR_CELL_HINT    = THEME_LIGHT["cell_hint"]
COLOR_CELL_FILLED  = THEME_LIGHT["cell_filled"]
COLOR_BORDER_SOLID  = THEME_LIGHT["border_solid"]
COLOR_BORDER_DOTTED = THEME_LIGHT["border_dotted"]
COLOR_ACCENT       = THEME_LIGHT["accent"]
COLOR_TEXT_DARK    = THEME_LIGHT["text_dark"]
COLOR_TEXT_LIGHT   = THEME_LIGHT["text_light"]
