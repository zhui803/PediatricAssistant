 
from flask import Flask ,request, jsonify
from pymongo import MongoClient
from flask_cors import CORS 
from AssistantAPICall.main import *

app = Flask(__name__) 
CORS(app)
  
# Set up MongoDB connection 
client = MongoClient('mongodb+srv://sliu484:K78iS903oYFohcca@cluster0.cjvuvqh.mongodb.net/')  
db = client['gpt_prompt'] 

simulationFile = loadFile("PediatricSavior/backend/AssistantAPICall/case_1.json")

@app.route('/') 
def hello_world(): 
    return 'Hello, World!'

@app.route('/submit-data', methods=['POST'])
def submit_data():
    data = request.json  # Assuming the incoming data is JSON
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Assuming 'formData' is the collection you want to use
    result = db.phase_data.insert_one(data)
    
    return jsonify({"message": "Data received", "id": str(result.inserted_id)}), 200

@app.route('/submit-user-input', methods=['POST'])
def submit_user_input():
    data = request.json
    text = data['text']
    # Process the user input, generate response, etc.
    print(text)
    return jsonify({"message": "User input received", "input": text})

@app.route('/get-message', methods=['GET'])
def get_message():
    return jsonify({"message": "Message from BackEnd"})

@app.before_first_request
def start_conversation():
    thread, run, simulationFile, user_message = conversation()


  
if __name__ == '__main__': 
    app.run() 