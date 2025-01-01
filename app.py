from flask import Flask, request, jsonify, render_template_string
from flask_pymongo import PyMongo
from datetime import datetime
import uuid

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://Kalpeshpawar:01042001@cluster0.s0fmo.mongodb.net/dailyTasks?retryWrites=true&w=majority"
mongo = PyMongo(app)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Task Recorder</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            text-align: center;
        }
        label, textarea, input {
            width: 100%;
            margin-bottom: 10px;
        }
        button {
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>What did you do today?</h1>
    <form id="taskForm">
        <label for="date">Date:</label>
        <input type="date" id="date" name="date" required><br>
        <label for="tasks">Tasks:</label><br>
        <textarea id="tasks" name="tasks" rows="4" required></textarea><br>
        <button type="submit">Save</button>
    </form>

    <script>
        document.getElementById('taskForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const date = document.getElementById('date').value;
            const tasks = document.getElementById('tasks').value;
            const response = await fetch('/save-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ date, tasks }),
            });
            const result = await response.json();
            alert(result.message);
        });
    </script>
</body>
</html>"""


# API to Save Task
@app.route('/save-task', methods=['POST'])
def save_task():
    data = request.json
    date = data.get('date')
    tasks = data.get('tasks')

    if not date or not tasks:
        return jsonify({'message': 'Invalid input'}), 400

    task_collection = mongo.db.tasks
    existing_task = task_collection.find_one({'date': date})

    if existing_task:
        task_collection.update_one({'date': date}, {'$set': {'tasks': tasks}})
        return jsonify({'message': 'Task updated successfully'})
    else:
        task_collection.insert_one({'date': date, 'tasks': tasks})
        return jsonify({'message': 'Task saved successfully'})

if __name__ == '__main__':
    app.run(debug=True)
