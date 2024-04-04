import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS 
from flask_cors import cross_origin
from AssistantAPICall.main import *  # Make sure this import includes all needed functions
from dotenv import load_dotenv
from datetime import datetime, timezone
load_dotenv()

app = Flask(__name__) 
CORS(app)

# Set up MongoDB connection 
client = MongoClient(os.environ.get('MONGO_DB_CONNECTION_STRING', 'your_default_connection_string'))
db = client[os.environ.get('DB_NAME', 'tests')]


simulationFile = loadFile("backend/AssistantAPICall/case_1.json")

temp_message = ""

# Assuming global variables for managing conversation state
conversation_thread = None
conversation_run = None

def store_conversation(user_input, bot_response):
    """Store the conversation in the MongoDB collection."""
    conversation_data = {
        'user_input': user_input,
        'bot_response': bot_response,
        'timestamp': datetime.now(timezone.utc) # Store the current timestamp
    }
    try:
        # Insert the conversation data into the 'conversations' collection
        db.conversations.insert_one(conversation_data)
    except Exception as e:
        print(f"An error occurred while inserting to MongoDB: {e}")


@app.route('/init-conversation', methods=['POST'])
@cross_origin()
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
@cross_origin()
def submit_data():
    data = request.json
    result = db.cases.insert_one(data)
    return jsonify({"message": "Data received", "id": str(result.inserted_id)}), 200

@app.route('/submit-user-input', methods=['POST'])
@cross_origin()
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

    # Store the conversation after each exchange
    store_conversation(user_input, last_message)

    temp_message = last_message
    
    return jsonify({"response": last_message})

@app.route('/get-message', methods=['GET'])
@cross_origin()
def get_message():
    global temp_message
    if conversation_thread is not None:
        return jsonify({"message": temp_message})
    else:
        return jsonify({"error": "No conversation started"})

if __name__ == '__main__':
    app.run(port=4999)