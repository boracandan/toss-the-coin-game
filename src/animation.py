from src.settings import *

from time import perf_counter

class AsciiAnimation:
    def __init__(self, animationFrames, animationWindow, topLeft, dimensions, disableResizing = False, playContinuously = False):
        self.animationFrames = animationFrames
        self.currentFrameIndex = 0
        self.animationWindow = animationWindow

        self.width, self.height = dimensions
        self.left, self.top = topLeft

        if not disableResizing:
            self.resize_animation()

        self.animationSpeed = 15 # Frames per second
        self.preTimer, self.timer = None, None # Timer that toggles on/off every 1/(frame rate of animation)
        self.playContinuously = playContinuously

    @staticmethod
    def shrink_list(l, goalLength):
        if goalLength > len(l):
            raise ValueError("goalLength cannot be greater than the current list length.")
        diff = len(l) - goalLength
        start = diff // 2
        end = len(l) - (diff - start)
        return l[start:end]
    
    @staticmethod
    def expand_list(l, goalLength):
        if goalLength < len(l):
            raise ValueError("Target length is smaller than current length.")
        diff = goalLength - len(l)
        left_pad = [l[0]] * (diff - diff // 2)
        right_pad = [l[-1]] * (diff // 2)
        return left_pad + l + right_pad


    def resize_animation(self):
        # Width resizing
        if len(self.animationFrames[0][0]) > self.width:
            for frame in self.animationFrames:
                for i, row in enumerate(frame):
                    frame[i] = "".join(self.shrink_list(list(row), self.width))


        elif len(self.animationFrames[0][0]) < self.width:
            for frame in self.animationFrames:
                for i, row in enumerate(frame):
                    frame[i] = "".join(self.expand_list(list(row), self.width))

        # Height resizing
        if len(self.animationFrames[0]) > self.height:
            for i, frame in enumerate(self.animationFrames):
                self.animationFrames[i] = self.shrink_list(frame, self.height)

        elif len(self.animationFrames[0]) < self.height:
            for i, frame in enumerate(self.animationFrames):
                self.animationFrames[i] = self.expand_list(frame, self.height)



    @property
    def isFinished(self):
        return self.currentFrameIndex == len(self.animationFrames) - 1

    def play(self):
        if self.preTimer is not None and self.timer != self.preTimer:
            self.currentFrameIndex += 1
            
            if self.playContinuously:
                self.currentFrameIndex %= len(self.animationFrames)  # Loop back to 0
            else:
                self.currentFrameIndex = min(self.currentFrameIndex, len(self.animationFrames) - 1)       

        self.preTimer, self.timer = self.timer, perf_counter() // (1 / (self.animationSpeed)) % 2
        
        for rowIdx in range(self.height):
            self.animationWindow.add_string(self.left, rowIdx + self.top, self.animationFrames[self.currentFrameIndex][rowIdx][:self.width])

    def reset(self):
        self.currentFrameIndex = 0
        
