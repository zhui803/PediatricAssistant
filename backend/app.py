from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS 
from AssistantAPICall.main import *  # Make sure this import includes all needed functions

app = Flask(__name__) 
CORS(app)

# Set up MongoDB connection 
client = MongoClient('mongodb+srv://sliu484:K78iS903oYFohcca@cluster0.cjvuvqh.mongodb.net/')  
db = client['gpt_prompt']

simulationFile = loadFile("backend/AssistantAPICall/case_1.json")

temp_message = ""

# Assuming global variables for managing conversation state
conversation_thread = None
conversation_run = None

@app.route('/init-conversation', methods=['POST'])
def init_conversation():
    global conversation_thread, conversation_run, simulationFile
    if conversation_thread is None or conversation_run is None:
        # Only initialize if not already done
        data = request.json
        init_input = data.get('init_input', '')  # Optional initial input to start the conversation
        conversation_thread, conversation_run, simulationFile = initialize(init_input, simulationFile)
        print("Conversation intialized")
        return jsonify({"message": "Conversation initialized"}), 200
    else:
        return jsonify({"error": "Conversation already initialized"}), 400

@app.route('/submit-data', methods=['POST'])
def submit_data():
    data = request.json
    result = db.phase_data.insert_one(data)
    return jsonify({"message": "Data received", "id": str(result.inserted_id)}), 200

@app.route('/submit-user-input', methods=['POST'])
def submit_user_input():
    global conversation_thread, conversation_run, simulationFile, temp_message
    if conversation_thread is None or conversation_run is None:
        return jsonify({"error": "Conversation not initialized"}), 400

    data = request.json
    user_input = data.get('text')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    # Submit the new user input to the ongoing conversation
    conversation_run = submit_message(conversation_thread, user_input, simulationFile)
    
    # Wait for the run to complete and fetch the last message
    wait_on_run(conversation_run, conversation_thread)
    last_message = getChatHistory(conversation_thread)[-1]
    temp_message = last_message
    
    return jsonify({"response": last_message})

@app.route('/get-message', methods=['GET'])
def get_message():
    global temp_message
    if conversation_thread is not None:
        return jsonify({"message": temp_message})
    else:
        return jsonify({"error": "No conversation started"})

if __name__ == '__main__':
    app.run()