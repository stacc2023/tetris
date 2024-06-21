import sys
sys.path.insert(1, './')

import socketio
import asyncio
from aiohttp import web


from web.webgame import WebGame
import os
base_dir = os.path.abspath(os.path.dirname(__file__))


sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

room_counter = 0
waiting_user = None
rooms_users = {}

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse(os.path.join(base_dir, 'index.html'))

@sio.on('connect')
async def handle_connect(sid, data):
    global waiting_user, room_counter
    print('cunnected:', sid)
    if waiting_user:
        await sio.emit('sid', sid, to=sid)
        room = f'room_{room_counter}'
        await sio.enter_room(room=room, sid=waiting_user)
        await sio.enter_room(room=room, sid=sid)
        if room not in rooms_users:
            rooms_users[room] = {}
            rooms_users[room][waiting_user] = {'name': 'user1', 'data': WebGame(user='user1', socket=sio, room=room, rooms_users=rooms_users, sid=waiting_user)}
            rooms_users[room][sid] = {'name': 'user2', 'data': WebGame(user='user2', socket=sio, room=room, rooms_users=rooms_users, sid=sid)}
        await sio.emit('message', {'event': 'connected', 'data': 'A new user has joined the room.'}, to=room)
        asyncio.create_task(rooms_users[room][waiting_user]['data'].start())
        asyncio.create_task(rooms_users[room][sid]['data'].start())
        waiting_user = None
        room_counter += 1
    else:
        waiting_user = sid
        await sio.emit('sid', sid, to=sid)

@sio.on('disconnect')
async def handle_disconnect(sid):
    global waiting_user
    if waiting_user == sid:
        waiting_user = None
    else:
        rid = [room for room in sio.rooms(sid) if room != sid][0]
        if rid:
            del rooms_users[rid][sid]
            await sio.emit('message', {'event': 'connected', 'data': rid}, room=rid)

# 클라이언트로부터 키보드 이벤트를 수신
@sio.on('message')
async def handle_message(sid, data):
    # 입력된 키
    key = data['data']['key']
    if key in WebGame.hotkeys:
        # 유저가 속한 룸의 이름 추출(유저 본인의 고유 룸 제외)
        rid = [room for room in sio.rooms(sid) if room != sid][0]
        if rid:
            room = rooms_users[rid]
            user = room[sid]
            g: WebGame = user['data']
            if g.gameover:
                return

            flag = False
            if key == 'ArrowRight':
                flag = g.move('R')
            elif key == 'ArrowLeft':
                flag = g.move('L')
            elif key == 'ArrowDown':
                flag = g.move('D')
            elif key == 'KeyZ':
                print(1)
                flag = g.rotate(True)
            elif key == 'KeyX':
                flag = g.rotate()
            elif key == 'KeyC':
                flag = g.hold()
            elif key == 'Space':
                while g.move('D'):
                    pass
                g.droped = True
                asyncio.create_task(g.start())
                return
            if flag:
                await g.display()

app.add_routes(routes)
if __name__ == '__main__':
    web.run_app(app,host='0.0.0.0', port=8000)

