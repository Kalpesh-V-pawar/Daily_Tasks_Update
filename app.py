import sys
import os
import flask
from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from datetime import datetime
import requests
import pytz
from flask import session
from bson.objectid import ObjectId
import base64
import json  # Add this line
from flask import redirect, url_for
from functools import wraps




app = Flask(__name__)
app.secret_key = "376757980"  # must be set for session to work

# MongoDB Atlas connection string
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set. Please set it as an environment variable.")

GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
if not GOOGLE_SCRIPT_URL:
    print("Warning: GOOGLE_SCRIPT_URL is not set. Data will only be saved to MongoDB.")

GOOGLE_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbw1eEVY9hYlkkiDk6DFWRIBUq1ecojZLFcYC6OoXV4lfucaJE844qcgm-u0IaDyaCYG/exec"

client = MongoClient(mongo_uri)
db = client['dailyTasks']
task_collection = db['tasks']
task_collection1 = db['paisatransactions']
login_collection = db['uspass']
notes_collection = db['notes']

def send_to_google_sheets(data):
    if not GOOGLE_SCRIPT_URL:
        return {"status": "skipped", "message": "Google Script URL not configured"}
    
    try:
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=data,
            timeout=10  # Set a timeout to prevent hanging
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"Google Sheets API error: HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send data to Google Sheets: {str(e)}"
        }




Maine_page = """
<html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    
    <title>Login page</title>
    <link rel="icon" href="https://raw.githubusercontent.com/Kalpesh-V-pawar/Daily_Tasks_Update/main/img/kal.png" type="image/png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Consumption Tracker</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
                background-size: 300% 300%;
                animation: gradientBG 10s ease infinite;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
    
            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
    
            .container {
                background: linear-gradient(135deg, #30343F, #404452);
                backdrop-filter: blur(12px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                max-width: 425px;
                width: 90%;
                text-align: center;
                background-size: 200% 200%;
                animation: containerGradient 6s ease infinite;
            }
    
            @keyframes containerGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
    
            h1 {
                font-size: 2rem;
                margin-bottom: 25px;
            }
    
            label {
                display: block;
                margin: 12px 0 6px;
                font-size: 1rem;
            }
    
            input, textarea {
                width: 100%;
                padding: 8px;
                margin-bottom: 18px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                background: linear-gradient(135deg, #2e323d, #3a3e4a);
                color: #ffffff;
                box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.3);
                resize: none;
            }
    
            input:focus, textarea:focus {
                outline: none;
                background: linear-gradient(135deg, #383c48, #464a56);
            }
    
            button {
                background-color: #ff758c;
                color: #ffffff;
                border: none;
                padding: 14px 22px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
            }
    
            button:hover {
                background-color: #ffde59;
                color: #2e2e3e;
                transform: scale(1.05);
            }
    
            @media (max-width: 768px) {
                h1 {
                    font-size: 1.7rem;
                }
    
                button {
                    font-size: 0.9rem;
                }
            }
            .toggle-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                margin-bottom: 15px;
            }
            .toggle-label {
                font-size: 1rem;
                color: #555;
            }
            .toggle-switch {
                position: relative;
                display: inline-block;
                width: 40px;
                height: 20px;
            }
            .toggle-switch input {
                display: none;
            }
            .slider {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                border-radius: 20px;
                transition: 0.4s;
                cursor: pointer;
            }
            .slider::before {
                position: absolute;
                content: "";
                height: 14px;
                width: 14px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                border-radius: 50%;
                transition: 0.4s;
            }
            input:checked + .slider {
                background-color: #4CAF50;
            }
            input:checked + .slider::before {
                transform: translateX(20px);
            }
            label, input, textarea, button {
                display: block;
                width: 100%;
                margin-bottom: 10px;
                font-size: 1rem;
            }
    
        </style>   
    </head>
    <body>
        <div class="container">
            <h1>Enter your pass</h1><br><br>
            <form id = "Loginform" onsubmit="return false;">
                <label for="user">Username:</label>
                <input type="text" id="user" name="user" required><br><br>
                <label for="pass">Password:</label>
                <input type="password" id="pass" name="pass" required><br><br>
                <button type="submit">login</button>
                <div id="errorfooter"></div>
            </form>    
        </div>
     <script>
        const farm = document.getElementById('Loginform');
        const err = document.getElementById('errorfooter'); 
        farm.addEventListener("submit",async(e)=>{
           e.preventDefault();
           err.textContent = "";
            const usr = document.getElementById('user').value;
            const psr = document.getElementById('pass').value; 
                const response = await fetch('/save_login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ usr, psr }),
                });
                const result = await response.json();
                //alert(result.message); shows alert for every message fail, pass
                if (result.status === "success") {
                 window.location.href = "/LOGIN_page"}
                else {
                  err.textContent = result.message;
                } 
        });
     </script>  
    </body>  

</html>    
"""


