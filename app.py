import sys
import os
import flask
from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from datetime import datetime
import requests
import pytz
from flask import session


app = Flask(__name__)
app.secret_key = "376757980"  # must be set for session to work

# MongoDB Atlas connection string
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set. Please set it as an environment variable.")

GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
if not GOOGLE_SCRIPT_URL:
    print("Warning: GOOGLE_SCRIPT_URL is not set. Data will only be saved to MongoDB.")


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
      return redirect (url_for(login))
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
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Notes</title>

<!-- Quill CSS -->
<link href='https://cdn.quilljs.com/1.3.6/quill.snow.css' rel='stylesheet'>

<style>
/* -------------------------------------------
   iPhone Style Dark Mode
-------------------------------------------- */
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #111;
    color: white;
    overflow-x: hidden;
}

h1 {
    text-align: center;
    padding: 20px 0;
    margin: 0;
    font-weight: 600;
    color: #f0f0f0;
}

/* Notes container */
#notesContainer {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* Card styling */
.noteCard {
    background: #1c1c1e;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #2c2c2e;
    animation: slideDown 0.3s ease;
}

.noteCard:hover {
    background: #2c2c2e;
    cursor: pointer;
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Floating add button */
#addBtn {
    position: fixed;
    bottom: 22px;
    right: 22px;
    width: 58px;
    height: 58px;
    background: #0a84ff;
    border-radius: 50%;
    box-shadow: 0 6px 15px rgba(0,0,0,0.4);
    color: white;
    font-size: 34px;
    display:flex; 
    justify-content:center; 
    align-items:center;
    cursor:pointer;
}

/* Modal */
.modal {
    display:none;
    position:fixed;
    inset:0;
    background:rgba(0,0,0,0.6);
    backdrop-filter: blur(6px);
    justify-content:center;
    align-items:center;
}

.modalContent {
    background:#1c1c1e;
    padding:20px;
    width:90%;
    max-width:420px;
    border-radius:16px;
    border:1px solid #2c2c2e;
}

input, .ql-container {
    width:100%;
    margin-top:10px;
}

button {
    background:#0a84ff;
    color:white;
    padding:10px 16px;
    border:none;
    border-radius:10px;
    margin-top:12px;
}

#deleteBtn {
    background:#ff453a;
}
</style>
</head>

<body>

<h1>Your Notes</h1>

<!-- Search -->
<div style='padding: 0 20px;'>
    <input id='searchBox' placeholder='Search...' style='width:100%; padding:12px; border-radius:12px; border:none; background:#2c2c2e; color:white;'>
</div>

<!-- Notes List -->
<div id='notesContainer'></div>

<!-- Floating add button -->
<div id='addBtn'>+</div>

<!-- Modal -->
<div id='modal' class='modal'>
  <div class='modalContent'>
      <h2 id='modalTitle'>New Note</h2>

      <input id='titleInput' placeholder='Title'>

      <!-- Quill editor -->
      <div id='editor' style='height:160px; background:white; color:black; margin-top:10px;'></div>

      <input id='tagsInput' placeholder='Tags (comma separated)'>

      <button id='saveBtn'>Save</button>
      <button id='deleteBtn' style='display:none;'>Delete</button>
      <button onclick='closeModal()' style='background:#444;'>Cancel</button>
  </div>
</div>

<!-- Quill JS -->
<script src='https://cdn.quilljs.com/1.3.6/quill.js'></script>

<script>
const API = "https://script.google.com/macros/s/AKfycbwEZizUjeRyE2YhZVNUvzmdxikEGAWmYxTC0X6ZRNmS8coUnIsXW1PT_J7aDx7UQZjJWg/exec";

let quill = new Quill('#editor', {
    theme: 'snow',
    placeholder: 'Write something...',
    modules: {
        toolbar: [
            ['bold', 'italic', 'underline'],
            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
            ['image']
        ]
    }
});

let editId = null;

/* --------------------------
   Load Notes
-------------------------- */
async function loadNotes() {
    const res = await fetch(API + '?action=get_notes');
    const notes = await res.json();

    const box = document.getElementById('notesContainer');
    box.innerHTML = '';

    notes.forEach(n => {
        let d = document.createElement('div');
        d.className = 'noteCard';
        d.innerHTML = `
            <div style='font-size:18px;font-weight:600;'>${n.title || 'Untitled'}</div>
            <div style='opacity:.7; margin-top:4px;'>${n.timestamp}</div>
        `;
        d.onclick = ()=> openModal(n);
        box.appendChild(d);
    });
}

