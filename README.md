# Datheon Python Internship

Submission repository for the Datheon Python Programming Internship. 

## Tasks

| # | Task | Folder | Status |
|---|------|--------|--------|
| 1 | Hangman Word Guessing Game (Console) | [`task1_hangman/`](task1_hangman) | Complete |
| 2 | Stock Portfolio Performance Tracker | [`task2_portfolio/`](task2_portfolio) | Complete |
| 3 | Automated File Organizer & Cleanup Utility | [`task3_file_organizer/`](task3_file_organizer) | Complete |
| 4 | Rule-Based Interactive Terminal Assistant | [`task4_terminal_assistant/`](task4_terminal_assistant) | Complete |
| 5 | Enterprise Smart Inventory & Asset System | [`task5_inventory_asset_system/`](task5_inventory_asset_system) | Complete |

---

# Task 1: Hangman Word Guessing Game (Console)

A terminal-based Hangman game written in Python. The player guesses a hidden word letter by letter within 6 incorrect attempts.

## Features
- 6 incorrect attempts per round
- ASCII gallows art that updates after every wrong guess
- Tracks all guessed letters and the wrong ones separately
- Repeated guesses are detected and do **not** deduct an attempt
- Input validation (single letters a-z only)
- Multiple rounds with a running win/loss score
- Graceful exit on Ctrl+C / Ctrl+D

## Installation

Requirements: Python 3.8 or newer. No external libraries are needed.

```bash
git clone https://github.com/charan137/Datheon_Python_Internship.git
cd Datheon_Python_Internship/task1_hangman
python hangman.py
```

(On some systems use `python3` instead of `python`.)

## How to Play
1. A random word is chosen and shown as underscores.
2. Type one letter per turn and press Enter.
3. Correct letters are revealed in place; wrong letters add a part to the hangman.
4. Reveal the whole word to win. Make 6 wrong guesses and you lose.

## Architecture

The program is split into small, single-purpose functions, with game state kept in local variables inside `play_round`.

```
main()
 └── loop: play_round() → show score → ask_play_again()

play_round()
 ├── choose_word()        pick a random word from WORDS
 ├── display_state()      print gallows, masked word, guessed/wrong letters
 │     └── mask_word()    build "_ a _ _" view of the word
 ├── validate_guess()     check input is a single new letter (no penalty on repeats)
 └── is_word_guessed()    win condition check
```

| Function | Responsibility |
|----------|----------------|
| `choose_word()` | Returns a random lowercase word |
| `mask_word(word, guessed)` | Hides unguessed letters with underscores |
| `is_word_guessed(word, guessed)` | True when all letters are found |
| `validate_guess(raw, guessed)` | Returns `(letter, error)`; rejects invalid or repeated input |
| `display_state(...)` | Renders ASCII art and status lines |
| `play_round()` | Runs one full game and returns win/loss |
| `ask_play_again()` | Prompts for another round |
| `main()` | Top-level loop and score tracking |

**Data structures:** a `set` holds guessed letters (fast lookup, automatically prevents duplicates), a `list` holds the 7 ASCII gallows stages indexed by the wrong-guess count, and a `list` holds the word bank.

# Task 2: Stock Portfolio Performance Tracker

A command-line utility that values entered stock holdings, calculates gain or loss per holding and for the portfolio, and appends timestamped snapshots to a CSV file.

## Features
- Accepts ticker symbols, purchase prices, and share quantities
- Retrieves the latest available regular-market prices from Yahoo Finance
- Displays invested value, current value, and percentage return
- Appends holding and portfolio totals to `portfolio_summary.csv`
- Uses only Python's standard library; a network connection is required for quotes

## Installation and Usage

Requirements: Python 3.8 or newer. No external libraries are needed.

```bash
cd task2_portfolio
python3 portfolio.py
```

Quotes may be delayed or reflect the last market close. Pass `--csv PATH` to write snapshots to a different CSV file.

# Task 3: Automated File Organizer & Cleanup Utility

A command-line utility that sorts files into category folders by extension. It previews changes by default, avoids overwriting files, and can optionally scan subdirectories.

## Features
- Organizes documents, images, videos, audio, archives, code, and unknown file types
- Defaults to a non-destructive dry run; `--apply` performs the moves
- Supports opt-in recursive scanning with `--recursive`
- Renames collisions with numbered suffixes and reports filesystem errors
- Uses only Python's standard library

## Installation and Usage

Requirements: Python 3.8 or newer. No external libraries are needed.

```bash
cd task3_file_organizer
python3 organizer.py ~/Downloads --recursive
python3 organizer.py ~/Downloads --recursive --apply
```

The first command previews the planned changes. The second performs them.

# Task 4: Rule-Based Interactive Terminal Assistant

A rule-based terminal chatbot that answers FAQ questions, recognizes multiple intents per message, remembers the previous answer for follow-ups, and provides suggestions when it cannot confidently match a query.

## Features
- Loads greetings and question-answer pairs from JSON
- Supports multiple FAQ matches in a single user message
- Handles contextual repeat requests, fallback suggestions, and clean exit commands
- Includes an editable sample FAQ dataset and supports custom JSON files
- Uses only Python's standard library

## Installation and Usage

Requirements: Python 3.8 or newer. No external libraries are needed.

```bash
cd task4_terminal_assistant
python3 chatbot.py
```

Pass `--faq PATH` to load a different FAQ JSON file.

# Task 5: Enterprise Smart Inventory & Asset System

An object-oriented inventory system with an abstract `LibraryItem` base class, specialized book, magazine, and digital-media models, checkout and return workflows, overdue fees, and audit reporting.

## Features
- Encapsulated attributes with validated properties
- Abstract methods and polymorphic fee and metadata behavior
- Safe inventory operations with unique IDs and synchronized manager access
- Checkout and return audit records with tabular inventory and audit reports
- Uses only Python's standard library

## Installation and Usage

Requirements: Python 3.8 or newer. No external libraries are needed.

```bash
cd task5_inventory_asset_system
python3 inventory.py
```

The manager and audit log are in-memory and reset when the process exits.

## Author
Charan
