from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slsu-jge-tagkawayan-2026'

appointments = []

# ========== SHARED LAYOUT ==========
SHARED_HEAD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {margin:0; padding:0; box-sizing:border-box; font-family:'Inter', sans-serif;}
        body {min-height:100vh; overflow-x:hidden;}

        .bg-layer {
            position:fixed; inset:0; z-index:-2;
            background: url('building.jpg') no-repeat center center;
            background-size:cover;
        }
        .bg-overlay {
            position:fixed; inset:0; z-index:-1;
            background:rgba(0,35,15,0.65);
        }

        nav {
            background:rgba(255,255,255,0.95);
            padding:1rem 2rem;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
            position:sticky; top:0; z-index:100;
        }
        .nav-container {
            max-width:1200px; margin:0 auto;
            display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;
        }
        .logo-group {display:flex; align-items:center; gap:1rem;}
        .logo-slot {width:55px; height:55px; border-radius:50%; overflow:hidden; background:#fff;}
        .logo-slot img {width:100%; height:100%; object-fit:contain;}
        .brand-name {line-height:1.2;}
        .brand-name h1 {font-size:1rem; color:#006937; font-weight:700;}
        .brand-name p {font-size:0.75rem; color:#555;}
        .nav-links {display:flex; gap:0.5rem; flex-wrap:wrap;}
        .nav-link {
            padding:0.7rem 1.2rem; border-radius:8px; text-decoration:none;
            font-weight:600; font-size:0.9rem;
            color:#333; transition:all 0.3s ease;
        }
        .nav-link:hover, .nav-link.active {
            background:#006937; color:white;
        }

        .page-container {
            display:flex; align-items:flex-start; justify-content:center;
            min-height:calc(100vh - 90px);
            padding:2rem;
        }
        .main-card {
            background:rgba(255,255,255,0.94);
            border-radius:24px;
            padding:2.5rem;
            width:100%; max-width:680px;
            box-shadow:0 10px 40px rgba(0,0,0,0.25);
            backdrop-filter:blur(10px);
        }
        .card-logo {
            width:90px; height:90px; margin:0 auto 1rem; border-radius:50%;
            overflow:hidden; background:#fff; padding:0.3rem;
        }
        .card-logo img {width:100%; height:100%; object-fit:contain;}
        .main-card h2 {
            font-size:1.8rem; color:#004d29; margin-bottom:0.5rem; text-align:center;
        }
        .main-card > p {
            color:#556b5f; margin-bottom:2rem; font-size:1rem; text-align:center;
        }
        .btn {
            display:inline-block; padding:0.9rem 2rem; border-radius:10px;
            font-weight:600; text-decoration:none; border:none; cursor:pointer;
            font-size:1rem; transition:transform 0.2s;
        }
        .btn:hover {transform:translateY(-2px);}
        .btn-primary {background:#006937; color:white; width:100%; margin:0.5rem 0;}
        .btn-primary:hover {background:#00552d;}
        .btn-secondary {background:transparent; color:#006937; border:2px solid #006937; width:100%; margin:0.5rem 0;}
        .btn-secondary:hover {background:#006937; color:white;}
        .btn-sm {padding:0.6rem 1.2rem; font-size:0.9rem; width:auto;}

        .docs-list {text-align:left; margin-top:1rem;}
        .doc-category {margin-bottom:1.5rem;}
        .doc-category h4 {color:#006937; margin-bottom:0.5rem; font-size:1rem; padding-bottom:0.3rem; border-bottom:2px solid #e2eae5;}
        .doc-item {padding:0.4rem 0; font-size:0.9rem; color:#333; border-bottom:1px solid #eef3f0;}
        .doc-item:before {content:"✓ "; color:#006937; font-weight:bold;}

        .form-grid {display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1.5rem;}
        .form-full {grid-column:1/-1;}
        label {display:block; text-align:left; font-weight:600; font-size:0.9rem; margin-bottom:0.4rem; color:#333;}
        input, select, textarea {
            width:100%; padding:0.9rem; border:2px solid #d1ddd7; border-radius:8px;
            font-size:0.95rem;
        }
        input:focus, select:focus, textarea:focus {outline:none; border-color:#006937;}
        .note {margin-top:1rem; font-size:0.85rem; color:#666; text-align:left; line-height:1.6;}

        /* PAYMENT STYLES */
        .payment-section {margin-top:2rem; padding-top:1.5rem; border-top:2px dashed #d1ddd7;}
        .payment-section h3 {color:#006937; font-size:1.2rem; margin-bottom:1rem; text-align:center;}
        .payment-tabs {display:flex; gap:0.5rem; margin-bottom:1.5rem; flex-wrap:wrap;}
        .pay-tab {
            flex:1; min-width:120px; padding:0.8rem; border:2px solid #e2eae5; background:white;
            border-radius:10px; cursor:pointer; text-align:center; font-weight:600; color:#555; transition:all 0.25s;
        }
        .pay-tab:hover {border-color:#006937;}
        .pay-tab.active {border-color:#006937; background:#f0f7f2; color:#006937;}
        .pay-content {display:none;}
        .pay-content.active {display:block; animation:fadeIn 0.3s ease;}
        @keyframes fadeIn {from{opacity:0; transform:translateY(5px);} to{opacity:1; transform:translateY(0);}}
        .pay-box {background:#f8faf9; padding:1.2rem; border-radius:12px; margin-bottom:1rem; border-left:4px solid #006937;}
        .pay-box h4 {font-size:0.95rem; color:#006937; margin-bottom:0.5rem;}
        .pay-box p {font-size:0.9rem; color:#444; line-height:1.7;}
        .acc-no {font-family:monospace; font-weight:700; font-size:1.1rem; color:#006937; background:#e6f2eb; padding:0.3rem 0.6rem; border-radius:6px; display:inline-block; margin:0.3rem 0;}
        .ref-badge {background:#f5b82e; color:#000; padding:0.3rem 0.7rem; border-radius:20px; font-weight:700; font-size:0.85rem; display:inline-block; margin:0.5rem 0;}
        .amount-box {background:#fff3cd; padding:1rem; border-radius:10px; text-align:center; margin:1rem 0; border:2px solid #f5b82e;}
        .amount {font-size:1.5rem; font-weight:700; color:#926c00;}
        .upload-box {border:2px dashed #d1ddd7; border-radius:10px; padding:1.5rem; text-align:center; cursor:pointer; transition:0.2s;}
        .upload-box:hover {border-color:#006937; background:#f0f7f2;}

        .contact-item {
            text-align:left; background:#f0f7f2; padding:1.5rem; border-radius:12px; margin-bottom:1rem;
        }
        .contact-item h4 {color:#006937; margin-bottom:0.3rem;}
        .contact-item p {color:#444; margin:0;}

        .modal {
            position:fixed; inset:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center;
            z-index:200; opacity:0; visibility:hidden; transition:all 0.3s ease;
        }
        .modal.show {opacity:1; visibility:visible;}
        .modal-content {
            background:white; padding:2.5rem; border-radius:16px; max-width:450px; width:90%; text-align:center;
        }
        .ref-box {
            background:#f0f7f2; padding:0.8rem; border-radius:8px; font-family:monospace;
            font-weight:700; color:#006937; margin:1rem 0; font-size:1.1rem;
        }

        .page-footer {
            text-align:center; padding:1.5rem; color:rgba(255,255,255,0.7); font-size:0.8rem;
            margin-top:1rem;
        }

        @media(max-width:600px) {
            .form-grid {grid-template-columns:1fr;}
            .nav-links {gap:0.25rem;}
            .nav-link {padding:0.6rem 0.9rem; font-size:0.8rem;}
            .main-card {padding:2rem 1.5rem;}
        }
    </style>
</head>
<body>
    <div class="bg-layer"></div>
    <div class="bg-overlay"></div>

    <nav>
        <div class="nav-container">
            <div class="logo-group">
                <div class="logo-slot">
                    <img src="maincampus.jpg" alt="SLSU Main">
                </div>
                <div class="logo-slot">
                    <img src="jge.jpg" alt="SLSU Tagkawayan">
                </div>
                <div class="brand-name">
                    <h1>SLSU · JGE Tagkawayan</h1>
                    <p>Office of the Registrar</p>
                </div>
            </div>
            <div class="nav-links">
                <a href="/" class="nav-link {{home_active}}">Home</a>
                <a href="/services" class="nav-link {{services_active}}">Services</a>
                <a href="/appointment" class="nav-link {{book_active}}">Book & Pay</a>
                <a href="/contact" class="nav-link {{contact_active}}">Contact</a>
            </div>
        </div>
    </nav>
"""

FOOTER = """
    <div class="page-footer">
        © 2026 Southern Luzon State University — JGE Tagkawayan College. Office of the Registrar. All Rights Reserved.
    </div>
</body>
</html>
"""

# ========== HOME PAGE ==========
@app.route('/')
def home():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card" style="text-align:center;">
            <div class="card-logo">
                <img src="jge.jpg" alt="SLSU JGE Tagkawayan">
            </div>
            <h2>Welcome, Students!</h2>
            <p>Official Appointment & Payment System — Office of the Registrar</p>
            
            <a href="/appointment" class="btn btn-primary">📅 Make Appointment & Pay</a>
            <a href="/services" class="btn btn-secondary">📋 View Documents & Fees</a>
        </div>
    </div>
""" + FOOTER, home_active='active', services_active='', book_active='', contact_active='')

# ========== SERVICES PAGE with FEES ==========
@app.route('/services')
def services():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card">
            <h2>📋 Documents & Schedule of Fees</h2>
            <p>Complete list of documents, services, and corresponding rates</p>
            
            <div class="docs-list">
                <div class="doc-category">
                    <h4>📄 Academic Records & Transcripts</h4>
                    <div class="doc-item">Transcript of Records (TOR) — ₱150.00 / copy</div>
                    <div class="doc-item">Certificate of Grades — ₱50.00 / copy</div>
                    <div class="doc-item">Certificate of Registration/COR — ₱50.00</div>
                    <div class="doc-item">Certificate of Units Earned — ₱50.00</div>
                    <div class="doc-item">Evaluation of Records — ₱100.00</div>
                    <div class="doc-item">Honorable Dismissal — ₱100.00</div>
                    <div class="doc-item">Form 137 / Permanent Record — ₱80.00</div>
                    <div class="doc-item">Certificate of Good Moral — ₱50.00</div>
                </div>

                <div class="doc-category">
                    <h4>🎓 Graduation & Diplomas</h4>
                    <div class="doc-item">Original Diploma — Included in Graduation Fee</div>
                    <div class="doc-item">Certified True Copy of Diploma — ₱100.00</div>
                    <div class="doc-item">Certified True Copy of Registration Form — ₱100.00</div>
                    <div class="doc-item">Certificate of Graduation — ₱80.00</div>
                    <div class="doc-item">Replacement of Lost Diploma — ₱500.00</div>
                    <div class="doc-item">Graduation Clearance — ₱200.00</div>
                </div>

                <div class="doc-category">
                    <h4>✅ Enrollment & Registration</h4>
                    <div class="doc-item">Add/Drop/Change Subject — ₱30.00 / subject</div>
                    <div class="doc-item">Change of Course/Major — ₱150.00</div>
                    <div class="doc-item">Cross-Enrollment — ₱100.00</div>
                    <div class="doc-item">Correction of Name/Details — ₱50.00</div>
                    <div class="doc-item">Late Registration — ₱200.00</div>
                </div>

                <div class="doc-category">
                    <h4>📊 Other Certifications</h4>
                    <div class="doc-item">Certificate for Scholarship — ₱50.00</div>
                    <div class="doc-item">Certificate for Employment — ₱50.00</div>
                    <div class="doc-item">Certificate for Board Exam — ₱50.00</div>
                    <div class="doc-item">Authentication of Document — ₱30.00 / page</div>
                    <div class="doc-item">Clearance — ₱30.00</div>
                </div>
            </div>
            
            <p class="note" style="text-align:center; margin-top:1.5rem;">
                💡 <strong>Payment:</strong> Proceed to "Book & Pay" to get your Reference Number before paying.
            </p>
            <a href="/appointment" class="btn btn-primary" style="margin-top:1rem;">📅 Book Appointment & Pay</a>
        </div>
    </div>
""" + FOOTER, home_active='', services_active='active', book_active='', contact_active='')

# ========== BOOK & PAY PAGE ==========
@app.route('/appointment')
def appointment_page():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card">
            <h2>📅 Book Appointment</h2>
            <p>Get your Reference Number — use it for payment</p>
            
            <form id="aptForm">
                <div class="form-grid">
                    <div>
                        <label>Full Name *</label>
                        <input type="text" name="fullname" placeholder="Last Name, First Name, Middle Initial" required>
                    </div>
                    <div>
                        <label>Student ID *</label>
                        <input type="text" name="studentId" placeholder="2023-00123-TG" required>
                    </div>
                    <div>
                        <label>Email Address *</label>
                        <input type="email" name="email" placeholder="your.email@slsu.edu.ph" required>
                    </div>
                    <div>
                        <label>Contact Number *</label>
                        <input type="tel" name="contact" placeholder="09XX-XXX-XXXX" required>
                    </div>
                    <div>
                        <label>Program / Course *</label>
                        <select name="course" required>
                            <option value="">Select Course</option>
                            <option>BS Industrial Technology major in Computer Technology</option>
                            <option>BS Industrial Technology major in Food Technology</option>
                            <option>BS Fisheries and Aquatic Science</option>
                            <option>BS Business Administration major in Financial Management</option>
                            <option>BS Business Administration major in Marketing Management</option>
                            <option>BS Public Administration</option>
                            <option>Bachelor of Secondary Education</option>
                            <option>Bachelor of Elementary Education</option>
                            <option>Other / Non-Student</option>
                        </select>
                    </div>
                    <div>
                        <label>Document / Service *</label>
                        <select name="purpose" id="docType" required>
                            <option value="">Select Document</option>
                            <option value="TOR-150">Transcript of Records — ₱150.00</option>
                            <option value="CERT-GRADES-50">Certificate of Grades — ₱50.00</option>
                            <option value="SUMM-GRADES-50">Summary of Grades — ₱50.00</option>
                            <option value="COR-50">Certificate of Registration — ₱50.00</option>
                            <option value="CERTIFIEDCOR-50">Certified of Registration — ₱50.00</option>
                            <option value="GOODMORAL-50">Certificate of Good Moral — ₱50.00</option>
                            <option value="HON-DISMISS-100">Honorable Dismissal — ₱100.00</option>
                            <option value="FORM137-80">Form 137 — ₱80.00</option>
                            <option value="DIPLOMA-COPY-100">Certified Diploma Copy — ₱100.00</option>
                            <option value="DIPLOMA-REPLACE-500">Lost Diploma Replacement — ₱500.00</option>
                            <option value="ADD-DROP-30">Add/Drop Subject — ₱30.00/subject</option>
                            <option value="CROSS-ENROLL-100">Cross-Enrollment — ₱100.00</option>
                            <option value="CERT-SCHOL-50">Cert. for Scholarship — ₱50.00</option>
                            <option value="AUTH-30">Authentication — ₱30.00/page</option>
                            <option value="GRAD-CLEAR-200">Graduation Clearance — ₱200.00</option>
                            <option value="OTHER">Other — See Cashier</option>
                        </select>
                    </div>
                    <div>
                        <label>Preferred Date *</label>
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
                    <div class="form-full">
                        <label>Remarks / No. of Copies</label>
                        <textarea name="remarks" rows="2" placeholder="e.g. 2 copies, purpose: employment..."></textarea>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary" id="genRefBtn">✅ Generate Reference Number</button>
            </form>

            <!-- PAYMENT SECTION — HIDDEN UNTIL REFERENCE GENERATED -->
            <div class="payment-section" id="paymentSection" style="display:none;">
                <h3>💳 Payment Instructions</h3>
                
                <div class="amount-box">
                    <div>Amount to Pay</div>
                    <div class="amount" id="payAmount">₱0.00</div>
                </div>

                <p style="text-align:center; margin-bottom:1rem;">Your Reference Number:</p>
                <div class="ref-badge" id="refDisplayPmt" style="font-size:1rem; padding:0.6rem 1.2rem;">—</div>

                <p style="text-align:center; font-size:0.85rem; color:#666; margin:1rem 0;">
                    ⚠️ Use this Reference Number when paying. Keep your proof of payment/receipt.
                </p>

                <!-- PAYMENT TABS -->
                <div class="payment-tabs">
                    <div class="pay-tab active" data-tab="bank">🏦 Bank</div>
                    <div class="pay-tab" data-tab="ewallet">📱 E-Wallet</div>
                    <div class="pay-tab" data-tab="over">🏢 Over-the-Counter</div>
                </div>

                <!-- BANK PAYMENTS -->
                <div class="pay-content active" id="bank">
                    <div class="pay-box">
                        <h4>🏦 Land Bank of the Philippines (LBP)</h4>
                        <p>Account Name: <strong>Southern Luzon State University</strong><br>
                        Account No.: <span class="acc-no">3072-1008-95</span><br>
                        Type: Savings Account</p>
                    </div>
                    <div class="pay-box">
                        <h4>🏦 Development Bank of the Philippines (DBP)</h4>
                        <p>Account Name: <strong>SLSU — Trust Fund</strong><br>
                        Account No.: <span class="acc-no">000-1005-004567</span><br>
                        Type: Current Account</p>
                    </div>
                    <div class="pay-box">
                        <h4>🏦 Philippine National Bank (PNB)</h4>
                        <p>Account Name: <strong>Southern Luzon State University</strong><br>
                        Account No.: <span class="acc-no">1234-7890-12</span><br>
                        Type: Savings Account</p>
                    </div>
                </div>

                <!-- E-WALLET PAYMENTS -->
                <div class="pay-content" id="ewallet">
                    <div class="pay-box">
                        <h4>📱 GCash</h4>
                        <p>Account Name: <strong>SLSU — Official Collection</strong><br>
                        Number: <span class="acc-no">0917-123-4567</span><br>
                        <strong>Remarks:</strong> Enter your Reference Number & Full Name</p>
                    </div>
                    <div class="pay-box">
                        <h4>📱 Maya</h4>
                        <p>Account Name: <strong>Southern Luzon State University</strong><br>
                        Number: <span class="acc-no">0918-987-6543</span><br>
                        <strong>Remarks:</strong> Enter your Reference Number & Student ID</p>
                    </div>
                    <div class="pay-box">
                        <h4>📱 Coins.ph</h4>
                        <p>Account Name: <strong>SLSU Finance Office</strong><br>
                        Number: <span class="acc-no">0998-123-4567</span><br>
                        Purpose: Registrar Document Fee</p>
                    </div>
                </div>

                <!-- OVER-THE-COUNTER -->
                <div class="pay-content" id="over">
                    <div class="pay-box">
                        <h4>🏢 SLSU Cashier — Main Campus</h4>
                        <p>📍 Administration Building, Lucban, Quezon<br>
                        🕐 8:00 AM – 4:00 PM, Mon–Fri<br>
                        Present your Reference Number at the window</p>
                    </div>
                    <div class="pay-box">
                        <h4>🏢 SLSU JGE Tagkawayan — Cashier</h4>
                        <p>📍 Registrar Building, Tagkawayan Campus<br>
                        🕐 8:30 AM – 3:30 PM, Mon–Fri<br>
                        On-site payment available here</p>
                    </div>
                    <div class="pay-box">
                        <h4>🏢 Bayad Center / SM Bills Payment</h4>
                        <p>Biller: <strong>Southern Luzon State University</strong><br>
                        Enter Reference Number as Account No.<br>
                        Add ₱15.00 convenience fee</p>
                    </div>
                </div>

                <p class="note" style="margin-top:1.5rem; background:#fff9e6; padding:1rem; border-radius:8px; border-left:3px solid:#f5b82e;">
                    📌 <strong>After Payment:</strong> Send proof of payment (screenshot/receipt) to <em>treasury.tagkawayan@slsu.edu.ph</em> or present original receipt at the Registrar's Office on your appointment date.
                </p>
            </div>
        </div>
    </div>

    <!-- SUCCESS MODAL -->
    <div class="modal" id="successModal">
        <div class="modal-content">
            <div style="font-size:3rem;">✅</div>
            <h3 style="color:#006937; margin:1rem 0;">Reference Generated!</h3>
            <p>Your Reference Number:</p>
            <div class="ref-box" id="refModal">—</div>
            <p style="font-size:0.9rem; color:#555; margin-bottom:1.5rem;">Scroll down to view payment options.</p>
            <button class="btn btn-primary" onclick="closeModal()">Got it</button>
        </div>
    </div>

    <script>
        // Min date = today
        document.getElementById('minDate').min = new Date().toISOString().split('T')[0];

        // Amount mapping
        const feeMap = {
            'TOR-150': 150, 'CERT-GRADES-50': 50, 'COR-50': 50, 'GOODMORAL-50': 50,
            'HON-DISMISS-100': 100, 'FORM137-80': 80, 'DIPLOMA-COPY-100': 100,
            'DIPLOMA-REPLACE-500': 500, 'ADD-DROP-30': 30, 'CROSS-ENROLL-100': 100,
            'CERT-SCHOL-50': 50, 'AUTH-30': 30, 'GRAD-CLEAR-200': 200, 'OTHER': 0
        };

        // Tab switching
        document.querySelectorAll('.pay-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.pay-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.pay-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });

        // Form submit
        document.getElementById('aptForm').addEventListener('submit', async e => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const res = await fetch('/submit-appointment', {
                method: 'POST',
                body: formData
            });
            
            const data = await res.json();
            
            if (data.success) {
                // Update all reference displays
                document.getElementById('refModal').textContent = data.ref_num;
                document.getElementById('refDisplayPmt').textContent = data.ref_num;
                
                // Update amount
                const selected = document.getElementById('docType').value;
                const amount = feeMap[selected] || 0;
                document.getElementById('payAmount').textContent = amount > 0 ? ₱${amount.toFixed(2)} : 'See Cashier';
                
                // Show payment section & modal
                document.getElementById('paymentSection').style.display = 'block';
                document.getElementById('successModal').classList.add('show');
                
                // Scroll to payment section
                setTimeout(() => {
                    document.getElementById('paymentSection').scrollIntoView({behavior:'smooth'});
                }, 300);
            }
        });

        function closeModal() {
            document.getElementById('successModal').classList.remove('show');
        }
    </script>
""" + FOOTER, home_active='', services_active='', book_active='active', contact_active='')

# ========== CONTACT PAGE ==========
@app.route('/contact')
def contact():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card">
            <h2>📍 Contact & Payment Channels</h2>
            <p>Reach us or pay through these official channels</p>
            
            <div style="margin-top:2rem;">
                <div class="contact-item">
                    <h4>📍 Office Location</h4>
                    <p>SLSU JGE Tagkawayan College<br>Registrar Building, Tagkawayan, Quezon</p>
                </div>
                <div class="contact-item">
                    <h4>📧 Email</h4>
                    <p>registrar.tagkawayan@slsu.edu.ph<br>treasury.tagkawayan@slsu.edu.ph (payments)</p>
                </div>
                <div class="contact-item">
                    <h4>📞 Contact No.</h4>
                    <p>(042) XXX-XXXX — Registrar<br>(042) XXX-XXXX — Cashier/Finance</p>
                </div>
                <div class="contact-item">
                    <h4>🏦 Official Bank Accounts</h4>
                    <p>Land Bank: 3072-1008-95<br>DBP: 000-1005-004567<br>PNB: 1234-7890-12<br>— All under "Southern Luzon State University"</p>
                </div>
                <div class="contact-item">
                    <h4>📱 E-Wallets</h4>
                    <p>GCash: 0917-123-4567<br>Maya: 0918-987-6543<br>Coins.ph: 0998-123-4567</p>
                </div>
                <div class="contact-item">
                    <h4>🕐 Office Hours</h4>
                    <p>Monday – Friday<br>8:00 AM – 5:00 PM<br>Processing of payments until 4:00 PM only</p>
                </div>
            </div>
            
            <a href="/appointment" class="btn btn-primary" style="margin-top:2rem;">📅 Start Appointment & Payment</a>
        </div>
    </div>
""" + FOOTER, home_active='', services_active='', book_active='', contact_active='active')

# ========== SUBMISSION HANDLER ==========
@app.route('/submit-appointment', methods=['POST'])
def submit_appointment():
    try:
        data = request.form
        today = datetime.now()
        date_str = today.strftime('%y%m%d')
        unique_id = str(uuid.uuid4())[:5].upper()
        ref_num = f"SLSU-TG-{date_str}-{unique_id}"
        
        apt = {
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
        appointments.append(apt)
        
        print(f"\n📝 NEW APPOINTMENT: {ref_num}")
        for k, v in apt.items():
            print(f"   {k}: {v}")
        
        return jsonify({"success": True, "ref_num": ref_num})
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"success": False}), 400

# ========== ADMIN PANEL ==========
@app.route('/admin')
def admin():
    if not appointments:
        return "<h1 style='padding:3rem; text-align:center; color:#006937;'>No appointments yet.<br><a href='/' style='color:inherit;'>← Return Home</a></h1>"
    
    html = """
    <style>
        body {font-family:Arial, sans-serif; margin:0; background:#f0f7f2;}
        h1 {background:#006937; color:white; padding:1.5rem; text-align:center; margin:0;}
        table {border-collapse:collapse; width:96%; margin:2rem auto; background:white; box-shadow:0 2px 10px rgba(0,0,0,0.1);}
        th {background:#006937; color:white; padding:0.8rem; text-align:left;}
        td {padding:0.7rem; border-bottom:1px solid #e2eae5;}
        tr:hover {background:#f8faf9;}
        .back {text-align:center; margin:1rem;}
        .back a {color:#006937; font-weight:bold; text-decoration:none;}
    </style>
    <h1>📋 Registrar — All Appointments</h1>
    <table>
        <tr>
            <th>Reference No.</th>
            <th>Full Name</th>
            <th>Student ID</th>
            <th>Document / Service</th>
            <th>Appointment Date</th>
            <th>Contact</th>
        </tr>
    """
    
    for a in appointments:
        html += f"""
        <tr>
            <td><strong>{a['ref_num']}</strong></td>
            <td>{a['fullname']}</td>
            <td>{a['student_id']}</td>
            <td>{a['purpose']}</td>
            <td>{a['apt_date']} — {a['apt_time']}</td>
            <td>{a['contact']}</td>
        </tr>
        """
    
    html += "</table><div class='back'><a href='/'>← Back to Homepage</a></div>"
    return html

if __name__ == '__main__':
    print("="*70)
    print("🎓 SLSU JGE Tagkawayan — Registrar Appointment & Payment System")
    print("✅ Homepage:   http://127.0.0.1:5000")
    print("📋 Admin List: http://127.0.0.1:5000/admin")
    print("="*70)
    app.run(debug=True)
