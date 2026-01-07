from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-it'
socketio = SocketIO(app, cors_allowed_origins="*")


users = {} 
messages = [] 

@app.route('/')
def index():
    """عرض صفحة الشات الرئيسية"""
    return render_template('chat.html')


@socketio.on('connect')
def handle_connect():
    """عند اتصال مستخدم جديد"""
    print(f'✅ User connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """عند انفصال مستخدم"""
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        emit('user_left', {'username': username}, broadcast=True)
        print(f'❌ User disconnected: {username}')

@socketio.on('join')
def handle_join(data):
    """عند انضمام مستخدم للشات"""
    username = data['username']
    users[request.sid] = username
    
    emit('previous_messages', {'messages': messages})
    
    emit('user_joined', {
        'username': username,
        'users_count': len(users)
    }, broadcast=True)
    
    print(f'👤 {username} joined the chat. Total users: {len(users)}')

@socketio.on('send_message')
def handle_message(data):
    """عند إرسال رسالة"""
    username = users.get(request.sid, 'Anonymous')
    message_data = {
        'username': username,
        'message': data['message']
    }
    
    messages.append(message_data)
    
    if len(messages) > 50:
        messages.pop(0)
    
    emit('receive_message', message_data, broadcast=True)
    print(f'💬 {username}: {data["message"]}')

@socketio.on('typing')
def handle_typing(data):
    """عند كتابة مستخدم (اختياري)"""
    username = users.get(request.sid, 'Anonymous')
    emit('user_typing', {'username': username}, broadcast=True, include_self=False)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(
        app, 
        debug=False,   
        host='0.0.0.0', 
        port=port
    )
