from random import randint

class GuessingGame:
    def __init__(self, start_range=0, end_range=101, hints_on=True):
        if start_range > end_range:
            raise ValueError("End range must be higher than start range.")
        self.start_range = start_range
        self.end_range = end_range
        self.hints_on = hints_on
        self.count = 0

    def valid_guess(self, guess):
        try:
            guess = int(guess)
        except:
            return False
        return self.start_range <= guess <= self.end_range

    def get_guess(self):
        guess = input(f"Enter a number between {self.start_range} - {self.end_range}\n")
        if self.valid_guess(guess):
            return int(guess)
        else:
            print(f"Your guess \"{guess}\" is not a valid guess.\n")
            return self.get_guess()

    def play(self):
        secret_number = randint(self.start_range, self.end_range)

        while True:
            guess = self.get_guess()
            self.count += 1

            if guess == secret_number:
                break
            elif self.hints_on:
                if guess < secret_number:
                    print("Higher\n")
                else:
                    print("Lower\n")

        print(f"You guessed the secret number {secret_number}! It took you {self.count} guesses. Noice!")


if __name__ == "__main__":
    GuessingGame(0, 20).play()