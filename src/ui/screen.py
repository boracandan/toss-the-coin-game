from src.settings import *

from dataclasses import dataclass
from textwrap import wrap
from enum import Enum, auto
import curses

@dataclass
class PositionedString:
    x: int
    y: int
    val: str
    wrap: bool = True

class Modes(Enum):
    STRING_MODE = auto()
    INPUT_MODE = auto()

class Events(Enum):
    EXIT = auto()
    INPUT_RECIEVED = auto()


class Screen:
    def __init__(self, dimensions):
        self.width, self.height = dimensions

        # Initializing Curses
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        # Check if terminal is large enough
        max_y, max_x = self.stdscr.getmaxyx()
        if max_y < self.height or max_x < self.width:
            curses.endwin()
            raise ValueError(f"Terminal too small. Required: {self.width}x{self.height}, found: {max_x}x{max_y}")

        self.elements = []
        self._events = []

    @property
    def events(self):
        return self._events


    def add_element(self, win):
        """Add a curses window (sub-window or pad) to the screen."""
        self.elements.append(win)

    def end(self):
        # Terminate curses screen
        curses.nocbreak()
        self.stdscr.keypad(False)
        self.stdscr.nodelay(False)
        curses.echo()
        curses.endwin()

    def update(self):
        self.events.clear()

        for element in self.elements:
            element.update()
        
        # Set cursor position on main screen for any input windows
        for element in self.elements:
            if hasattr(element, 'mode') and element.mode == Modes.INPUT_MODE:
                self.stdscr.move(element.cursorY, element.cursorX)
                break  # Only handle first input window
        
        self.stdscr.refresh()


class Window:
    def __init__(self, dimensions, beginningPoint, screen: Screen, bordered = True):
        self.screen = screen
        self.screen.add_element(self)

        self.width, self.height = (dimensions[0] - 2, dimensions[1] - 2) if bordered else dimensions
        self.left, self.top = (beginningPoint[0] + 1, beginningPoint[1] + 1) if bordered else beginningPoint 

        self.window = curses.newwin(dimensions[1], dimensions[0], beginningPoint[1], beginningPoint[0])

        self.strings = []

        self.bordered = bordered
    
    def resize_window(self, new_dimensions, new_position=None):
        if new_position is None:
            new_position = (self.left - int(self.bordered), self.top - int(self.bordered))

        # Recompute drawing dimensions
        self.width, self.height = (new_dimensions[0] - 2, new_dimensions[1] - 2) if self.bordered else new_dimensions
        self.left, self.top = (new_position[0] + 1, new_position[1] + 1) if self.bordered else new_position

        # Create new curses window
        self.window = curses.newwin(new_dimensions[1], new_dimensions[0], new_position[1], new_position[0])



    def process(self):
        self.print_strings()

    def update(self):
        self.window.clear()
        if self.bordered: self.window.box()
        self.process() 
        self.window.refresh()


    def print_strings(self):
        for string in self.strings:
            if string.wrap:
                wrappedLines = wrap(string.val, self.width - string.x, drop_whitespace = False)
                for i, line in enumerate(wrappedLines):
                    if string.y + i < self.height:
                        self.window.addnstr(string.y + i + int(self.bordered), string.x + int(self.bordered), line, self.width - string.x)
            else:
                if string.y < self.height:
                    self.window.addnstr(string.y + int(self.bordered), string.x + int(self.bordered), string.val, self.width - string.x)
        
    def add_string(self, x, y, val, wrap = True):
        self.strings.append(PositionedString(x, y, val, wrap))

    def add_positioned_string(self, pstr: PositionedString):
        self.strings.append(pstr)

    def clear_strings(self):
        self.strings.clear()

class InputWindow(Window):
    def __init__(self, dimensions, beginningPoint, screen: Screen, bordered = True, maxInputLength = 100, startMode = "string", **kwargs):
        super().__init__(dimensions, beginningPoint, screen, bordered)

        self.window.nodelay(True)
        self.change_mode(startMode, **kwargs)

        # input attributes
        self._userInput = None
        self.maxInputLength = maxInputLength

    @property
    def userInput(self):
        returnVal = self._userInput.lower().strip() if type(self._userInput) is str else self._userInput
        self._userInput = None
        return returnVal
    
    def set_prompt(self, prompt):
        self.prompt = prompt
        self.inputLine.val = self.prompt + self.inputStr

    def change_mode(self, mode, prompt = "", strings = None):
        if mode == "string":
            self.mode = Modes.STRING_MODE
            if strings:
                for string in strings:
                    self.add_string(*string)
        elif mode == "input":
            self.clear_strings()
            self.mode = Modes.INPUT_MODE
            self.prompt = prompt
            self.inputStr = ""
            self.inputLine = PositionedString(0, 0, self.prompt + self.inputStr)
            self.add_positioned_string(self.inputLine)
            self.cursorY, self.cursorX = self.top, self.left + len(self.prompt + self.inputStr) 
            curses.curs_set(1)

    
    def process(self):
        self.print_strings()
        self.get_input()

    def calculate_cursor_position(self):
        """Calculate the correct cursor position based on wrapped text."""
        full_text = self.prompt + self.inputStr
        if not full_text:
            return 0, 0
        
        # Get the wrapped lines just like in print_strings
        wrapped_lines = wrap(full_text, self.width - self.inputLine.x, drop_whitespace = False)
        
        if not wrapped_lines:
            return 0, len(full_text)
        
        # Find which line the cursor should be on
        total_chars = 0
        for i, line in enumerate(wrapped_lines):
            if total_chars + len(line) >= len(full_text):
                # Cursor is on this line
                cursor_x = self.left + self.inputLine.x + (len(full_text) - total_chars)
                cursor_y = self.top + self.inputLine.y + i
                return cursor_y, cursor_x
            total_chars += len(line)
        
        # If we get here, cursor is at the end of the last line
        cursor_y = self.left + self.inputLine.y + len(wrapped_lines) - 1
        cursor_x = self.top + self.inputLine.x + len(wrapped_lines[-1])

        return cursor_y, cursor_x
                
    def get_input(self):
        try:
            ch = self.window.getch()
            if self.mode == Modes.INPUT_MODE:
                if ch in (10, 13):  # Enter
                    # self._userInput = self.inputStr
                    # self.strings.remove(self.inputLine)
                    # self.mode = Modes.STRING_MODE
                    # curses.curs_set(0)
                    self._userInput = self.inputStr
                    self.inputStr = ""
                    self.cursorY, self.cursorX = self.top, self.left + len(self.prompt + self.inputStr) 
                    self.inputLine.val = self.prompt + self.inputStr
                
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    if len(self.inputStr) > 0:
                        self.inputStr = self.inputStr[:-1]
                    
                    # Update the input line text
                    self.inputLine.val = self.prompt + self.inputStr
                    
                    # Calculate correct cursor position
                    self.cursorY, self.cursorX = self.calculate_cursor_position()
                
                elif 32 <= ch <= 126 and len(self.inputStr) < self.maxInputLength:
                    self.inputStr += chr(ch)
                    
                    # Update the input line text
                    self.inputLine.val = self.prompt + self.inputStr
                    
                    # Calculate correct cursor position
                    self.cursorY, self.cursorX = self.calculate_cursor_position()
            if ch in (27,): # ESC
                self.screen.events.append(Events.EXIT)
        
        except:
            pass
    

    
    

    