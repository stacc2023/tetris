import numpy as np
import os
import time
from collections import defaultdict
import time
import keyboard
import asyncio

from game.block import Block

class Board:
    prev_t = None

    def __init__(self, w=10, h=20):
        self.w = w
        self.h = h
        self.b = np.array(
            [[8] + [0] * w + [8]] * (h+3)
            + [[8] * (w + 2)]
        )
    
    def clear(self):
        cnt = 0
        for i in range(len(self.b)-2,-1,-1):
            if 0 not in self.b[i]:
                self.b = np.delete(self.b, i, 0)
                cnt += 1
        for _ in range(cnt):
            self.b = np.insert(self.b, 0, [8] + [0] * self.w + [8], axis=0)
        return cnt

    def collision(self, t: Block):
        y = 0 if t.row_index < 0 else t.row_index
        x = 0 if t.col_index < 0 else t.col_index

        area = self.b[y:y + t.h, x:x + t.w]
        block = t.b[:area.shape[0], :area.shape[1]]
        if (((area > 0) & (block != 0)) != 0).sum():
            return True
        return False


    def remove(self, t: Block):
        area = self.b[t.row_index:t.row_index + t.h, t.col_index:t.col_index + t.w]
        block = t.b[:area.shape[0], :area.shape[1]]
        area[area == block] -= block[area == block]


    def insert(self, t: Block):
        area = self.b[t.row_index:t.row_index + t.h, t.col_index:t.col_index + t.w]
        block = t.b[:area.shape[0], :area.shape[1]]
        condition = (area == 0) | ((area < 0) & (block > 0))
        area[condition] = block[condition]