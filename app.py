from llm_wrapper.wrapper import LLMWrapper
from flask import Flask, render_template
from flask_socketio import SocketIO
import weaviate
import openai
import dotenv
import time
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('/index.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
    return 'message was received!!!'

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', str('from server connection sucessful'))

@socketio.on('user_message')
def handle_user_message(json, methods=['GET', 'POST']):
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_APIKEY")
    wrapper = LLMWrapper()
    
    # API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")

    # vectrstore = weaviate.Client("http://localhost:8080",
    #         additional_headers={
    #             "X-HuggingFace-Api-Key": API_TOKEN
    # })

    response = wrapper.generate_response(str(json))
    response_msg = ""
    for r in response:
        if r["choices"][0]["delta"] == {}:
            break
        msg = r["choices"][0]["delta"]["content"]
        response_msg += msg
        socketio.emit('user_response', str(msg))
    wrapper.history.append({
        "role": "user", 
        "content": response_msg
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)
