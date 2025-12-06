from flask import Flask, jsonify, request
from flask_cors import CORS
import json, os

DATA_FILE = 'tasks.json'
app = Flask(__name__)
CORS(app)

def read_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def write_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(read_tasks())

@app.route('/add', methods=['POST'])
def add_task():
    data = request.get_json() or {}
    task = (data.get('task') or '').strip()
    if not task:
        return jsonify({'error':'empty'}), 400
    tasks = read_tasks()
    tasks.append(task)
    write_tasks(tasks)
    return jsonify({'ok':True}), 201

@app.route('/delete/<int:index>', methods=['DELETE'])
def delete_task(index):
    tasks = read_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        write_tasks(tasks)
        return jsonify({'ok':True})
    return jsonify({'error':'index'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