@app.route('/save_login', methods=['POST'])
def save_login():
    dataup = request.json
    usern = dataup.get('usr')
    pasrn = dataup.get('psr')
    usr = login_collection.find_one({
       'usernamem' : usern,
       'passwordm' : pasrn
    })
    if usr:
        session['logged_in'] = True
        session['username'] = usern
        return {"status": "success", "message": "Login successful"}
        #return redirect (url_for('LOGIN_page')) for direct redirect, but as in js response & result are awaiting reply, they seek status & message, and only one return cab be used
    else:
        return {"status": "fail", "message": "Invalid username or password"}    

@app.route("/LOGIN_page")
def LOGIN_page_route():
    if not session.get('logged_in') :
      return redirect (url_for("login"))
    return render_template_string(LOGIN_page)

LOGIN_page = """
<html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    
    <title>Login page</title>
    <link rel="icon" href="https://raw.githubusercontent.com/Kalpesh-V-pawar/Daily_Tasks_Update/main/img/kal.png" type="image/png">
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
                background-size: 300% 300%;
                animation: gradientBG 10s ease infinite;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
    
            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
    
            .container {
                background: linear-gradient(135deg, #30343F, #404452);
                backdrop-filter: blur(12px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                max-width: 425px;
                width: 90%;
                text-align: center;
                background-size: 200% 200%;
                animation: containerGradient 6s ease infinite;
            }
    
            @keyframes containerGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
    
            h1 {
                font-size: 2rem;
                margin-bottom: 25px;
            }
    
            label {
                display: block;
                margin: 12px 0 6px;
                font-size: 1rem;
            }
    
            input, textarea {
                width: 100%;
                padding: 8px;
                margin-bottom: 18px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                background: linear-gradient(135deg, #2e323d, #3a3e4a);
                color: #ffffff;
                box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.3);
                resize: none;
            }
    
            input:focus, textarea:focus {
                outline: none;
                background: linear-gradient(135deg, #383c48, #464a56);
            }
    
            button {
                background-color: #ff758c;
                color: #ffffff;
                border: none;
                padding: 14px 22px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
            }
    
            button:hover {
                background-color: #ffde59;
                color: #2e2e3e;
                transform: scale(1.05);
            }
    
            @media (max-width: 768px) {
                h1 {
                    font-size: 1.7rem;
                }
    
                button {
                    font-size: 0.9rem;
                }
            }
            .toggle-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                margin-bottom: 15px;
            }
            .toggle-label {
                font-size: 1rem;
                color: #555;
            }
            .toggle-switch {
                position: relative;
                display: inline-block;
                width: 40px;
                height: 20px;
            }
            .toggle-switch input {
                display: none;
            }
            .slider {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                border-radius: 20px;
                transition: 0.4s;
                cursor: pointer;
            }
            .slider::before {
                position: absolute;
                content: "";
                height: 14px;
                width: 14px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                border-radius: 50%;
                transition: 0.4s;
            }
            input:checked + .slider {
                background-color: #4CAF50;
            }
            input:checked + .slider::before {
                transform: translateX(20px);
            }
            label, input, textarea, button {
                display: block;
                width: 100%;
                margin-bottom: 10px;
                font-size: 1rem;
            }
    
        </style>    
    </head>
    <body>
<div class="container">    
 <div style="display: flex; flex-direction: column; gap: 16px; align-items: center; margin-top: 20px;">    
        <h1>Enter your details</h1><br><br>
 <div style="display: flex; flex-direction: column; gap: 16px; align-items: center; margin-top: 20px;">
    <form action="{{ url_for('dailytasks') }}" method="get">
        <button type="submit">Go to Second Page</button>
    </form>

    <form action="{{ url_for('paisa') }}" method="get">
        <button type="submit">Go to dengi Page</button>
    </form>

    <form action="{{ url_for('notes') }}" method="get">
        <button type="submit">Go to notee Page</button>
    </form>  
 <div class="container">  
    <script type='text/javascript' src='//pl26677118.profitableratecpm.com/a7/0f/34/a70f3406ef58579888372fbebaa0bcd4.js'></script>
   </body>     
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Task Recorder</title>
    <link rel="icon" href="https://raw.githubusercontent.com/Kalpesh-V-pawar/Daily_Tasks_Update/main/img/kal.png" type="image/png">
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
            background-size: 300% 300%;
            animation: gradientBG 10s ease infinite;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            background: linear-gradient(135deg, #30343F, #404452);
            backdrop-filter: blur(12px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            max-width: 425px;
            width: 90%;
            text-align: center;
            background-size: 200% 200%;
            animation: containerGradient 6s ease infinite;
        }

        @keyframes containerGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin: 12px 0 6px;
            font-size: 1rem;
        }

        input, textarea {
            width: 100%;
            padding: 8px;
            margin-bottom: 18px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            background: linear-gradient(135deg, #2e323d, #3a3e4a);
            color: #ffffff;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.3);
            resize: none;
        }

        input:focus, textarea:focus {
            outline: none;
            background: linear-gradient(135deg, #383c48, #464a56);
        }

        button {
            background-color: #ff758c;
            color: #ffffff;
            border: none;
            padding: 14px 22px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
        }

        button:hover {
            background-color: #ffde59;
            color: #2e2e3e;
            transform: scale(1.05);
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.7rem;
            }

            button {
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>What did you do today?</h1>
        <form id="taskForm">
            <label for="date">Date:</label>
            <input type="date" id="date" name="date" required>

            <label for="tasks">Tasks:</label>
            <textarea id="tasks" name="tasks" rows="4" required></textarea>

            <button type="submit">Save</button>
        </form>
    </div>

    <script>
        document.getElementById('taskForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const date = document.getElementById('date').value;
            const tasks = document.getElementById('tasks').value;
            const response = await fetch('/save_task', {
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
    <script type='text/javascript' src='//pl26677118.profitableratecpm.com/a7/0f/34/a70f3406ef58579888372fbebaa0bcd4.js'></script>
</body>
</html>
"""


