from src.settings import *
from utils.utility import pos_int
from src.main import CoinTossGame

from abc import ABC, abstractmethod
import time
from random import choice


class GameState(ABC):
    playsIdleAnimation = True

    @abstractmethod
    def render(self, game: CoinTossGame):
        """Render the Game State, updating the display"""

    def handle_input(self, game: CoinTossGame, userInput: str):
        """Handle user input for the spesific game state"""

    def process(self, game: CoinTossGame):
        """Processes background logic (e.g., timers, animations)"""
        if self.playsIdleAnimation:
            game.idleAnimation.play()

class TimedState(GameState):
    def __init__(self, scheduledState = None, onTimerEnd = None):
        self.startTime = time.time()
        self.scheduledState = scheduledState
        self.onTimerEnd = onTimerEnd

    def process(self, game):
        super().process(game)

        if time.time() - self.startTime > self.timerDuration:
            if self.scheduledState:
                game.gameState = self.scheduledState
            if self.onTimerEnd:
                self.onTimerEnd()
        


class CutSceneState(GameState):
    def __init__(self, scheduledState, prompts, timerDuration = 0, waitForUserInput = False, onSceneEnd = None):
        self.startTime = time.time()
        self.scheduledState = scheduledState
        self.prompts = prompts
        self.timerDuration = timerDuration
        self.onSceneEnd = onSceneEnd
        self.waitForUserInput = waitForUserInput
    
    def process(self, game):
        if self.timerDuration:
            if time.time() - self.startTime > self.timerDuration:
                if self.scheduledState:
                    game.gameState = self.scheduledState
                if self.onSceneEnd:
                    self.onSceneEnd()

    def render(self, game):
        for idx, prompt in enumerate(self.prompts):
            game.mainWin.add_string(0, idx, prompt)

    def handle_input(self, game, userInput):
        if self.waitForUserInput:
            if self.scheduledState:
                game.gameState = self.scheduledState
            if self.onSceneEnd:
                    self.onSceneEnd()

class ModeSelectState(GameState):
    def render(self, game):
            game.mainWin.add_string(0, 0, Prompt.WELCOME)
            game.mainWin.add_string(0, 1, Prompt.SELECT_MODE)
            game.mainWin.add_string(0, 2, "Write 'help' if you want additional information about the modes.")
        
    def handle_input(self, game, userInput):
        match userInput: 
                case mode if mode.lower() in ("easy", "e"):
                    game.gameMode = GAME_MODES["easy"]
                    game.playerBalance = game.gameMode.initialBalance
                    game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.EASY_MODE_INTRO], timerDuration=2)
                case mode if mode.lower() in ("moderate", "m"):
                    game.gameMode = GAME_MODES["moderate"]
                    game.playerBalance = game.gameMode.initialBalance
                    game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.MODERATE_MODE_INTRO], timerDuration=2)
                case mode if mode.lower() in ("hard", "h"):
                    game.gameMode = GAME_MODES["hard"]
                    game.playerBalance = game.gameMode.initialBalance
                    game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.HARD_MODE_INTRO], timerDuration=2)
                case mode if mode.lower() in ("intense", "i"):
                    game.gameMode = GAME_MODES["intense"]
                    game.playerBalance = game.gameMode.initialBalance
                    game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.INTENSE_MODE_INTRO], timerDuration=2)
                case command if command.lower() in ("help", "h"):
                    game.gameState = CutSceneState(scheduledState=ModeSelectState(), prompts=[Prompt.MODE_INFO.format(name = GAME_MODES["easy"].name,
                                                                                                initialBalance = GAME_MODES["easy"].initialBalance,
                                                                                                goalMoney = GAME_MODES["easy"].goalMoneyAmount),
                                                                        Prompt.MODE_INFO.format(name = GAME_MODES["moderate"].name,
                                                                                                initialBalance = GAME_MODES["moderate"].initialBalance,
                                                                                                goalMoney = GAME_MODES["moderate"].goalMoneyAmount),
                                                                        Prompt.MODE_INFO.format(name = GAME_MODES["hard"].name,
                                                                                                initialBalance = GAME_MODES["hard"].initialBalance,
                                                                                                goalMoney = GAME_MODES["hard"].goalMoneyAmount),
                                                                        Prompt.MODE_INFO.format(name = GAME_MODES["intense"].name,
                                                                                                initialBalance = GAME_MODES["intense"].initialBalance,
                                                                                                goalMoney = GAME_MODES["intense"].goalMoneyAmount)], waitForUserInput=True)
                case _:
                    game.gameState = CutSceneState(scheduledState=ModeSelectState(), prompts=[Prompt.INVALID_INPUT], timerDuration=1)


