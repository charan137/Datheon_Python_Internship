"""Hangman - a console word guessing game.

The player has 6 incorrect attempts to guess a hidden word letter by letter.
Features: ASCII gallows that updates per wrong guess, tracking of guessed
letters, and no penalty for repeated guesses.
"""

import random
import string

MAX_ATTEMPTS = 6

WORDS = [
    "python", "variable", "function", "internet", "keyboard", "algorithm",
    "database", "compiler", "network", "software", "developer", "terminal",
    "string", "integer", "boolean", "library", "debugging", "iteration",
]

GALLOWS = [
    # 0 wrong guesses
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    # 1
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    # 2
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    # 3
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    # 4
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    # 5
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    # 6
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========""",
]


def choose_word(words=WORDS):
    """Return a random word from the word list (lowercase)."""
    return random.choice(words).lower()


def mask_word(word, guessed):
    """Return the word with unguessed letters replaced by underscores."""
    return " ".join(ch if ch in guessed else "_" for ch in word)


def is_word_guessed(word, guessed):
    """True if every letter of the word has been guessed."""
    return all(ch in guessed for ch in word)


def validate_guess(raw, guessed):
    """Validate raw input. Returns (letter, error_message).

    If the input is valid and new, error_message is None.
    Repeated letters return an error so no penalty is applied.
    """
    guess = raw.strip().lower()
    if len(guess) != 1 or guess not in string.ascii_lowercase:
        return None, "Please enter a single letter (a-z)."
    if guess in guessed:
        return None, f"You already guessed '{guess}'. No penalty - try another."
    return guess, None


def display_state(word, guessed, wrong_count):
    """Print the gallows, masked word and guessed letters."""
    print(GALLOWS[wrong_count])
    print(f"\nWord:    {mask_word(word, guessed)}")
    wrong_letters = sorted(g for g in guessed if g not in word)
    print(f"Guessed: {' '.join(sorted(guessed)) or '-'}")
    print(f"Wrong:   {' '.join(wrong_letters) or '-'}")
    print(f"Attempts left: {MAX_ATTEMPTS - wrong_count}\n")


def play_round():
    """Play a single round. Returns True if the player won."""
    word = choose_word()
    guessed = set()
    wrong_count = 0

    print("\n=== HANGMAN ===")
    print(f"I'm thinking of a {len(word)}-letter word.")

    while wrong_count < MAX_ATTEMPTS and not is_word_guessed(word, guessed):
        display_state(word, guessed, wrong_count)
        letter, error = validate_guess(input("Guess a letter: "), guessed)
        if error:
            print(error)
            continue

        guessed.add(letter)
        if letter in word:
            print(f"Good guess! '{letter}' is in the word.")
        else:
            wrong_count += 1
            print(f"Sorry, '{letter}' is not in the word.")

    display_state(word, guessed, wrong_count)
    if is_word_guessed(word, guessed):
        print(f"You won! The word was '{word}'.")
        return True
    print(f"You lost! The word was '{word}'.")
    return False


def ask_play_again():
    """Ask whether the player wants another round."""
    while True:
        answer = input("\nPlay again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer y or n.")


def main():
    wins = losses = 0
    while True:
        if play_round():
            wins += 1
        else:
            losses += 1
        print(f"Score - Wins: {wins}  Losses: {losses}")
        if not ask_play_again():
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGame exited. Goodbye!")
