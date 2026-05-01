from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["memory_db"]

users = db["users"]
notes = db["notes"]

# Register
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if users.find_one({"email": data["email"]}):
        return jsonify({"message": "User already exists"})
    
    users.insert_one(data)
    return jsonify({"message": "Registration successful"})

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users.find_one({"email": data["email"], "password": data["password"]})
    
    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})

# Save note
@app.route("/save_note", methods=["POST"])
def save_note():
    data = request.json
    
    notes.update_one(
        {"date": data["date"], "month": data["month"], "year": data["year"]},
        {"$set": {"note": data["note"]}},
        upsert=True
    )
    
    return jsonify({"message": "Saved"})

# Get note
@app.route("/get_note", methods=["POST"])
def get_note():
    data = request.json
    note = notes.find_one({
        "date": data["date"],
        "month": data["month"],
        "year": data["year"]
    })
    
    if note:
        return jsonify({"note": note["note"]})
    else:
        return jsonify({"note": ""})

# Search
@app.route("/search", methods=["POST"])
def search():
    keyword = request.json["keyword"]
    result = notes.find({"note": {"$regex": keyword, "$options": "i"}})

    output = []
    for r in result:
        output.append({
            "date": r["date"],
            "month": r["month"],
            "year": r["year"],
            "note": r["note"]
        })

    return jsonify(output)

app.run(debug=True)