class InitialBalanceState(GameState):
    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.WELCOME)
        game.mainWin.add_string(0, 1, Prompt.MONEY_INPUT)
    
    def handle_input(self, game, userInput):
        try:
            parsed = pos_int(userInput)
        except ValueError:
            parsed = userInput
    
        match parsed: 
                case int(balance) if balance > 0:
                    game.playerBalance = balance
                    if balance <= 1000:
                        game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.POOR_PLAYER_INTRO], timerDuration=2)
                    else:
                        game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.RICH_PLAYER_INTRO], timerDuration=2)
                case _:
                    game.gameState = CutSceneState(scheduledState=InitialBalanceState(), prompts=[Prompt.INVALID_INPUT], timerDuration=1)
    

class WelcomeState(TimedState):
    timerDuration = 5
    
    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.WELCOME)

        if game.playerBalance is None: # If new game
            game.gameState = ModeSelectState()

        else:
            game.mainWin.add_string(0, 1, Prompt.CONTINUE_GAME)
    
    def handle_input(self, game, userInput):
        match userInput:
                case None:
                    ...
                case command if command.lower() in NEGATIVE_PHRASES:
                    game.gameState = ...
                case command if command.lower() in POSITIVE_PHRASES:
                    game.gameState = ...
                case _:
                    game.gameState = WelcomeState()
    
class GameMenuState(GameState):
    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.HOW_MUCH)
    
    def handle_input(self, game, userInput):
        try:
            parsed = pos_int(userInput)
        except ValueError:
            parsed = userInput
    
        match parsed:
                case int(betAmount) if 0 < betAmount <= game.playerBalance - (game.gameMode.debtThreshold if game.loanMode else 0):
                    # Update player balance and get to the prediction state
                    game.playerBalance -= betAmount
                    game.betAmount = betAmount
                    game.gameState = PredictionState()
                case _:
                    game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.INVALID_INPUT], timerDuration=1)
    


    
class PredictionState(GameState):
    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.ASK_CHOICE)
    
    def handle_input(self, game, userInput):
        match userInput:
                case prediction if prediction.lower() in ("tails", "t"):
                    game.gameState = CoinFlipState("tails")
                case prediction if prediction.lower() in ("heads", "h"):
                    game.gameState = CoinFlipState("heads")
                case _:
                    game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.INVALID_INPUT], timerDuration=1)
    
class CoinFlipState(GameState):
    def __init__(self, playerPrediction):
        self.playerPrediction = playerPrediction

    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.COIN_FLIP)
    
    def process(self, game):
        game.coinFlipAnimation.play()

        if not game.coinFlipAnimation.isFinished:
            return

        result = choice(["heads", "tails"])
        game.coinFlipAnimation.reset()

        if result == self.playerPrediction:
            game.playerBalance += game.betAmount * 2

            if game.playerBalance >= game.gameMode.goalMoneyAmount:
                game.gameOver = True
                game.gameState = CutSceneState(
                    scheduledState=None,
                    prompts=[Prompt.GAME_WON.format(mode=game.gameMode.name)],
                    timerDuration=3,
                    onSceneEnd=game.end_game
                )
                return

            game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.LUCKY_WINNER], timerDuration=1.5)
            return

       # Wrong prediction
        if game.loanMode:
            # Check if player is still above debt threshold
            if game.playerBalance > game.gameMode.debtThreshold:
                game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.LOSS_MESSAGE], timerDuration=1.5)
            else:
                game.gameOver = True
                game.gameState = CutSceneState(scheduledState=None, prompts=[Prompt.GAME_OVER], timerDuration=3, onSceneEnd=game.end_game)
        else:
            # Player has no more money and loans are disabled → offer loan
            if game.playerBalance > 0:
                game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.LOSS_MESSAGE], timerDuration=1.5)
            else:
                game.gameState = LoanOfferState()



class LoanOfferState(GameState):
    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.ASK_LOAN_CHOICE)
    
    def handle_input(self, game, userInput):
        match userInput:
            case command if command.lower() in NEGATIVE_PHRASES:
                game.gameOver = True
                game.gameState = CutSceneState(scheduledState=None, prompts=[Prompt.GAME_OVER], timerDuration=1.5, onSceneEnd=game.end_game)
            case command if command.lower() in POSITIVE_PHRASES:
                game.loanMode = True
                game.gameState = CutSceneState(scheduledState=GameMenuState(), prompts=[Prompt.LOANS_ENABLED], timerDuration=1.5)
            case _:
                game.gameState = CutSceneState(scheduledState=LoanOfferState(), prompts=[Prompt.RETRY_INPUT], timerDuration=1.5)


class GameExitState(TimedState):
    timerDuration = 2
    def render(self, game):
        game.mainWin.add_string(0, 0, Prompt.LEAVE_GAME.format(balance = game.playerBalance))
    
    def process(self, game):
        if time.time() - self.startTime > self.timerDuration:
            # Change state when timer over
            game.end_game()


