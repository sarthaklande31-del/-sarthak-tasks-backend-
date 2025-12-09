import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)
DB_FILE = 'notes.json'

# ⚠️ PASTE YOUR KEY HERE
GENAI_API_KEY = "PASTE_YOUR_GEMINI_KEY_HERE"
genai.configure(api_key=GENAI_API_KEY)

# --- DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {"notes": []} # Simplified structure for the "Ultimate" version
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"notes": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- AI LOGIC ---
def get_ai_category(text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Categorize this text into ONE word (Todo, Shopping, Idea, Work): '{text}'"
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Unsorted"

# --- ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/notes', methods=['GET'])
def get_notes():
    return jsonify(load_db())

@app.route('/api/add', methods=['POST'])
def add_note():
    data = request.json
    db = load_db()
    
    # AI Magic
    category = get_ai_category(data['text'])
    
    new_note = {
        "id": str(datetime.datetime.now().timestamp()),
        "title": data.get('title', ''),
        "text": data['text'],
        "color": data.get('color', '#202124'), # Default Grey
        "category": category,
        "is_pinned": False,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    db['notes'].insert(0, new_note)
    save_db(db)
    return jsonify({"status": "success", "note": new_note})

@app.route('/api/update', methods=['POST'])
def update_note():
    data = request.json
    db = load_db()
    for note in db['notes']:
        if note['id'] == data['id']:
            note.update(data) # Update text, color, title
            break
    save_db(db)
    return jsonify({"status": "success"})

@app.route('/api/delete', methods=['POST'])
def delete_note():
    data = request.json
    db = load_db()
    db['notes'] = [n for n in db['notes'] if n['id'] != data['id']]
    save_db(db)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
