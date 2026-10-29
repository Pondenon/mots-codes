# 🔤 Les Mots Codés

> Un jeu de **mots codés** en Python, inspiré des célèbres puzzles de **Jean Paul Cordier**.

Chaque lettre de l'alphabet est remplacée par un chiffre de 1 à 26. À partir de quelques indices, le joueur doit déduire les correspondances et reconstituer tous les mots de la grille.

---

## ✨ Fonctionnalités

- 🎲 **Génération aléatoire** de grilles de mots croisés codés
- 📐 **Taille de grille configurable** (au choix avant chaque partie)
- 🖥️ **Interface graphique** intuitive (Tkinter)
- 🇫🇷 **Dictionnaire français** intégré (~300 000 mots)
- 💾 **Sauvegarde automatique** de chaque partie
- 📜 **Historique** de toutes les parties jouées
- ⏱️ **Chronomètre** avec option pause
- 🌍 **Multi-langues** (architecture prête pour l'anglais, l'espagnol…)

---

## 📁 Structure du projet

```
mots-codes/
│
├── main.py                    # Point d'entrée
│
├── data/
│   └── french/
│       ├── french_words_raw.txt   # Dictionnaire source (non inclus — voir ci-dessous)
│       ├── french_words.db        # Base SQLite générée (non incluse)
│       └── puzzles/               # Parties sauvegardées (générées localement)
│
├── core/
│   ├── dictionary.py          # Chargement et requêtes sur le dictionnaire
│   ├── grid_generator.py      # Algorithme de génération de grille
│   ├── encoder.py             # Attribution des codes chiffres ↔ lettres
│   └── game_model.py          # État et logique d'une partie
│
├── ui/
│   ├── app.py                 # Fenêtre principale
│   ├── menu_screen.py         # Écran d'accueil et historique
│   ├── grid_view.py           # Affichage interactif de la grille
│   ├── code_panel.py          # Panneau de saisie des codes (1–26)
│   └── timer_widget.py        # Chronomètre et bouton pause
│
├── storage/
│   └── puzzle_store.py        # Sauvegarde / chargement JSON des parties
│
├── utils/
│   └── config.py              # Configuration globale (langue, chemins…)
│
└── tools/
    └── setup_dictionary.py    # Script d'initialisation du dictionnaire
```

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/<ton-username>/mots-codes.git
cd mots-codes
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Télécharger le dictionnaire français

Télécharge le fichier de mots depuis [Lexique](http://www.lexique.org/) ou [dicollecte](https://www.dicollecte.org/) et place-le ici :

```
data/french/french_words_raw.txt
```

### 5. Initialiser la base de données

```bash
python tools/setup_dictionary.py --lang french
```

### 6. Lancer le jeu

```bash
python main.py
```

---

## 🧩 Comment jouer

1. **Choisissez la taille** de la grille sur l'écran d'accueil
2. Une nouvelle grille est **générée aléatoirement**
3. Quelques lettres sont révélées en **indice**
4. Utilisez le **panneau de codes** (à droite) pour entrer vos hypothèses : chaque chiffre correspond à une lettre
5. Lorsqu'une correspondance est entrée, **toutes les cases** portant ce chiffre se remplissent
6. La partie est gagnée quand **toute la grille** est correctement remplie

---

## 🌍 Ajouter une langue

```bash
# Préparez votre fichier de mots :
data/<langue>/<langue>_words_raw.txt

# Puis lancez :
python tools/setup_dictionary.py --lang <langue>

# Changez la langue dans :
utils/config.py  →  CURRENT_LANGUAGE = "<langue>"
```

---

## 🛠️ Technologies

| Composant | Technologie |
|---|---|
| Langage | Python 3.10+ |
| Interface graphique | Tkinter |
| Base de données | SQLite (via `sqlite3` builtin) |
| Sauvegarde | JSON |

---

## 📜 Licence

Ce projet est distribué sous licence **MIT** — voir le fichier [LICENSE](LICENSE) pour les détails.

> ⚠️ *"Les Mots Codés"* est un concept associé aux publications de **Jean Paul Cordier**. Ce projet est une implémentation open-source à but éducatif et non commercial.

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une *issue* ou une *pull request*.

1. Fork le projet
2. Crée une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commit tes changements (`git commit -m 'feat: ajout de ma fonctionnalité'`)
4. Push sur la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvre une Pull Request