loadNotes();

/* --------------------------
   Modal Controls
-------------------------- */
function openModal(note=null) {
    document.getElementById('modal').style.display='flex';

    if (note) {
        editId = note.id;
        document.getElementById('modalTitle').innerText = 'Edit Note';
        document.getElementById('titleInput').value = note.title;
        document.getElementById('tagsInput').value = note.tags.join(',');
        quill.root.innerHTML = note.content;
        document.getElementById('deleteBtn').style.display = 'inline-block';
    } else {
        editId = null;
        document.getElementById('modalTitle').innerText = 'New Note';
        document.getElementById('titleInput').value = '';
        document.getElementById('tagsInput').value = '';
        quill.root.innerHTML = '';
        document.getElementById('deleteBtn').style.display = 'none';
    }
}

function closeModal() {
    document.getElementById('modal').style.display='none';
}

/* --------------------------
   Add/Edit Note
-------------------------- */
document.getElementById('saveBtn').onclick = async () => {
    const title = document.getElementById('titleInput').value;
    const tags = document.getElementById('tagsInput').value.split(',').map(s=>s.trim());
    const content = quill.root.innerHTML;

    const payload = {
        title, content, tags
    };

    let action = 'add_note';

    if (editId) {
        payload.id = editId;
        action = 'edit_note';
    }

    await fetch(API + '?action=' + action, {
        method:'POST',
        body: JSON.stringify(payload)
    });

    closeModal();
    loadNotes();
};

/* --------------------------
   Delete Note
-------------------------- */
document.getElementById('deleteBtn').onclick = async () => {
    if (!confirm('Delete this note?')) return;

    await fetch(API + '?action=delete_note', {
        method:'POST',
        body: JSON.stringify({ id: editId })
    });

    closeModal();
    loadNotes();
};

/* --------------------------
   Search Filter
-------------------------- */
document.getElementById('searchBox').oninput = () => {
    let q = document.getElementById('searchBox').value.toLowerCase();
    document.querySelectorAll('.noteCard').forEach(card=>{
        card.style.display = card.innerText.toLowerCase().includes(q) ? 'block' : 'none';
    });
};

document.getElementById('addBtn').onclick = () => openModal();

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


@app.route("/get_notes", methods=["GET"])
@login_required
def get_notes():
    notes = []
    for n in notes_collection.find().sort("timestamp", -1):
        notes.append({
            "id": str(n["_id"]),
            "title": n.get("title", ""),
            "content": n.get("content", ""),
            "tags": n.get("tags", []),
            "timestamp": n.get("timestamp", "")
        })
    return jsonify(notes)


@app.route("/add_note", methods=["POST"])
@login_required
def add_note():
    data = request.json
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()   # HTML from contenteditable
    tags = data.get("tags", [])                 # list of strings

    if not content and not title:
        return jsonify({"status": "fail", "message": "Note is empty"}), 400

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notes_collection.insert_one({
        "title": title,
        "content": content,
        "tags": tags,
        "timestamp": ts
    })
    return jsonify({"status": "success"})


@app.route("/edit_note", methods=["POST"])
@login_required
def edit_note():
    data = request.json
    note_id = data.get("id")
    if not note_id:
        return jsonify({"status": "fail", "message": "Missing id"}), 400

    update = {}
    if "title" in data:
        update["title"] = data.get("title", "")
    if "content" in data:
        update["content"] = data.get("content", "")
    if "tags" in data:
        update["tags"] = data.get("tags", [])

    update["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": update})
    return jsonify({"status": "success"})


@app.route("/delete_note", methods=["POST"])
@login_required
def delete_note():
    data = request.json
    note_id = data.get("id")
    if not note_id:
        return jsonify({"status": "fail", "message": "Missing id"}), 400
    notes_collection.delete_one({"_id": ObjectId(note_id)})
    return jsonify({"status": "success"})
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("Login_page"))


if __name__ == '__main__':
    app.run(debug=True)