Paisa_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Money Consumption Tracker</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ff7eb3, #ff758c, #fdb15c, #ffde59, #a7ff83, #17c3b2, #2d6cdf, #7c5cdb);
            background-size: 300% 300%;
            animation: gradientBG 10s ease infinite;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            background: linear-gradient(135deg, #30343F, #404452);
            backdrop-filter: blur(12px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            max-width: 425px;
            width: 90%;
            text-align: center;
            background-size: 200% 200%;
            animation: containerGradient 6s ease infinite;
        }

        @keyframes containerGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin: 12px 0 6px;
            font-size: 1rem;
        }

        input, textarea {
            width: 100%;
            padding: 8px;
            margin-bottom: 18px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            background: linear-gradient(135deg, #2e323d, #3a3e4a);
            color: #ffffff;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.3);
            resize: none;
        }

        input:focus, textarea:focus {
            outline: none;
            background: linear-gradient(135deg, #383c48, #464a56);
        }

        button {
            background-color: #ff758c;
            color: #ffffff;
            border: none;
            padding: 14px 22px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
        }

        button:hover {
            background-color: #ffde59;
            color: #2e2e3e;
            transform: scale(1.05);
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.7rem;
            }

            button {
                font-size: 0.9rem;
            }
        }
        .toggle-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .toggle-label {
            font-size: 1rem;
            color: #555;
        }
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 40px;
            height: 20px;
        }
        .toggle-switch input {
            display: none;
        }
        .slider {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            border-radius: 20px;
            transition: 0.4s;
            cursor: pointer;
        }
        .slider::before {
            position: absolute;
            content: "";
            height: 14px;
            width: 14px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            border-radius: 50%;
            transition: 0.4s;
        }
        input:checked + .slider {
            background-color: #4CAF50;
        }
        input:checked + .slider::before {
            transform: translateX(20px);
        }
        label, input, textarea, button {
            display: block;
            width: 100%;
            margin-bottom: 10px;
            font-size: 1rem;
        }

    </style>
