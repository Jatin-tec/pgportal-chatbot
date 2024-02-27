from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('/index.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
    return 'message was received!!!'


def UserMessageReceived(methods=['GET', 'POST']):
    print('Server received user message!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', str('from server connection sucessful'))

@socketio.on('user_message')
def handle_user_message(json, methods=['GET', 'POST']):
    print('Client message received: ' + str(json))
    response_array = ["hello", "how", "are", "you", "I", "am", "fine", "bye"]
    for msg in response_array:
        time.sleep(0.5)
        socketio.emit('user_response', str(msg), callback=UserMessageReceived)

if __name__ == '__main__':
    socketio.run(app, debug=True)