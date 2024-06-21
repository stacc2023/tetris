import sys
sys.path.insert(1, './')
from game.__main__ import Game
from socketio import AsyncServer
import asyncio


class WebGame(Game):
    score = 0

    def __init__(self, user, socket: AsyncServer, room, rooms_users, sid):
        super().__init__()
        self.user = user
        self.socket = socket
        self.room = room
        self.rooms_users = rooms_users
        self.sid = sid 


    hotkeys = ['ArrowRight', 'ArrowLeft', 'KeyX', 'KeyZ', 'Space', 'Enter', 'KeyC', 'ArrowDown']

    async def display(self):
        rid = [room for room in self.socket.rooms(self.sid) if room != self.sid][0]
        if rid:
            result = self.rooms_users[rid]
            tmp = {}
            for sid in result:
                tmp[sid] = {'board': result[sid]['data'].b.b.tolist(), 
                            'next_block': result[sid]['data'].next_t.b.tolist(),
                            'hold_block': result[sid]['data'].hold_t.b.tolist() if result[sid]['data'].hold_t else None,
                            'score': result[sid]['data'].score
                            }
            result = {'event': 'display', 'name': result[self.sid]['name'], 'data': tmp, 'sid': self.sid}
            # 해당 룸의 데이터를 찾기(테트리스의 game 배열)
            await self.socket.emit('message', result, room=rid)

    async def start(self):
        # 블럭 줄 없애기
        cnt = self.b.clear()
        if cnt == 1:
            self.score += 100
        elif cnt == 2:
            self.score += 250
        elif cnt == 3:
            self.score += 450
        elif cnt == 4:
            self.score += 700

        # 블럭을 초기화 하고 게임 오버 여부를 판단
        if self.make_block() == False:
            # game over
            self.b.b[self.b.b > 0] = 8
            self.gameover = True
            # display
            await self.display()
            return
        while True:        
            await asyncio.sleep(0.2)
            if self.droped:
                self.droped = False
                break
            if self.move('D') == False:
                await self.start()
                break
            await self.display()
    
   