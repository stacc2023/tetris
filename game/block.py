import numpy as np
import os
import time
from collections import defaultdict
import time
import keyboard
import asyncio

class Tetromino:
    types = ['I', 'O', 'L', 'J', 'Z', 'S', 'T']
    block_types= {
        'I': np.array([
            [0,1,0,0],
            [0,1,0,0],
            [0,1,0,0],
            [0,1,0,0]
        ]),
        'O': np.array([
            [2,2],
            [2,2],
        ]),
        'L': np.array([
            [0,3,0],
            [0,3,0],
            [0,3,3],
        ]),
        'J': np.array([
            [0,4,0],
            [0,4,0],
            [4,4,0],
        ]),
        'Z': np.array([
            [0,0,0],
            [5,5,0],
            [0,5,5],
        ]),
        'S': np.array([
            [0,0,0],
            [0,6,6],
            [6,6,0],
        ]),
        'T': np.array([
            [0,0,0],
            [0,7,0],
            [7,7,7],
        ]),
    }

class Block(Tetromino):
    type: str= None
    row_index = 0
    col_index = 0
    w = None
    h = None
    b = None

    board_w = None
    board_h = None


    def __init__(self, type: str='L', shadow= False, board_w = 20, board_h = 20):
        if type:
            self.type = type
        else:
            self.type = ['I', 'O', 'L', 'J', 'Z', 'S', 'T'][np.random.randint(0,7)]

        self.board_w = board_w
        self.board_h = board_h

        self.h = len(self.block_types[self.type])
        self.w = len(self.block_types[self.type][0])
        self.b = self.block_types[self.type]
        if shadow:
            self.b = -self.b

        self.row_index = 4 - self.h
        self.col_index = self.board_w // 2

    def rotate(self, degree):
        self.b = np.rot90(self.b, k=-degree // 90)

    def copy(self, other):
        self.type = other.type
        self.row_index = other.row_index
        self.col_index = other.col_index
        self.w = other.w
        self.h = other.h
        self.b = other.b
        self.board_h = other.board_h
        self.board_w = other.board_w

    def reset(self):
        self.row_index = 4 - self.h
        self.col_index = self.board_w // 2
