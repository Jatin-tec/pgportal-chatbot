from llm_wrapper.wrapper import LLMWrapper
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from database.utils.embedding import huggingface_ef
from chromadb.config import Settings
import pymongo
import chromadb
import openai
import dotenv
import json
import os
import time

dotenv.load_dotenv()

# Weaviate setup
chroma_host = os.getenv("CHROMA_HOST")
vectorstore = chromadb.HttpClient(host=chroma_host, port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))

def wait_for_chroma_service(client, timeout=60):
    """Wait for the Chroma service to be ready before proceeding."""
    start_time = time.time()
    while True:
        try:
            # Attempt to call the heartbeat method
            response = client.heartbeat()
            # Assuming a successful call returns a timestamp or similar
            if response:
                print("Chroma service is up and running.")
                break
        except Exception as e:
            # Handle exceptions, which likely indicate that the service is not yet ready
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print("Timeout waiting for Chroma service to be ready.")
                exit(1)
            print("Waiting for Chroma service to be ready...")
            time.sleep(5)  # wait for 5 seconds before trying again

# Place this at the beginning of your Flask application's startup routine
wait_for_chroma_service(vectorstore)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['DEBUG'] = True
openai.api_key = os.getenv("OPENAI_APIKEY")
socketio = SocketIO(app)

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
            try:
                wrapper = user_sessions[session_id]["wrapper"]
                response = wrapper.generate_response(user_message, vectorstore)
                response_msg = ""
                for r in response:
                    if r["choices"][0]["delta"] == {}:
                        break
                    msg = r["choices"][0]["delta"]["content"]
                    response_msg += msg
                    socketio.emit('user_response', { "message": msg, "options": None }, room=session_id)
                wrapper.history.append({
                    "role": "user", 
                    "content": response_msg
                }) 
            except:
                print("Error generating response")
                response_msg = "This service is currently unavailable. Please try again later."
                options = {
                    "Back to main menu": conversation_data['initial_step']
                }
    else:
        next_step_key = get_next_step(session_id, user_message)

        if next_step_key:
            next_step = conversation_data['steps'][next_step_key]
            response_msg = next_step['message']
            options = next_step.get('options', None)
            
            if next_step_key == "grievance_category":
                
                collection = vectorstore.get_collection(name="Departments", embedding_function=huggingface_ef)
                results = collection.query(
                    query_texts=user_message,
                    n_results=10
                )
                print(results)
                options = {}
                if results and results["documents"]:
                    for i, result in enumerate(results["documents"][0]):
                        options[result] = results["ids"][0][i]

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