</head>
<body>

<div class="container">
    <h1>You consumed money today? Enter details</h1>
    
    <!-- Toggle Switch -->
    <div class="toggle-container">
        <span class="toggle-label">Manual</span>
        <label class="toggle-switch">
            <input type="checkbox" id="toggleMode">
            <span class="slider"></span>
        </label>
        <span class="toggle-label">Auto</span>
    </div>
    
    <form id="paisa_form">
        <label for="date2">Date:</label>
        <input type="datetime-local" id="date2" name="date2" required>

        <label for="amount">Enter amount:</label>
        <input type="number" id="amount" name="amount" step="0.01" required>

        <label for="usage">Usage description:</label>
        <textarea id="usage" name="usage" rows="4" required></textarea>
                    
        <button type="submit">Save</button>
    </form>
</div>

<script>
    const toggleMode = document.getElementById('toggleMode');
    const dateInput = document.getElementById('date2');

    toggleMode.addEventListener('change', () => {
        if (toggleMode.checked) {
            // Auto mode: Set to current India time
            const now = new Date().toLocaleString('en-GB', { 
                timeZone: 'Asia/Kolkata', 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit', 
                hour: '2-digit', 
                minute: '2-digit' 
            }).replace(',', ''); // Remove the comma between date and time
            
            // Convert 'DD/MM/YYYY HH:MM' → 'YYYY-MM-DDTHH:MM' for input field format
            const [date, time] = now.split(' ');
            const [day, month, year] = date.split('/');
            const formattedDate = `${year}-${month}-${day}T${time}`;
            
            dateInput.value = formattedDate;
            dateInput.disabled = true; // Disable input in auto mode
        } else {
            // Manual mode: Enable date input
            dateInput.value = "";
            dateInput.disabled = false;
        }
    });

    document.getElementById('paisa_form').addEventListener('submit', async (e) => {
        e.preventDefault();

        let dateValue = dateInput.value;
        if (dateValue) {
            // Convert 'YYYY-MM-DDTHH:MM' → 'DD-MM-YYYY HH:MM' for backend
            const [date, time] = dateValue.split('T');
            const [year, month, day] = date.split('-');
            dateValue = `${day}-${month}-${year} ${time}`;
        }

        const amount = parseFloat(document.getElementById('amount').value);
        const usage = document.getElementById('usage').value;

        if (!dateValue || isNaN(amount) || !usage.trim()) {
            alert('Please fill all fields correctly!');
            return;
        }

        try {
            const response = await fetch('/save-transaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ date2: dateValue, amount, usage }),
            });

            const result = await response.json();
            alert(result.message);

            if (response.ok) {
                // ✅ Reset form after successful submission
                document.getElementById('paisa_form').reset(); 
                toggleMode.checked = false; // ✅ Reset toggle to default (manual)
                dateInput.disabled = false; // ✅ Enable date input after reset
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to save task. Please try again.');
        }
    });
</script>
<script type='text/javascript' src='//pl26677118.profitableratecpm.com/a7/0f/34/a70f3406ef58579888372fbebaa0bcd4.js'></script>

</body>
</html>
"""

Notes_page = """
<html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Notes</title>

