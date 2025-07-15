from src.settings import *
from src.ui.screen import *
from src.game_states import *
from src.utils.utility import write_dict_to_json, clear_file, pos_int
from src.animation import AsciiAnimation

from os.path import join, getsize
import json
import random
from time import sleep

class GameState(Enum):
    WELCOME = auto()
    INITIAL_BALANCE = auto()
    GAME_MENU = auto()
    PREDICTION = auto()
    COIN_FLIP = auto()
    RESULT = auto()
    CREDIT_OFFER = auto()
    GAME_OVER = auto()

class CoinTossGame:
    def __init__(self):
        self.debtThreshold = random.randint(-10000, -5000)
        self.playerBalance = None
        self.betAmount = 0
        self.coinAnimationFrames = self.load_animation(FileNames.COIN_ANIMATION_FILE)
        self.idleAnimationFrames = self.load_animation(FileNames.IDLE_ANIMATION_FILE)

        self.running = True
        self.gameOver = False
        self._loanMode = False
        self.gameState: GameState = WelcomeState(GameMenuState())

        # Create UI
        self.screen = Screen(dimensions = (200, 63))
        self.mainWin = Window(dimensions = (150, 60), beginningPoint = (0, 0), screen = self.screen)
        self.balanceWindow = Window(dimensions = (50, 3), beginningPoint = (151, 0), screen = self.screen)
        self.inputWin = InputWindow(dimensions = (150, 3), beginningPoint = (0, 60), screen = self.screen, maxInputLength = 150, startMode = "input")

        self.load_data()

        # Animations
        self.coinFlipAnimation = AsciiAnimation(animationFrames=self.coinAnimationFrames, animationWindow=self.mainWin, topLeft=(10, 5), dimensions=(128, 55))
        self.idleAnimation = AsciiAnimation(animationFrames=self.idleAnimationFrames, animationWindow=self.mainWin, topLeft=(15, 10), dimensions=(120, 40), playContinuously=True)

        # Start game
        self.start_game()


    @property
    def loanMode(self):
        return self._loanMode
    
    @loanMode.setter
    def loanMode(self, value):
        self._loanMode = bool(value)
        if self._loanMode: self.balanceWindow.resize_window((50, 4))
        

    def load_data(self):
        fullPath = join(MAIN_DIR, "Data", FileNames.DATA_FILE)
        if getsize(fullPath):
            with open(fullPath, "r") as f:
                data = json.load(f)
                self.gameMode = GameMode.from_dict(data["gameMode"])
                self.playerBalance = data["playerBalance"]
                self.loanMode = data["_loanMode"]
        
    def load_animation(self, fileName):
        animationFrames = []
        frame = []
        full_path = join(MAIN_DIR, "Animations", fileName)    
        with open(full_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.isspace():
                    animationFrames.append(frame)
                    frame = []
                else:
                    frame.append(line.strip())

        return animationFrames

    def end_game(self):
        if not self.gameOver: 
            # Exclude some keys from self.__dict__
            includedKeys = {"playerBalance", "_loanMode"}  # Add any keys you want to save
            filteredDict = {k: v for k, v in self.__dict__.items() if k in includedKeys}
            if self.gameMode:
                filteredDict["gameMode"] = self.gameMode.to_dict()

            write_dict_to_json(filteredDict, MAIN_DIR, "Data", "database.json")
        
        else: 
            clear_file(MAIN_DIR, "Data", "database.json")
        self.running = False


    def handle_input(self, input):
        if isinstance(input, str): self.gameState.handle_input(self, input)

    def render_balance(self):
        self.balanceWindow.add_string(0, 0, "Current Balance: " + (f"${self.playerBalance}" if self.playerBalance is not None else "$0"))
        if self.loanMode:
            self.balanceWindow.add_string(0, 1, f"Debt Threshold: ${self.gameMode.debtThreshold}")

    def update_display(self):
        self.mainWin.clear_strings()
        self.balanceWindow.clear_strings()
        # logging.debug(f"{self.gameState}")
        self.gameState.process(self)
        self.gameState.render(self)
        self.render_balance()

    def start_game(self):
        while self.running:
            self.update_display()
            for event in self.screen.events:
                if event == Events.EXIT:
                    self.gameState = GameExitState()
            self.handle_input(self.inputWin.userInput)
            self.screen.update()
            sleep(0.016)
            

if __name__ == "__main__":
    CoinTossGame()



