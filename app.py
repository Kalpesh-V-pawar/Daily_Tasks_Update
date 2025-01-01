from flask import Flask, request, jsonify, render_template_string
from flask_pymongo import PyMongo
from datetime import datetime
import uuid


# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://Kalpeshpawar:01042001@cluster0.s0fmo.mongodb.net/dailyTasks?retryWrites=true&w=majority"
mongo = PyMongo(app)

app = Flask(__name__, template_folder='templates')

@app.route("/")
def home():
    return render_template("index.html")  # Serve the HTML file


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