<style>
:root{
  --bg:#0b0b0d;
  --card:#0f1113;
  --muted:#9aa0a6;
  --accent:#ffd94d;
  --radius:14px;
}
html,body{
  margin:0;height:100%;
  background:linear-gradient(180deg,#070708,#0c0c0e);
  color:#fff;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto;
}
.app{max-width:900px;margin:20px auto;padding:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.card{background:#111;padding:14px;border-radius:12px}
.title{font-weight:600}
.muted{color:var(--muted);font-size:12px}
.fab{
  position:fixed;right:24px;bottom:24px;width:60px;height:60px;
  background:linear-gradient(180deg,#ffd94d,#ffb700);
  color:#000;font-size:30px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;cursor:pointer;
}
.editor{
  position:fixed;top:6%;left:50%;transform:translateX(-50%) translateY(-120%);
  width:92%;max-width:820px;background:#0f1113;border-radius:16px;
  padding:14px;transition:.3s;opacity:0;z-index:999;
}
.editor.open{transform:translateX(-50%) translateY(0);opacity:1}
.rte{min-height:120px;background:#0b0b0d;padding:12px;border-radius:12px}
input,button{background:#111;color:#fff;border-radius:10px;border:0;padding:8px}
.save{background:var(--accent);color:#000;font-weight:700}
</style>
</head>

<body>

<div class="app">
  <h2>Notes</h2>
  <div id="notesGrid" class="grid"></div>
</div>

<div class="fab" id="openEditor">+</div>

<div class="editor" id="editor">
  <input id="noteTitle" placeholder="Title" style="width:100%;margin-bottom:8px">
  <input id="noteTags" placeholder="tags,comma,separated" style="width:100%;margin-bottom:8px">
  <input id="noteFile" type="file" style="margin-bottom:8px">
  <div id="rte" class="rte" contenteditable="true"></div>

  <div class="muted" id="uploadStatus" style="display:none;margin-top:8px"></div>
  <div id="uploadBarWrap" style="display:none;height:6px;background:#222;border-radius:6px">
    <div id="uploadBar" style="height:100%;width:0%;background:linear-gradient(90deg,#ffd94d,#ffb700)"></div>
  </div>

  <div style="margin-top:10px;text-align:right">
    <button class="save" id="saveNoteBtn">Save</button>
    <button id="closeEditor">Cancel</button>
  </div>
</div>

<script>
let NOTES = [];
let editingId = null;

const editor = document.getElementById("editor");
const openEditorBtn = document.getElementById("openEditor");
const closeEditorBtn = document.getElementById("closeEditor");
const saveNoteBtn = document.getElementById("saveNoteBtn");
const notesGrid = document.getElementById("notesGrid");

const noteTitle = document.getElementById("noteTitle");
const noteTags = document.getElementById("noteTags");
const rte = document.getElementById("rte");

openEditorBtn.onclick = () => {
  editingId = null;
  noteTitle.value = "";
  noteTags.value = "";
  rte.innerHTML = "";
  editor.classList.add("open");
};

closeEditorBtn.onclick = () => editor.classList.remove("open");

async function fetchNotes(){
  const r = await fetch("/get_notes",{credentials:"include"});
  NOTES = await r.json();
  renderNotes();
}

function renderNotes(){
  notesGrid.innerHTML="";
  NOTES.forEach(n=>{
    const d=document.createElement("div");
    d.className="card";
    d.innerHTML=`
      <div class="title">${n.title||"Untitled"}</div>
      <div class="muted">${n.timestamp}</div>
      <div>${n.content||""}</div>
      ${n.attachment?`<a href="${n.attachment}" target="_blank">📎 File</a>`:""}
    `;
    notesGrid.appendChild(d);
  });
}

saveNoteBtn.addEventListener("click",(e)=>{
  e.preventDefault();

  const formData=new FormData();
  formData.append("title",noteTitle.value);
  formData.append("content",rte.innerHTML);
  formData.append("tags",JSON.stringify(noteTags.value.split(",").map(t=>t.trim()).filter(Boolean)));

  const file=document.getElementById("noteFile");
  if(file.files[0]) formData.append("file",file.files[0]);

  const status=document.getElementById("uploadStatus");
  const barWrap=document.getElementById("uploadBarWrap");
  const bar=document.getElementById("uploadBar");

  status.style.display="block";
  barWrap.style.display="block";
  bar.style.width="0%";
  status.textContent="Uploading…";

  let fake=0;
  const fakeTimer=setInterval(()=>{
    if(fake<90){
      fake+=3;
      bar.style.width=fake+"%";
      status.textContent=`Uploading… ${fake}%`;
    }
  },120);

  const xhr=new XMLHttpRequest();
  xhr.open("POST","/add_note",true);
  xhr.withCredentials=true;

  xhr.upload.onprogress=(e)=>{
    if(e.lengthComputable){
      clearInterval(fakeTimer);
      const p=Math.round((e.loaded/e.total)*100);
      bar.style.width=p+"%";
      status.textContent=`Uploading… ${p}%`;
    }
  };

    xhr.onload = async () => {
      try {
        const res = JSON.parse(xhr.responseText);
    
        if (res.status === "success") {
          bar.style.width = "100%";
          status.textContent = "✅ Saved";
          await fetchNotes();
          setTimeout(() => editor.classList.remove("open"), 600);
        } else {
          status.textContent = "❌ Save failed";
          bar.style.background = "#ff4b5c";
        }
      } catch (e) {
        status.textContent = "❌ Server error";
        bar.style.background = "#ff4b5c";
      }
    };


  xhr.onerror=()=>{
    clearInterval(fakeTimer);
    status.textContent="❌ Upload failed";
  };

  xhr.send(formData);
});

fetchNotes();
</script>

</body>
</html>
"""

def login_required1(func):
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("Login_page"))  
    wrapper.__name__ = func.__name__
    return wrapper

def login_required(func):
    @wraps(func) 
    def wrapper(*args, **kwargs):
        bypass_login = True  # Toggle to False when you're ready for security
        
        if bypass_login or "username" in session:
            return func(*args, **kwargs)
            
        # This will only execute if bypass_login is False AND session is empty
        return redirect(url_for("Login_page"))  

    return wrapper

@app.route("/")
def login():
    return render_template_string(Maine_page)
    #return render_template_string(Login_page)

@app.route("/dailytasks")
def dailytasks():
    return render_template_string(HTML_TEMPLATE)

@app.route("/paisa")
def paisa():
    return render_template_string(Paisa_page)

@app.route('/notes')
@login_required
def notes():
    return Notes_page



# API to Save Task
@app.route('/save_task', methods=['POST'])
def save_task():
    data = request.json
    date = data.get('date')
    tasks = data.get('tasks')

    if not date or not tasks:
        return jsonify({'message': 'Invalid input'}), 400

    # Check if the task already exists for the given date
    existing_task = task_collection.find_one({'date': date})
    if existing_task:
        task_collection.update_one({'date': date}, {'$set': {'tasks': tasks}})
        mongodb_msg = 'Task updated successfully in MongoDB'
    else:

        task_collection.insert_one({'date': date, 'tasks': tasks})
        mongodb_msg = 'Task saved successfully to MongoDB'

    sheets_data = {
        "type": "task",
        "date": date,
        "tasks": tasks
    }
    sheets_result = send_to_google_sheets(sheets_data)
    
    # Return combined result
    if sheets_result.get("status") == "success":
        return jsonify({
            'message': f'{mongodb_msg} and Google Sheets'
        })
    else:
        return jsonify({
            'message': f'{mongodb_msg}. Google Sheets error: {sheets_result.get("message", "Unknown error")}'
        })



@app.route('/save-transaction', methods=['POST'])
def save_transaction():
    data = request.json
    date2 = data.get('date2')  # Example format: '16-03-2025 14:30'
    amount = data.get('amount')
    usage = data.get('usage')

    if not date2 or amount is None or not usage:
        return jsonify({'message': 'Invalid input'}), 400

    try:
        # Validate date-time format (including hours and minutes)
        date2_obj = datetime.strptime(date2, '%d-%m-%Y %H:%M')

        # Convert to India time (GMT +5:30)
        india_timezone = pytz.timezone('Asia/Kolkata')
        date2_formatted = india_timezone.localize(date2_obj).strftime('%d-%m-%Y %H:%M')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use DD-MM-YYYY HH:MM'}), 400

    if not isinstance(amount, (int, float)):
        return jsonify({'message': 'Amount should be a numeric value'}), 400

    # ✅ Directly insert the task without checking for duplicates
    task_collection1.insert_one({
        'date2': date2_formatted,  # Save in readable format
        'amount': amount,
        'usage': usage
    })

    mongodb_msg = 'Transaction saved successfully to MongoDB'

    sheets_data = {
        "type": "transaction",
        "date2": date2_formatted,
        "amount": amount,
        "usage": usage
    }
    sheets_result = send_to_google_sheets(sheets_data)
    
    # Return combined result
    if sheets_result.get("status") == "success":
        d2_value = sheets_result.get("d2Value", "N/A")
        return jsonify({
            'message': f'{mongodb_msg} and Google Sheets. D2 Value: {d2_value}'
        }), 201
    else:
        return jsonify({
            'message': f'{mongodb_msg}. Google Sheets error: {sheets_result.get("message", "Unknown error")}'
        }), 201




def serialize_note(note):
    note["_id"] = str(note["_id"])
    return note


@app.route("/get_notes", methods=["GET"])
@login_required
def get_notes():

    india = pytz.timezone("Asia/Kolkata")
    timestamp = datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")
    notes = list(notes_collection.find().sort("timestamp", -1))

    # Convert ObjectId → string
    for n in notes:
        n["id"] = str(n["_id"])
        del n["_id"]

    return jsonify(notes)


@app.route("/add_note", methods=["POST"])
@login_required
def add_note():
    try:
        india = pytz.timezone("Asia/Kolkata")
        ts = datetime.now(india).strftime("%Y-%m-%d %H:%M")

        title = request.form.get("title", "")
        content = request.form.get("content", "")
        tags = json.loads(request.form.get("tags", "[]"))

        file_url = None

        # ---- FILE HANDLING ----
        file = request.files.get("file")
        if file and file.filename:
            file_bytes = file.read()  # READ ONCE
            encoded = base64.b64encode(file_bytes).decode("utf-8")

            post_data = {
                "title": title,
                "content": content,
                "tags": json.dumps(tags),
                "timestamp": ts,
                "filename": file.filename,
                "mimeType": file.mimetype,
                "file": encoded
            }

            r = requests.post(GOOGLE_WEBAPP_URL, data=post_data, timeout=60)

            if r.status_code != 200:
                return jsonify({"status": "error", "msg": "Google upload failed"}), 500

            result = r.json()
            if result.get("status") != "success":
                return jsonify({"status": "error", "msg": "Drive error"}), 500

            file_url = result.get("url")

        # ---- SAVE NOTE ----
        notes_collection.insert_one({
            "title": title,
            "content": content,
            "tags": tags,
            "timestamp": ts,
            "attachment": file_url
        })

        return jsonify({"status": "success"})

    except Exception as e:
        print("ADD_NOTE ERROR:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route("/edit_note", methods=["POST"])
@login_required
def edit_note():
    try:
        # Read form fields
        note_id = request.form.get("id")
        if not note_id:
            return jsonify({"status": "fail", "message": "Missing id"}), 400
        
        try:
            oid = ObjectId(str(note_id).strip())
        except:
            return jsonify({"status": "fail", "message": "Invalid ObjectId"}), 400
        
        india = pytz.timezone("Asia/Kolkata")
        update = {
            "title": request.form.get("title", ""),
            "content": request.form.get("content", ""),
            "tags": json.loads(request.form.get("tags", "[]")),
            "timestamp": datetime.now(india).strftime("%Y-%m-%d %H:%M")
        }
        
        file_url = None
        
        # Check for uploaded file
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                encoded = base64.b64encode(file.read()).decode("utf-8")
                response = requests.post(
                    GOOGLE_WEBAPP_URL,
                    data={
                        "filename": file.filename,
                        "mimeType": file.mimetype,
                        "file": encoded
                    }
                )
                result = response.json()
                if result.get("status") == "success":
                    file_url = result.get("url")
                    update["attachment"] = file_url
        
        # Save in MongoDB
        notes_collection.update_one({"_id": oid}, {"$set": update})
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"ERROR in edit_note: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/delete_note", methods=["POST"])
@login_required
def delete_note():
    data = request.json
    note_id = data.get("id")

    if not note_id:
        return jsonify({"status": "fail", "message": "Missing id"}), 400

    try:
        oid = ObjectId(str(note_id).strip())
    except:
        return jsonify({"status": "fail", "message": "Invalid ObjectId format"}), 400

    result = notes_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        return jsonify({"status": "fail", "message": "Note not found"}), 404

    return jsonify({"status": "success"})

def upload_to_drive(file):
    files = {
        'file': (file.filename, file.stream, file.mimetype)
    }
    
    resp = requests.post(GOOGLE_WEBAPP_URL, files=files)
    
    if resp.status_code == 200:
        return resp.text.strip()   # Contains Drive URL returned by Apps Script
    return None

    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("Login_page"))


if __name__ == '__main__':
    app.run(debug=True)
