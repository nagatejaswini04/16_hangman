import random
from words import WORDS, HINTS
from stats import SessionStats


class HangmanGame:
    def __init__(self):
        self.score = 0
        self.streak = 0

        # Session-level state
        self.stats = SessionStats()

        # Round-level state
        self.category = "technology"
        self.difficulty = "medium"
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 6
        self.hint_used = False

        # Difficulty rules
        self.difficulty_rules = {
            "easy": {
                "lives": 8,
                "base_score": 3,
                "hint_penalty": 1
            },
            "medium": {
                "lives": 6,
                "base_score": 5,
                "hint_penalty": 2
            },
            "hard": {
                "lives": 4,
                "base_score": 7,
                "hint_penalty": 3
            }
        }

    def start_round(self):
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()

        # Set lives according to the current round's difficulty
        self.lives = self.difficulty_rules[self.difficulty]["lives"]

        self.hint_used = False

    def masked(self):
        return " ".join(
            ch if ch in self.guessed else "_"
            for ch in self.secret
        )

    def won(self):
        return all(
            ch in self.guessed
            for ch in set(self.secret)
        )

    def guess(self, letter):
        if len(letter) != 1 or not letter.isalpha():
            return "Enter one letter."

        # Task 1: repeated correct/wrong guesses
        # must not consume another life
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."

        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."

        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        if self.hint_used:
            return None

        self.hint_used = True

        # Task 3: hint penalty depends on difficulty
        hint_penalty = self.difficulty_rules[
            self.difficulty
        ]["hint_penalty"]

        self.score = max(0, self.score - hint_penalty)

        return HINTS.get(
            self.secret,
            "No hint available."
        )

    def play_round(self):
        self.start_round()

        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print(
                "Wrong:",
                " ".join(sorted(self.wrong)) or "-"
            )
            print(
                "Difficulty:",
                self.difficulty.capitalize(),
                "Lives:",
                self.lives,
                "Score:",
                self.score,
                "Streak:",
                self.streak
            )

            raw = input(
                "Letter, /hint, or /quit: "
            ).strip().lower()

            if raw == "/quit":
                return False

            if raw == "/hint":
                hint = self.use_hint()
                print(
                    hint if hint else "Hint already used."
                )
                continue

            print(self.guess(raw))

        if self.won():
            self.streak += 1

            # Difficulty changes the base score.
            base_score = self.difficulty_rules[
                self.difficulty
            ]["base_score"]

            # Existing streak behavior is preserved.
            self.score += base_score + self.streak

            # Task 2: record completed winning round.
            self.stats.record(True, self.streak)

            print("Solved:", self.secret)
            return True

        # Lost round
        self.streak = 0

        # Task 2: record completed losing round.
        self.stats.record(False, self.streak)

        print(
            "Out of lives. The word was:",
            self.secret
        )
        return True

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")

        while True:
            # Category selection is preserved
            print(
                "\nCategories:",
                ", ".join(WORDS)
            )

            raw = input(
                "Choose category or q: "
            ).strip().lower()

            if raw == "q":
                return

            if raw not in WORDS:
                print("Unknown category.")
                continue

            self.category = raw

            # Task 3: choose difficulty for each round
            print(
                "\nDifficulty: easy, medium, hard"
            )

            difficulty = input(
                "Choose difficulty: "
            ).strip().lower()

            if difficulty not in self.difficulty_rules:
                print("Unknown difficulty. Using medium.")
                difficulty = "medium"

            self.difficulty = difficulty

            if not self.play_round():
                return

            again = input(
                "Another round? [y/n]: "
            ).strip().lower()

            if again != "y":
                print(
                    "Final score:",
                    self.score,
                    " Streak:",
                    self.streak
                )
                return