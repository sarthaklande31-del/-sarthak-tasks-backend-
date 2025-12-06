from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = 'database.json'

def load_db():
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "last_reset": datetime.now().strftime("%Y-%m-%d")}
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            
            # === SELF-HEALING LOGIC ===
            # If we detect the old "List" format, we wipe it and start fresh.
            if isinstance(data, list):
                print("Old database format detected. Upgrading to Sarthak 2.0...")
                return {"tasks": [], "last_reset": datetime.now().strftime("%Y-%m-%d")}
            
            return data
    except Exception as e:
        print(f"Database Error: {e}")
        return {"tasks": [], "last_reset": datetime.now().strftime("%Y-%m-%d")}

def save_db(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Sarthak 2.0 Backend: ONLINE"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    data = load_db()
    
    # Check for Daily Reset
    today = datetime.now().strftime("%Y-%m-%d")
    if data.get("last_reset") != today:
        for task in data["tasks"]:
            task["done"] = False
        data["last_reset"] = today
        save_db(data)
        
    return jsonify(data["tasks"])

@app.route('/add', methods=['POST'])
def add_task():
    data = load_db()
    req = request.json or {}
    
    new_task = {
        "text": req.get("task", "Untitled"),
        "category": req.get("category", "General"),
        "priority": req.get("priority", "Normal"),
        "done": False,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    
    data["tasks"].append(new_task)
    save_db(data)
    return jsonify({"message": "Task created", "task": new_task})

@app.route('/toggle/<int:index>', methods=['POST'])
def toggle_task(index):
    data = load_db()
    tasks = data["tasks"]
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index]["done"]
        save_db(data)
        return jsonify({"success": True})
    return jsonify({"error": "Invalid index"}), 400

@app.route('/delete/<int:index>', methods=['DELETE'])
def delete_task(index):
    data = load_db()
    tasks = data["tasks"]
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_db(data)
        return jsonify({"success": True})
    return jsonify({"error": "Invalid index"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
