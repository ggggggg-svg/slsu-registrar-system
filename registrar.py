from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slsu-tagkawayan-registrar-2026'

# In-memory storage (replace with database in production)
appointments = []

# ========== HTML TEMPLATE ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrar Appointment | SLSU JGE Tagkawayan College</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --slsu-green: #006937; --slsu-gold: #f5b82e; --slsu-dark: #0f2e20;
            --slsu-light: #f0f7f2; --neutral-600: #4a6358; --neutral-800: #1e3329;
            --shadow-md: 0 4px 12px rgba(0,0,0,0.1); --radius: 12px; --transition: all 0.3s ease;
        }
        * {margin:0; padding:0; box-sizing:border-box; font-family:'Inter',sans-serif;}
        html {scroll-behavior:smooth;}
        body {background:linear-gradient(135deg,var(--slsu-light) 0%,#fff 100%); color:var(--neutral-800); line-height:1.6;}
        
        header {background:#fff; box-shadow:0 1px 3px rgba(0,0,0,0.08); position:sticky; top:0; z-index:100;}
        .hdr {max-width:1200px; margin:0 auto; padding:1rem 1.5rem; display:flex; align-items:center; justify-content:space-between;}
        .brand {display:flex; align-items:center; gap:.8rem;}
        .brand-logo {width:50px; height:50px; border-radius:50%; background:var(--slsu-green); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.3rem;}
        .brand-text h1 {font-size:1rem; color:var(--slsu-green);}
        .brand-text p {font-size:.75rem; color:var(--neutral-600);}
        nav a {margin-left:1.5rem; font-weight:500; color:var(--neutral-600); text-decoration:none;}
        nav a:hover, nav a.active {color:var(--slsu-green);}
        nav .book-btn {background:var(--slsu-green); color:#fff; padding:.6rem 1.2rem; border-radius:8px;}
        nav .book-btn:hover {background:#00552d;}

        .hero {max-width:1200px; margin:0 auto; padding:4rem 1.5rem; display:grid; grid-template-columns:1fr 1fr; gap:3rem; align-items:center;}
        .hero h2 {font-size:2.5rem; line-height:1.2; margin-bottom:1.5rem;}
        .hero h2 span {color:var(--slsu-green);}
        .hero p {font-size:1.1rem; color:var(--neutral-600); margin-bottom:2rem;}
        .btn-primary {background:var(--slsu-green); color:#fff; padding:.9rem 2rem; border-radius:var(--radius); border:none; font-size:1rem; font-weight:600; cursor:pointer; transition:var(--transition);}
        .btn-primary:hover {background:#00552d; transform:translateY(-2px);}
        .btn-secondary {background:#fff; color:var(--slsu-green); padding:.9rem 2rem; border-radius:var(--radius); border:2px solid var(--slsu-green); font-weight:600; cursor:pointer;}
        .hero-card {background:linear-gradient(135deg,var(--slsu-green),#008045); color:#fff; padding:3rem; border-radius:24px; text-align:center;}
        .hero-card .time {font-size:3rem; font-weight:700; margin:1rem 0;}

        section {max-width:1000px; margin:0 auto; padding:4rem 1.5rem;}
        .sec-head {text-align:center; margin-bottom:3rem;}
        .sec-head h3 {font-size:1.8rem; color:var(--slsu-dark); margin-bottom:.5rem;}
        .services {display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:1.5rem;}
        .svc-card {background:#fff; padding:2rem; border-radius:var(--radius); border-left:4px solid var(--slsu-gold); transition:var(--transition);}
        .svc-card:hover {transform:translateY(-5px); box-shadow:var(--shadow-md);}
        .svc-card h4 {color:var(--slsu-green); margin-bottom:.5rem;}
        .svc-card p {color:var(--neutral-600); font-size:.9rem;}

        form {background:#fff; padding:2.5rem; border-radius:20px; box-shadow:var(--shadow-md);}
        .form-grid {display:grid; grid-template-columns:1fr 1fr; gap:1.2rem;}
        .full {grid-column:1/-1;}
        label {display:block; font-weight:600; font-size:.9rem; margin-bottom:.4rem;}
        input,select,textarea {width:100%; padding:.9rem 1rem; border:2px solid #e2eae5; border-radius:8px; font-size:.95rem;}
        input:focus,select:focus,textarea:focus {outline:none; border-color:var(--slsu-green);}
        .note {margin-top:1rem; font-size:.8rem; color:var(--neutral-600);}
        .submit-btn {width:100%; margin-top:1rem;}

        .modal {position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:200; opacity:0; visibility:hidden; transition:var(--transition);}
        .modal.show {opacity:1; visibility:visible;}
        .modal-box {background:#fff; padding:2.5rem; border-radius:16px; max-width:420px; text-align:center; transform:translateY(20px); transition:var(--transition);}
        .modal.show .modal-box {transform:translateY(0);}
        .ref {background:var(--slsu-light); padding:.8rem; border-radius:8px; font-family:monospace; font-weight:700; color:var(--slsu-green); margin:1rem 0;}
        .err-msg {color:#dc2626; margin-top:.5rem; display:none;}

        footer {background:var(--slsu-dark); color:#fff; padding:3rem 1.5rem; margin-top:3rem;}
        .ftr {max-width:1000px; margin:0 auto;}
        .ftr-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:2rem;}
        .ftr h5 {color:var(--slsu-gold); margin-bottom:1rem;}
        .ftr p {color:#b8c7be; font-size:.85rem; line-height:1.8;}
        .ftr-bot {margin-top:2rem; padding-top:2rem; border-top:1px solid rgba(255,255,255,.1); text-align:center; font-size:.8rem; color:#7a9486;}

        @media(max-width:768px) {
            .hero {grid-template-columns:1fr;}
            .form-grid {grid-template-columns:1fr;}
            nav {display:none;}
        }
    </style>
</head>
<body>
    <header>
        <div class="hdr">
            <a href="/" class="brand" style="text-decoration:none;">
                <div class="brand-logo">S</div>
                <div class="brand-text">
                    <h1>SLSU · JGE Tagkawayan</h1>
                    <p>Office of the Registrar</p>
                </div>
            </a>
            <nav>
                <a href="#home" class="active">Home</a>
                <a href="#services">Services</a>
                <a href="#appointment" class="book-btn">📅 Book Now</a>
                <a href="#contact">Contact</a>
            </nav>
        </div>
    </header>

    <section class="hero" id="home">
        <div>
            <h2>Official <span>Online Appointment</span> System</h2>
            <p>Schedule your visit to the Registrar’s Office easily and securely. Reduce wait time — from SLSU JGE Tagkawayan College.</p>
            <a href="#appointment"><button class="btn-primary">📅 Make Appointment</button></a>
        </div>
        <div class="hero-card">
            <h3>Office Hours</h3>
            <div class="time">8:00 AM – 5:00 PM</div>
            <p>Monday – Friday</p>
            <p style="margin-top:1rem; opacity:.8;">No appointment needed for releasing documents</p>
        </div>
    </section>

    <section id="services">
        <div class="sec-head">
            <h3>📋 Our Services</h3>
            <p>Select the type of assistance you need</p>
        </div>
        <div class="services">
            <div class="svc-card">
                <h4>📄 Document Requests</h4>
                <p>Transcript, Diploma, Certification & more</p>
            </div>
            <div class="svc-card">
                <h4>✅ Enrollment Matters</h4>
                <p>Add/drop subjects, cross-enrollment</p>
            </div>
            <div class="svc-card">
                <h4>📊 Academic Records</h4>
                <p>Grade verification, record correction</p>
            </div>
            <div class="svc-card">
                <h4>🎓 Graduation</h4>
                <p>Application & clearance processing</p>
            </div>
        </div>
    </section>

    <section id="appointment">
        <div class="sec-head">
            <h3>📅 Submit Appointment</h3>
            <p>Fill all required fields — we'll confirm your schedule</p>
        </div>
        <form id="aptForm">
            <div class="form-grid">
                <div>
                    <label>Full Name *</label>
                    <input type="text" name="fullname" placeholder="Last, First Middle" required>
                </div>
                <div>
                    <label>Student ID *</label>
                    <input type="text" name="studentId" placeholder="2023-00123-TG" required>
                </div>
                <div>
                    <label>Email *</label>
                    <input type="email" name="email" placeholder="your.email@slsu.edu.ph" required>
                </div>
                <div>
                    <label>Contact No. *</label>
                    <input type="tel" name="contact" placeholder="09XX-XXX-XXXX" required>
                </div>
                <div>
                    <label>Course/Program *</label>
                    <select name="course" required>
                        <option value="">Select Course</option>
                        <option>BSIT</option><option>BSED</option><option>BEED</option>
                        <option>BSBA</option><option>BS Criminology</option><option>Other</option>
                    </select>
                </div>
                <div>
                    <label>Purpose *</label>
                    <select name="purpose" required>
                        <option value="">Select Purpose</option>
                        <option>Document Request</option>
                        <option>Enrollment Concern</option>
                        <option>Academic Records</option>
                        <option>Graduation Clearance</option>
                        <option>Other</option>
                    </select>
                </div>
                <div>
                    <label>Date *</label>
                    <input type="date" name="aptDate" id="minDate" required>
                </div>
                <div>
                    <label>Time Slot *</label>
                    <select name="aptTime" required>
                        <option value="">Select Time</option>
                        <option>09:00 AM – 10:00 AM</option>
                        <option>10:00 AM – 11:00 AM</option>
                        <option>01:00 PM – 02:00 PM</option>
                        <option>02:00 PM – 03:00 PM</option>
                        <option>03:00 PM – 04:00 PM</option>
                    </select>
                </div>
                <div class="full">
                    <label>Remarks</label>
                    <textarea name="remarks" rows="3" placeholder="Details, specific documents needed..."></textarea>
                </div>
            </div>
            <p class="note">⚠️ Please arrive 10–15 mins early. Bring valid ID & requirements.</p>
            <p class="err-msg" id="formErr">Something went wrong. Try again.</p>
            <button type="submit" class="btn-primary submit-btn">✅ Submit Appointment</button>
        </form>
    </section>

    <div class="modal" id="successModal">
        <div class="modal-box">
            <div style="font-size:3rem;">✅</div>
            <h3 style="color:var(--slsu-green); margin:1rem 0;">Appointment Recorded!</h3>
            <p>Your Reference Number:</p>
            <div class="ref" id="refDisplay"></div>
            <p style="font-size:.9rem; color:var(--neutral-600); margin-bottom:1.5rem;">We'll send confirmation via email.</p>
            <button class="btn-primary" onclick="closeModal()">Got it</button>
        </div>
    </div>

    <footer id="contact">
        <div class="ftr">
            <div class="ftr-grid">
                <div>
                    <h5>📍 Location</h5>
                    <p>SLSU JGE Tagkawayan College<br>Tagkawayan, Quezon</p>
                </div>
                <div>
                    <h5>📞 Contact</h5>
                    <p>registrar.tagkawayan@slsu.edu.ph<br>(042) XXX-XXXX</p>
                </div>
                <div>
                    <h5>🕐 Hours</h5>
                    <p>Mon–Fri<br>8:00 AM – 5:00 PM</p>
                </div>
            </div>
            <div class="ftr-bot">
                <p>© 2026 SLSU JGE Tagkawayan — Office of the Registrar. All Rights Reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        // Min date = today
        document.getElementById('minDate').min = new Date().toISOString().split('T')[0];

        // Submit via Python backend
        document.getElementById('aptForm').addEventListener('submit', async e => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const res = await fetch('/book', {
                method: 'POST',
                body: formData
            });
            
            const data = await res.json();
            
            if (data.success) {
                document.getElementById('refDisplay').textContent = data.ref_num;
                document.getElementById('successModal').classList.add('show');
                e.target.reset();
            } else {
                document.getElementById('formErr').style.display = 'block';
            }
        });

        function closeModal() {
            document.getElementById('successModal').classList.remove('show');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/book', methods=['POST'])
def book():
    try:
        data = request.form
        
        # Generate unique reference number
        today = datetime.now()
        date_str = today.strftime('%y%m%d')
        unique_id = str(uuid.uuid4())[:5].upper()
        ref_num = f"SLSU-TG-{date_str}-{unique_id}"
        
        # Save appointment
        appointment = {
            "ref_num": ref_num,
            "fullname": data.get('fullname'),
            "student_id": data.get('studentId'),
            "email": data.get('email'),
            "contact": data.get('contact'),
            "course": data.get('course'),
            "purpose": data.get('purpose'),
            "apt_date": data.get('aptDate'),
            "apt_time": data.get('aptTime'),
            "remarks": data.get('remarks', ''),
            "submitted_at": today.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        appointments.append(appointment)
        
        # Console log — you can view all appointments here
        print(f"\n📝 NEW APPOINTMENT: {ref_num}")
        for k, v in appointment.items():
            print(f"   {k}: {v}")
        print(f"   Total appointments: {len(appointments)}")
        
        return jsonify({"success": True, "ref_num": ref_num})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"success": False}), 400

@app.route('/admin/appointments')
def admin_list():
    """View all appointments — simple admin page"""
    if not appointments:
        return "<h1>No appointments yet</h1><p>Return to <a href='/'>Home</a></p>"
    
    html = "<h1>📋 All Appointments</h1><table border='1' cellpadding='8' style='border-collapse:collapse; width:100%;'>"
    html += "<tr style='background:#006937; color:white;'><th>Reference</th><th>Name</th><th>Student ID</th><th>Date</th><th>Time</th><th>Purpose</th></tr>"
    
    for apt in appointments:
        html += f"""<tr>
            <td><strong>{apt['ref_num']}</strong></td>
            <td>{apt['fullname']}</td>
            <td>{apt['student_id']}</td>
            <td>{apt['apt_date']}</td>
            <td>{apt['apt_time']}</td>
            <td>{apt['purpose']}</td>
        </tr>"""
    
    html += "</table><br><a href='/'>← Back to Home</a>"
    return html

if __name__ == '__main__':
    print("="*50)
    print("🎓 SLSU JGE Tagkawayan — Registrar Appointment System")
    print("✅ Server running at: http://127.0.0.1:5000")
    print("📋 Admin panel: http://127.0.0.1:5000/admin/appointments")
    print("="*50)
    app.run(debug=True)
