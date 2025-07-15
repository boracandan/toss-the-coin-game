from enum import StrEnum
from os.path import dirname, abspath, join
from random import randint
import logging

logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
    filemode='w'  # Overwrite on each run
)

class Prompt(StrEnum):
    WELCOME = "Welcome to Double or Nothing, this is a game of luck and self-control. I hope you are ready to restrain your animalistic instincts..."
    MONEY_INPUT = "Now let's see how rich you are, how much money do you want to play with: (in $)"
    EASY_MODE_INTRO = "Ohh you poor little coward. Anyway let's get tossin the coins!"
    MODERATE_MODE_INTRO = "Okay, we're playing it safe. Anyway let's get tossin the coins!"
    INTENSE_MODE_INTRO = "INTENSE is no joke my boy, but it's your choice. Anyway let's get tossin the coins!"
    HARD_MODE_INTRO = "It's gonna be a challenge, be ready my boy. Anyway let's get tossin the coins!"
    INVALID_INPUT = "You can't trick me you little prick."
    ASK_CHOICE = "Heads or tails son: [H/T]"
    LUCKY_WINNER = "You lucky little son of a bitch. Promise is promise I am doubling your money now."
    LOSS_MESSAGE = "Ops, looks like somebody has lost the bet."
    RETRY_INPUT = "I didn't understand that. Please type yes/y or no/n."
    COIN_FLIP = "Oki Doki time for flippin!"
    CONTINUE_GAME = "Welcome back sir, let's continue playing shall we!"
    DOUBLE_OR_NOTHING = "Do you want to double or nothing with your ${balance}:"
    HOW_MUCH = "How much money do you want to double or nothing with?"
    LEAVE_GAME = "Leaving the game with a current balance of ${balance}, this amount will automatically be saved for your next game."
    GAME_OVER = "Unfortunately the saga ends here my guy, come again when you have money."
    CREDIT_PREPOSITION = "Looks like somebody's out of dollars! Would you want to capitalize on the casino's credit system, don't forget this will be your debt so don't exaggerate!" \
    "\nGet Credit: [Yes/No]"
    ASK_LOAN_CHOICE = "Looks like someone's broooke, would you like to continue on playing with loans or leave with your honor?"
    LOANS_ENABLED = "Ho hooo, we have a real gambling addict over here. Let's continue tossing 'em coins then!"
    SELECT_MODE = "What mode do you want to play in? [Easy, Moderate, Hard, Intense]"
    MODE_INFO = "{name}: Initial Balance = {initialBalance}, Goal Money = {goalMoney}"
    GAME_WON = "Holy moly, that was a good run, you have completed the {mode} level. I am proud of you son. Hope to see you again one time!"


class FileNames(StrEnum):
    COIN_ANIMATION_FILE = "coin_flip_animation.txt"
    IDLE_ANIMATION_FILE =  "idle_animation.txt"
    DATA_FILE = "database.json"

class GameMode:
    def __init__(self, name, debtThreshold, goalMoneyAmount, initialBalance = None):
        self.name = name
        self.initialBalance = initialBalance
        self.debtThreshold = debtThreshold
        self.goalMoneyAmount = goalMoneyAmount
    
    def to_dict(self):
        return {
            "name": self.name,
            "debtThreshold": self.debtThreshold,
            "goalMoneyAmount": self.goalMoneyAmount,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            debtThreshold=data["debtThreshold"],
            goalMoneyAmount=data["goalMoneyAmount"]
        )
    


NEGATIVE_PHRASES = ("exit", "no", "n", "q", "quit")
POSITIVE_PHRASES = ("yes", "y")

MAIN_DIR = dirname(dirname(abspath(__file__))) # Gets the main folder

GAME_MODES = {
    "easy": GameMode("Easy", initialBalance=1000, debtThreshold=randint(-5000, -4000), goalMoneyAmount=4000),
    "moderate": GameMode("Moderate", initialBalance=1000, debtThreshold=randint(-4000, -3000), goalMoneyAmount=7500),
    "hard": GameMode("Hard", initialBalance=1000, debtThreshold=randint(-3000, -2000), goalMoneyAmount=12500),
    "intense": GameMode("Intense", initialBalance=1000, debtThreshold=randint(-2000, -1000), goalMoneyAmount=15000),
}