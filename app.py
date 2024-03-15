from llm_wrapper.wrapper import LLMWrapper
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import pymongo
import chromadb
import openai
import dotenv
import json
import os

dotenv.load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
openai.api_key = os.getenv("OPENAI_APIKEY")
socketio = SocketIO(app)

# Weaviate setup
vectorstore = chromadb.HttpClient(host='chromadb', port=8000)

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["gov"]
grievance_collection = db["grievances"]

@app.route('/')
def sessions():
    # Render the index.html page from base directory
    return render_template('index.html')

# Placeholder for storing user session data
user_sessions = {}
with open('chat.json') as f:
  conversation_data = json.load(f)

def get_next_step(session_id, user_input):
    current_step = user_sessions[session_id]["current_step"]
    step_data = conversation_data['steps'][current_step]

    if "input_required" in step_data and step_data["input_required"]:
        user_sessions[session_id]["data"][current_step] = user_input
        next_step = step_data["next"]
    elif "options" in step_data:
        for option_key, option_value in step_data['options'].items():
            if user_input.lower() == option_value.lower():
                next_step = option_value
                break
        else:
            next_step = current_step  # stay on current step if no option matches
    else:
        next_step = step_data.get("next", None)
    
    user_sessions[session_id]["current_step"] = next_step
    return next_step

@socketio.on('connect')
def handle_connect():
    session_id = request.sid
    wrapper = LLMWrapper()
    user_sessions[session_id] = {
        "current_step": conversation_data["initial_step"], 
        "data": {},
        "wrapper": wrapper,
        }
    print(f"User connected: {session_id}")

@socketio.on('start_conversation')
def handle_start_conversation():
    print("Starting conversation")
    session_id = request.sid
    current_step = conversation_data["initial_step"]
    response_msg = conversation_data['steps'][current_step]['message']
    options = conversation_data['steps'][current_step].get('options', None)
    socketio.emit('first_message', { "message": response_msg, "options": options }, room=session_id)

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    del user_sessions[session_id]
    print(f"User disconnected: {session_id}")

@socketio.on('user_message')
def handle_user_message(json, methods=['GET', 'POST']):
    session_id = request.sid
    user_message = json["message"]
    print(f"User message: {user_message}")
    print(f"Use llm: {user_sessions[session_id].get('use_llm', False)}")
    if user_sessions[session_id].get("use_llm", False):
        if user_message.lower() == 'quit faq':
            # User wants to quit FAQ mode
            user_sessions[session_id]["use_llm"] = False
            user_sessions[session_id]["current_step"] = "anything_else"
            next_step = conversation_data['steps']['anything_else']
            response_msg = next_step['message']
            options = next_step.get('options', None)
        else:   
            # Use LLM to generate response
            wrapper = user_sessions[session_id]["wrapper"]
            response = wrapper.generate_response(user_message, vectorstore)
            response_msg = ""
            for r in response:
                if r["choices"][0]["delta"] == {}:
                    break
                # print(r)
                msg = r["choices"][0]["delta"]["content"]
                response_msg += msg
                socketio.emit('user_response', { "message": msg, "options": None }, room=session_id)
            wrapper.history.append({
                "role": "user", 
                "content": response_msg
            }) 
    else:
        next_step_key = get_next_step(session_id, user_message)
    
        if next_step_key:
            next_step = conversation_data['steps'][next_step_key]
            response_msg = next_step['message']
            options = next_step.get('options', None)
            if next_step_key == "faqs":
                user_sessions[session_id]["use_llm"] = True                
            elif next_step_key == "yes":
                # Save the collected data to MongoDB
                grievance_data = user_sessions[session_id]["data"]
                grievance_collection.insert_one(grievance_data)
                # Reset the user session
                user_sessions[session_id] = {"current_step": conversation_data["initial_step"], "data": {}}
        else:
            response_msg = "I didn't understand that. Can you try again? Choose from the options provided."
            options = next_step.get('options', None)
            
        socketio.emit('user_response', { "message": response_msg, "options": options }, room=session_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
