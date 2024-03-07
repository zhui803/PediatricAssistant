 
from flask import Flask ,request, jsonify
from pymongo import MongoClient
from flask_cors import CORS 

app = Flask(__name__) 
CORS(app)
  
# Set up MongoDB connection 
client = MongoClient('mongodb+srv://sliu484:K78iS903oYFohcca@cluster0.cjvuvqh.mongodb.net/')  
db = client['gpt_prompt'] 

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

@app.route('/get-message', methods=['GET'])
def get_message():
    return jsonify({"message": "This is a message from Flask"})
  
if __name__ == '__main__': 
    app.run() 