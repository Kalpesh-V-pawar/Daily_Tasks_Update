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
  <title>Notes — Dark iOS Style</title>
  <style>
    :root{
      --bg:#0b0b0d;
      --card:#0f1113;
      --muted:#9aa0a6;
      --accent:#ffd94d; /* warm gold highlight */
      --glass: rgba(255,255,255,0.03);
      --soft: rgba(255,255,255,0.02);
      --radius: 14px;
      --shadow: 0 6px 18px rgba(0,0,0,0.6);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }

    html,body{height:100%;margin:0;background:linear-gradient(180deg,#070708, #0c0c0e);color:#fff;}
    .app {max-width:940px;margin:28px auto;padding:18px;}
    header {display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
    h1{font-size:20px;margin:0;color:#fff}
    .sub {color:var(--muted);font-size:13px}

    /* Search / controls */
    .controls {display:flex;gap:12px;align-items:center}
    .search {
      display:flex;align-items:center;background:var(--glass);padding:10px 12px;border-radius:12px;backdrop-filter: blur(6px);
      box-shadow: var(--shadow); border:1px solid rgba(255,255,255,0.02);
    }
    .search input{background:transparent;border:0;outline:none;color:#fff;width:220px}

    .filters {display:flex;gap:8px;align-items:center}
    .select, .input {background:var(--soft);padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,0.02);color:#fff}
    .select select, .input input{background:transparent;border:0;color:#fff;outline:none}

    /* notes grid */
    .grid {display:grid;grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap:14px;margin-top:16px}
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius:12px;padding:14px;box-shadow: var(--shadow);border:1px solid rgba(255,255,255,0.03);
      transform-origin: top center;overflow:hidden;
    }
    .title {font-weight:600;color: #fff;font-size:16px;margin-bottom:6px}
    .time {font-size:12px;color:var(--muted);margin-bottom:8px}
    .content {color:#e6e6e6;font-size:14px;margin-bottom:10px;max-height:140px;overflow:auto}
    .tags {display:flex;gap:6px;flex-wrap:wrap}
    .tag {font-size:12px;padding:6px 8px;border-radius:999px;background:rgba(255,255,255,0.03);color:var(--muted)}

    .card-actions{display:flex;gap:8px;justify-content:flex-end}
    .btn {border:0;padding:8px 10px;border-radius:10px;cursor:pointer;font-weight:600}
    .btn-edit{background:#2baf7a;color:#fff}
    .btn-delete{background:#ff4b5c;color:#fff}

    /* floating + */
    .fab {
      position:fixed;right:24px;bottom:28px;width:62px;height:62px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#ffd94d,#ffb700);
      color:#111;font-size:32px;box-shadow: 0 10px 30px rgba(0,0,0,0.6);cursor:pointer;border:4px solid rgba(255,255,255,0.06);
    }

    /* editor modal (slide-down) */
    .editor {
      position:fixed;left:50%;transform:translateX(-50%) translateY(-120%);top:8%;width:92%;max-width:820px;background:var(--card);border-radius:16px;padding:14px;box-shadow:0 18px 50px rgba(0,0,0,0.7);
      transition: transform 300ms cubic-bezier(.2,.9,.2,1), opacity 220ms;opacity:0;z-index:999;
      border:1px solid rgba(255,255,255,0.03);
    }
    .editor.open { transform:translateX(-50%) translateY(0); opacity:1;}

    .editor .toolbar {display:flex;gap:8px;align-items:center;margin-bottom:8px}
    .toolbar button{background:transparent;border:0;color:var(--muted);padding:8px;border-radius:8px;cursor:pointer}
    .toolbar button.active{color:var(--accent);background:rgba(255,217,77,0.06)}

    .editor .fields{display:flex;gap:12px}
    .editor input.title{flex:1;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,0.03);background:transparent;color:#fff}
    .editor .tags-input{width:220px;padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,0.03);background:transparent;color:#fff}

    .editor .rte {
      margin-top:10px;border-radius:12px;padding:12px;min-height:120px;background:linear-gradient(180deg,#0b0b0d,#101215); color:#fff;outline:none;border:1px solid rgba(255,255,255,0.02)
    }

    .editor .footer{display:flex;justify-content:space-between;align-items:center;margin-top:12px}
    .editor .save{background:var(--accent);padding:10px 14px;border-radius:10px;border:0;font-weight:700;cursor:pointer}

    /* small helpers */
    .muted{color:var(--muted);font-size:13px}
    @media (max-width:480px){
      .search input{width:120px}
      .editor{top:6%}
    }
  </style>
</head>
<body>
  <div class="app">
    <header>
      <div>
        <h1>Notes</h1>
        <div class="sub muted">iOS Dark • Your private notes</div>
      </div>

      <div class="controls">
        <div class="search">
          🔍 &nbsp;<input id="searchInput" placeholder="Search notes, tags..." />
        </div>

        <div class="select">
          <select id="tagFilter">
            <option value="">All tags</option>
          </select>
        </div>

        <div class="input">
          <input id="dateFilter" type="date" />
        </div>
      </div>
    </header>

    <main>
      <div id="notesGrid" class="grid"></div>
    </main>
  </div>

  <!-- floating add -->
  <div class="fab" id="openEditor">+</div>

  <!-- Editor modal -->
  <div class="editor" id="editor">
    <div class="toolbar">
      <button id="boldBtn"><b>B</b></button>
      <button id="italicBtn"><i>I</i></button>
      <button id="underlineBtn"><u>U</u></button>
      <button id="bulletBtn">• List</button>
      <button id="linkBtn">🔗</button>
      <div class="muted" style="margin-left:8px">Formatting</div>
    </div>

    <div class="fields">
      <input id="noteTitle" class="title" placeholder="Title (optional)" />
      <input id="noteTags" class="tags-input" placeholder="tags comma-separated" />
    </div>
    
    <div style="margin-top:12px">
      <label class="muted">Attachment:</label>
      <input id="noteFile" type="file" style="margin-left:8px;color:var(--muted)" />
    </div>

    <div id="rte" class="rte" contenteditable="true" placeholder="Start writing..."></div>

    <div class="footer">
      <div class="muted" id="charCount">0 chars</div>
      <div>
        <button class="save" id="saveNoteBtn">Save</button>
        <button class="btn" id="closeEditor" style="margin-left:8px;background:transparent;color:var(--muted)">Cancel</button>
      </div>
    </div>
  </div>

<script>
  // state
  let NOTES = [];     // fetched notes
  let editingId = null;

  // elements
  const editor = document.getElementById('editor');
  const openEditorBtn = document.getElementById('openEditor');
  const closeEditorBtn = document.getElementById('closeEditor');
  const saveNoteBtn = document.getElementById('saveNoteBtn');
  const notesGrid = document.getElementById('notesGrid');
  const searchInput = document.getElementById('searchInput');
  const tagFilter = document.getElementById('tagFilter');
  const dateFilter = document.getElementById('dateFilter');
  const noteTitle = document.getElementById('noteTitle');
  const noteTags = document.getElementById('noteTags');
  const rte = document.getElementById('rte');
  const charCount = document.getElementById('charCount');

  // toolbar
  document.getElementById('boldBtn').addEventListener('click', ()=> document.execCommand('bold'));
  document.getElementById('italicBtn').addEventListener('click', ()=> document.execCommand('italic'));
  document.getElementById('underlineBtn').addEventListener('click', ()=> document.execCommand('underline'));
  document.getElementById('bulletBtn').addEventListener('click', ()=> document.execCommand('insertUnorderedList'));
  document.getElementById('linkBtn').addEventListener('click', ()=>{
    const url = prompt("Enter URL (include https://)");
    if (url) document.execCommand('createLink', false, url);
  });

  // editor open/close
  openEditorBtn.addEventListener('click', ()=>{
    editingId = null;
    noteTitle.value = '';
    noteTags.value = '';
    rte.innerHTML = '';
    document.getElementById('noteFile').value = '';
    editor.classList.add('open');
    setTimeout(()=> rte.focus(), 220);
  });
  closeEditorBtn.addEventListener('click', ()=> editor.classList.remove('open'));

  // char count
  rte.addEventListener('input', ()=> charCount.textContent = rte.innerText.length + " chars");

  // load notes from server
  async function fetchNotes(){
    const res = await fetch('/get_notes');
    NOTES = await res.json();
    populateTagFilter();
    renderNotes();
  }

  // populate tag filter options
  function populateTagFilter(){
    const allTags = new Set();
    NOTES.forEach(n => (n.tags||[]).forEach(t => allTags.add(t)));
    tagFilter.innerHTML = '<option value="">All tags</option>';
    Array.from(allTags).sort().forEach(t => {
      const opt = document.createElement('option'); opt.value = t; opt.textContent = t; tagFilter.appendChild(opt);
    });
  }

  // render notes with search & filters (animated)
  function renderNotes(){
    const q = (searchInput.value||'').toLowerCase();
    const selectedTag = tagFilter.value;
    const dateVal = dateFilter.value; // YYYY-MM-DD

    notesGrid.innerHTML = '';

    const filtered = NOTES.filter(n => {
      if (selectedTag && !(n.tags||[]).includes(selectedTag)) return false;
      if (dateVal && !n.timestamp.startsWith(dateVal)) {
         // timestamp format 'YYYY-MM-DD HH:MM:SS' so startsWith works
         return false;
      }
      if (!q) return true;
      // search title, content (strip html), tags
      const text = (n.title + ' ' + (n.content.replace(/<[^>]*>?/gm, '') || '') + ' ' + (n.tags||[]).join(' ')).toLowerCase();
      return text.includes(q);
    });

    filtered.forEach(n => {
      const div = document.createElement('div');
      div.className = 'card';
      div.style.animation = 'slideDown .28s ease';
      div.innerHTML = `
        <div class="title">${escapeHtml(n.title || 'Untitled')}</div>
        <div class="time">${n.timestamp}</div>
        <div class="content">${n.content || ''}</div>
      
        ${n.attachment ? `<div style="margin-top:8px"><a href="${n.attachment}" target="_blank" style="color:var(--accent);text-decoration:none">📎 Attachment</a></div>` : ''}
      
        <div class="tags">
          ${(n.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
        </div>
      
        <div class="card-actions" style="margin-top:10px">
          <button class="btn btn-edit" onclick='openEdit("${n.id}")'>Edit</button>
          <button class="btn btn-delete" onclick='deleteNote("${n.id}")'>Delete</button>
        </div>
      `;
      notesGrid.appendChild(div);
    });

    // tiny animation keyframes inserted once:
    if (!document.getElementById('notes-anim')) {
      const s = document.createElement('style'); s.id='notes-anim';
      s.innerHTML = '@keyframes slideDown{from{opacity:0; transform:translateY(-8px)} to{opacity:1; transform:translateY(0)}}';
      document.head.appendChild(s);
    }
  }

  // helpers
  function escapeHtml(s){ return (s||'').replace(/[&<>"']/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' })[c]); }

  // open edit modal prefilled
  function openEdit(id){
    const n = NOTES.find(x=>x.id===id);
    if(!n) return;
    editingId = id;
    noteTitle.value = n.title || '';
    noteTags.value = (n.tags||[]).join(', ');
    rte.innerHTML = n.content || '';
    editor.classList.add('open');
    setTimeout(()=> rte.focus(), 220);
  }

  // add / save note
    saveNoteBtn.addEventListener("click", async () => {
      const title = noteTitle.value.trim();
      const content = rte.innerHTML.trim();
      const rawTags = noteTags.value.split(",").map(t => t.trim()).filter(t => t);
      const fileInput = document.getElementById("noteFile");
      
    
      const formData = new FormData();
      formData.append("title", title);
      formData.append("content", content);
      formData.append("tags", JSON.stringify(rawTags));

      if (fileInput && fileInput.files[0]) {
         formData.append("file", fileInput.files[0]);
      }
    
      if (editingId) {
        formData.append("id", editingId);
    
        await fetch("/edit_note", {
          method: "POST",
          credentials: "include",
          body: formData
        });
    
      } else {
        await fetch("/add_note", {
          method: "POST",
          credentials: "include",
          body: formData
        });
      }
    
      editor.classList.remove("open");
      await fetchNotes();
    });


  // delete
  async function deleteNote(id){
    if(!confirm('Delete this note?')) return;
    await fetch('/delete_note', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      credentials: "include",
      body: JSON.stringify({ id })
    });
    await fetchNotes();
  }

  // search & filters events
  searchInput.addEventListener('input', ()=> renderNotes());
  tagFilter.addEventListener('change', ()=> renderNotes());
  dateFilter.addEventListener('change', ()=> renderNotes());

  // init
  fetchNotes();
</script>
</body>
</html>
"""

def login_required(func):
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("Login_page"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
def login():
    return render_template_string(Maine_page)

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
        
        # Read fields
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        tags = json.loads(request.form.get("tags", "[]"))
        
        file_url = None
        
        # Check if file exists and has content
        if "file" in request.files:
            file = request.files["file"]
            if file and file.filename:
                encoded = base64.b64encode(file.read()).decode("utf-8")
                # Prepare data to send
                file_obj = None
                if "file" in request.files:
                    file_obj = request.files["file"]
                
                post_data = {
                    "title": title,
                    "content": content,
                    "tags": json.dumps(tags),
                    "timestamp": ts
                }
                
                # Add file data if present
                if file_obj and file_obj.filename:
                    post_data["filename"] = file_obj.filename
                    post_data["mimeType"] = file_obj.mimetype
                    post_data["file"] = encoded
                
                print(f"Sending to Google: {post_data.keys()}")  # Debug log
                
                # Send to Google Apps Script
                response = requests.post(GOOGLE_WEBAPP_URL, data=post_data)
                
                print(f"Google response: {response.text}")  # Debug log
                
                result = response.json()
                if result.get("status") == "success":
                    file_url = result.get("url")
        
        notes_collection.insert_one({
            "title": title,
            "content": content,
            "tags": tags,
            "timestamp": ts,
            "attachment": file_url
        })
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"ERROR in add_note: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


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

