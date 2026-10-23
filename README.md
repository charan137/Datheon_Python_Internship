# Datheon Python Internship

Submission repository for the Datheon Python Programming Internship.

## Tasks

| # | Task | Folder | Status |
|---|------|--------|--------|
| 1 | Hangman Word Guessing Game (Console) | [`task1_hangman/`](task1_hangman) | Complete |
| 2 | _Add your second task here_ | `task2_.../` | Pending |
| 3 | _Optional third task_ | `task3_.../` | Pending |

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

## Author
Charan
