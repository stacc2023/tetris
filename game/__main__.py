import numpy as np
import os
import time
from collections import defaultdict
import time
import keyboard
import asyncio
import sys
sys.path.insert(1, './')


from game.board import Board
from game.block import Block, Tetromino
from game.cursor import move, get_cursor_position

class Game:
    pocket = None
    t = None
    next_t = None
    s = None
    b = None
    prev_b = None
    
    droped = False

    def __init__(self, w=10, h=20):
        self.w = w
        self.h = h
        self.b = Board(self.w, self.h)

        self.pocket = self.make_pocket()
        self.next_pocket = self.make_pocket()

        return

    def display(self):
        # 출력이 처음이면 화면을 초기화하고 전부 출력
        if self.prev_b == None:
            os.system('cls')
            for i in range(3, len(self.b.b)):
                for col in self.b.b[i]:
                    if col>0:
                        print(f'\033[9{col-1}m■\033[0m', end=' ', flush=True)
                    elif col<0:
                        print(f'\033[9{(-col-1)}m□\033[0m', end=' ', flush=True)
                    else:
                        print(' ', end=' ', flush=True)
                print()
        #출력이 처음이 아니면 바뀐 부분만 출력
        else:
            move(0,0)
            for i in range(3, len(self.b.b)):
                for j, col in enumerate(self.b.b[i]):
                    if self.prev_b.b[i][j] != self.b.b[i][j]:
                        move(j*2,i-3)
                        if col>0:
                            print(f'\033[9{col-1}m■\033[0m', end=' ', flush=True)
                        elif col<0:
                            print(f'\033[9{(-col-1)}m□\033[0m', end=' ', flush=True)
                        else:
                            print(' ', end=' ', flush=True)
                print()

        self.prev_b = Board(self.b.w, self.b.h)
        self.prev_b.b = self.b.b.copy()
        

        move(30, 0)
        print('NEXT', end='', flush=True)
        for i in range(4):
            move(30, i+1)
            for j in range(4):
                if i <= self.next_t.h and j <= self.next_t.w:
                    val = self.next_t.b[i-1][j-1]
                    if val:
                        print(f'\033[9{val-1}m■\033[0m', end=' ', flush=True)
                    else:
                        print(' ', end=' ', flush=True)
                else:
                    print(' ', end=' ', flush=True)
            print(flush=True)

    def make_pocket(self):
        indices = np.random.choice(np.arange(0,7), 7, False)
        types = np.vectorize(lambda i: Tetromino.types[i])(indices)
        pocket = []
        for type in types:
            b = Block(type)
            b.row_index = 4 - b.h
            b.col_index = self.w // 2
            pocket.append(b)
        return pocket

    def make_block(self):

        # 다음 블럭이 저장되어 있다면 그것을 사용
        if self.next_t:
            self.t = self.next_t
            if len(self.pocket):
                self.next_t = self.pocket.pop()
            else:
                self.pocket = self.next_pocket
                self.next_pocket = self.make_pocket()
                self.next_t = self.pocket.pop()
        # 다음 블럭이 없다면 새로 할당
        else:
            if len(self.pocket) > 1:
                self.t = self.pocket.pop()
                self.next_t = self.pocket.pop()
            elif len(self.pocket) == 1:
                self.t = self.pocket.pop()
                self.pocket = self.next_pocket
                self.next_pocket = self.make_pocket()
                self.next_t = self.pocket.pop()
            else:
                self.pocket, self.next_pocket = self.next_pocket, self.make_pocket()
                self.t, self.next_t = self.pocket.pop(), self.pocket.pop()

        # 블럭과 그림자 블럭을 초기화
        t = self.t

        s = Block(t.type, shadow=True)
        s.row_index = 4 - t.h
        s.col_index = self.w // 2

        s.row_index += 1
        while self.b.collision(s) == False:
            s.row_index += 1
        s.row_index -= 1

        # 만약에 처음 위치에서도 충돌이 발생하면(생성하자 마자 충돌이 발생) 게임 오버
        if self.b.collision(s) == False:
            self.s = s
            self.t = t
            self.b.insert(s)
            self.b.insert(t)
            return True
        else:
            return False

    async def start(self):
        # 블럭 줄 없애기
        self.b.clear()

        # 블럭을 초기화 하고 게임 오버 여부를 판단
        if self.make_block() == False:
            # game over
            self.b.b[self.b.b > 0] = 8
            self.display()
            return
        self.display()
        while True:        
            await asyncio.sleep(0.2)
            if self.droped:
                self.droped = False
                break
            if self.move('D') == False:
                await self.start()
                break
            self.display()

    def move(self, d):
        self.b.remove(self.t)

        if d == 'D':
            self.t.row_index += 1
            if self.b.collision(self.t):
                self.t.row_index -= 1
                self.b.insert(self.t)
                return False
            else:
                self.b.insert(self.t)

        elif d=='L':
            if self.t.col_index == 0:
                self.b.insert(self.t)
                return False
            self.t.col_index -= 1
            if self.b.collision(self.t):
                self.t.col_index += 1
                self.b.insert(self.t)
                return False
            else:
                self.insert()
            
        elif d=='R':
            self.t.col_index += 1

            if self.b.collision(self.t): # collision
                self.t.col_index -= 1
                self.b.insert(self.t)
                return False
            else:
                self.insert()
        return True
    
    def move_shadow(self):
        self.b.remove(self.s)
        self.s.type = self.t.type
        self.s.col_index = self.t.col_index
        self.s.b = -self.t.b
        self.s.row_index = self.t.row_index + 1
        while self.b.collision(self.s) == False:
            self.s.row_index += 1
        self.s.row_index -= 1
        self.b.insert(self.s)

    def insert(self):
        self.move_shadow()
        self.b.insert(self.t)

    def rotate(self, reverse=False):
        self.b.remove(self.t)
        self.t.rotate(-90 if reverse else 90)
        # 충돌 발생
        if self.b.collision(self.t):
            # 왼쪽 벽이 아니라면 오른쪽으로 이동해봄
            self.t.col_index += 1
            # 충돌 안했다면 쉐도우 이동
            if self.b.collision(self.t) == False:
                self.insert()
                return True
            else:
                self.t.col_index -= 1
            # 오른쪽 벽
            if self.t.col_index > 0:
                self.t.col_index -= 1
                if self.b.collision(self.t) == False:
                    self.insert()
                    return True
                else:
                    self.t.col_index += 1
            # 위
            if self.t.row_index > 0:
                self.t.row_index -= 1
                if self.b.collision(self.t) == False:
                    self.insert()
                    return True
                else:
                    self.t.row_index += 1
            self.t.rotate(90 if reverse else -90)
            self.b.insert(self.t)
            return False
        else:
            self.insert()
            return True
                
    def hold(self):
        self.b.remove(self.t)
        if self.b.collision(self.next_t) == False:
            self.t.row_index = 4 - self.t.h
            self.t.col_index = self.w // 2
            self.t, self.next_t = self.next_t, self.t
            self.insert()
            return True
        else:
            self.b.insert(self.t)
            return False

    async def handle_keyboard_events(self):
        while True:
            event = await asyncio.to_thread(keyboard.read_event)
            # print("Keyboard event:", event)
            if event.event_type == 'up':
                continue

            if event.name == "esc":
                break
            elif event.name == 'left': # move left
                if self.move('L'):
                    self.display()
            elif event.name == 'right': # move right
                if self.move('R'):
                    self.display()
            elif event.name == 'down': # soft drop 1
                if self.move('D'):
                    self.display()
            elif event.name == 'c': # hold
                if self.hold():
                    self.display()
            elif event.name == 'space': # hard drop
                while self.move('D'):
                    pass
                self.droped = True
                self.display()
                asyncio.create_task(self.start())
            elif event.name == 'z': #reverse rotation
                if self.rotate(reverse=True):
                    self.display()
            elif event.name == 'x': # rotation
                if self.rotate():
                    self.display()

async def main():
    g = Game()
    
    game_task = asyncio.create_task(g.start())
    keyboard_task = asyncio.create_task(g.handle_keyboard_events())
    
    await game_task
    await keyboard_task
    
if __name__ == '__main__':
    asyncio.run(main())