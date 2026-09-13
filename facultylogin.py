from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# 🔑 CHANGE THESE CREDENTIALS ANYTIME
VALID_USERS = {
    "teacher.sanchez@school.edu.ph": "Education2026!",
    "teacher.delaCruz@school.edu.ph": "ClassRecord#123"
}

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teacher Portal | School Login</title>
    <style>
        * {margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI', Roboto, sans-serif;}
        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            display: flex; align-items: center; justify-content: center; padding: 20px;
        }
        .portal-card {
            background: rgba(255,255,255,0.97);
            border-radius: 20px; padding: 2.5rem; width: 100%; max-width: 440px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.35);
            border-top: 5px solid #10b981;
        }
        .icon {text-align: center; font-size: 3rem; margin-bottom: 0.5rem;}
        h2 {text-align: center; color: #0f172a; font-weight: 700; margin-bottom: 0.3rem;}
        .tagline {text-align: center; color: #64748b; margin-bottom: 2rem; font-size: 0.95rem;}
        .form-group {margin-bottom: 1.3rem;}
        label {display: block; margin-bottom: 0.5rem; color: #334155; font-weight: 500; font-size: 0.9rem;}
        input {
            width: 100%; padding: 0.95rem 1rem; border: 2px solid #cbd5e1;
            border-radius: 10px; font-size: 1rem; transition: all 0.3s ease;
        }
        input:focus {outline: none; border-color: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.2);}
        .btn-login {
            width: 100%; padding: 0.95rem; background: linear-gradient(90deg, #0f172a, #1e293b);
            color: white; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600;
            cursor: pointer; transition: transform 0.2s; margin-top: 0.5rem;
        }
        .btn-login:hover {transform: translateY(-2px);}
        .error {
            margin-top: 1rem; padding: 0.8rem; background: #fef2f2; color: #dc2626;
            border-radius: 8px; text-align: center; display: none;
        }
        .footer {margin-top: 1.5rem; text-align: center; font-size: 0.85rem; color: #94a3b8;}
    </style>
</head>
<body>
    <div class="portal-card">
        <div class="icon">📚</div>
        <h2>Teacher Access Portal</h2>
        <p class="tagline">Official School Faculty Login System</p>

        <form method="POST">
            <div class="form-group">
                <label>📧 Official Email</label>
                <input type="email" name="email" placeholder="name@school.edu.ph" required>
            </div>
            <div class="form-group">
                <label>🔒 Password</label>
                <input type="password" name="password" placeholder="Enter your password" required>
            </div>
            <button class="btn-login" type="submit">SIGN IN TO PORTAL</button>
            {% if error %}
            <div class="error" style="display:block;">⚠️ {{ error }}</div>
            {% endif %}
        </form>
        <p class="footer">© 2026 School Faculty System • Authorized Access Only</p>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | Teacher Portal</title>
    <style>
        * {margin:0; padding:0; font-family:'Segoe UI', sans-serif;}
        body {background: #f8fafc; min-height: 100vh;}
        .header {background: linear-gradient(90deg, #0f172a, #1e293b); color: white; padding: 1.5rem 2rem; display: flex; justify-content: space-between; align-items: center;}
        .header h1 {font-size: 1.4rem;}
        .user-badge {background: #10b981; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;}
        .container {max-width: 1000px; margin: 2rem auto; padding: 0 1.5rem;}
        .welcome {background: white; padding: 2rem; border-radius: 14px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border-left: 4px solid #10b981;}
        .grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.2rem;}
        .card {background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); transition: transform 0.2s;}
        .card:hover {transform: translateY(-5px);}
        .card h3 {color: #0f172a; margin-bottom: 0.5rem;}
        .card p {color: #64748b; font-size: 0.9rem;}
        .logout {background: #ef4444; color: white; border: none; padding: 0.7rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: 600;}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏫 Teacher Portal Dashboard</h1>
        <div>
            <span class="user-badge">{{ email }}</span>
            <button class="logout" onclick="window.location.href='/logout'" style="margin-left:1rem;">Log Out</button>
        </div>
    </div>
    <div class="container">
        <div class="welcome">
            <h2>Welcome back! 🎉</h2>
            <p style="margin-top:0.5rem; color:#475569;">You are successfully logged in to the school faculty system.</p>
        </div>
        <div class="grid">
            <div class="card">
                <h3>📖 Class Records</h3>
                <p>Manage subjects, sections & student lists</p>
            </div>
            <div class="card">
                <h3>✅ Attendance</h3>
                <p>Mark & view daily attendance sheets</p>
            </div>
            <div class="card">
                <h3>📊 Grading Sheet</h3>
                <p>Encode, edit & submit grades</p>
            </div>
            <div class="card">
                <h3>📋 Reports</h3>
                <p>Generate forms & summary reports</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if email in VALID_USERS and VALID_USERS[email] == password:
            return redirect(url_for('dashboard', user=email))
        return LOGIN_PAGE.replace("{% if error %}", "").replace("{{ error }}", "Email or password is incorrect").replace("{% endif %}", "")
    return LOGIN_PAGE

@app.route('/dashboard')
def dashboard():
    user = request.args.get('user', '')
    if user not in VALID_USERS:
        return redirect(url_for('login'))
    return DASHBOARD_PAGE.replace("{{ email }}", user)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("✅ Teacher Portal Running → http://127.0.0.1:5000")
    app.run(debug=True)
