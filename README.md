<h1 align="center">
    Minesweeper
</h1>

<h4 align="center">
    The classic minesweeper game in python
</h4>

## Setup

```bash
python3 -m venv venv
venv/bin/pip install pyxel
```

## Usage

```bash
venv/bin/python3 minesweeper.py
```

## Controls

- **Left click** — reveal tile
- **Right click** — toggle flag
- **R** — restart game

## Web Export

Build a standalone `index.html` for GitHub Pages:

```bash
venv/bin/pyxel package . minesweeper.py
venv/bin/pyxel app2html minesweeper.pyxapp
mv minesweeper.html index.html
```
