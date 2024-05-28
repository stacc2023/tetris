from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import os

games = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

room_counter = 0
waiting_user = None
rooms_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global waiting_user, room_counter
    if waiting_user:
        room = f'room_{room_counter}'
        join_room(room, sid=waiting_user)
        join_room(room)
        if room not in rooms_users:
            rooms_users[room] = []
            rooms_users[room].append(waiting_user)
            rooms_users[room].append(request.sid)
        socketio.emit('message', {'event': 'connected', 'data': 'A new user has joined the room.'}, to=room)
        waiting_user = None
        room_counter += 1
    else:
        waiting_user = request.sid

@socketio.on('disconnect')
def handle_disconnect():
    global waiting_user
    if waiting_user == request.sid:
        waiting_user = None

    room = [room for room in socketio.server.rooms(request.sid) if room != request.sid]
    if room:
        print(room)
        emit('message', {'event': 'connected', 'data': room}, room=room[0])

@socketio.on('message')
def handle_message(data):
    room = [room for room in socketio.server.rooms(request.sid) if room != request.sid]
    print(socketio.server.rooms(request.sid), request.sid)
    if room:
        # 해당 룸의 데이터를 찾기(테트리스의 game 배열)
        emit('message', data, room=room[0])




if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

