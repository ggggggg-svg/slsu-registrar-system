from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import os
from html import escape
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-secret-key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

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

        /* BACKGROUND */
        .bg-layer {
            position:fixed; inset:0; z-index:-2;
            background: url('https://i.imgur.com/KCvL9wY.jpg') no-repeat center center;
            background-size:cover;
        }
        .bg-overlay {
            position:fixed; inset:0; z-index:-1;
            background:rgba(0,35,15,0.65);
        }

        /* NAVIGATION */
        nav {
            background:rgba(255,255,255,0.95);
            padding:1rem 2rem;
            box-shadow:0 2px 10px rgba(0,0,0,0.08);
            position:sticky; top:0; z-index:100;
        }
        .nav-container {
            max-width:1200px; margin:0 auto;
            display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;
        }
        .logo-group {display:flex; align-items:center; gap:1rem;}
        .logo-slot {width:54px; height:54px; border-radius:12px; overflow:hidden; background:#fff; border:1px solid #d9e6de; display:flex; align-items:center; justify-content:center; padding:4px; box-shadow:0 2px 8px rgba(0,0,0,.06);}
        .logo-slot img {width:100%; height:100%; object-fit:contain;}
        .brand-name {line-height:1.2;}
        .brand-name h1 {font-size:0.95rem; color:#006937; font-weight:700; letter-spacing:0.3px;}
        .brand-name p {font-size:0.75rem; color:#555;}
        .nav-links {display:flex; gap:0.4rem; flex-wrap:wrap;}
        .nav-link {
            padding:0.7rem 1.4rem; border-radius:8px; text-decoration:none;
            font-weight:600; font-size:0.88rem;
            color:#333; transition:all 0.25s ease;
        }
        .nav-link:hover, .nav-link.active {
            background:#006937; color:#ffffff;
        }

        /* PAGE CONTAINER */
        .page-container {
            display:flex; align-items:flex-start; justify-content:center;
            min-height:calc(100vh - 90px);
            padding:2.5rem 1.25rem;
        }
        .main-card {
            background:rgba(255,255,255,0.97);
            border-radius:22px;
            padding:2.25rem;
            width:100%; max-width:980px;
            box-shadow:0 10px 40px rgba(0,0,0,0.2);
            backdrop-filter:blur(10px);
        }
        .hero-card {
            background:rgba(255,255,255,0.9);
            border-radius:20px;
            padding:3rem 2.5rem;
            width:100%; max-width:520px;
            box-shadow:0 10px 40px rgba(0,0,0,0.25);
            backdrop-filter:blur(12px);
            text-align:center;
        }
        .hero-logo {
            width:100px; height:100px; margin:0 auto 1.5rem; border-radius:50%;
            overflow:hidden; background:#fff; padding:0.4rem; border:3px solid #006937;
        }
        .hero-logo img {width:100%; height:100%; object-fit:contain;}
        .hero-card h2 {
            font-size:1.9rem; color:#004d29; margin-bottom:0.5rem; font-weight:700;
        }
        .hero-card p {
            color:#556b5f; margin-bottom:2rem; font-size:1rem; line-height:1.6;
        }

        .card-logo {
            width:80px; height:80px; margin:0 auto 1rem; border-radius:50%;
            overflow:hidden; background:#fff; padding:0.3rem; border:2px solid #006937;
        }
        .card-logo img {width:100%; height:100%; object-fit:contain;}
        .main-card h2 {
            font-size:1.6rem; color:#004d29; margin-bottom:0.5rem; text-align:center; font-weight:700;
        }
        .main-card > p {
            color:#556b5f; margin-bottom:1.8rem; font-size:0.95rem; text-align:center;
        }

        /* BUTTONS */
        .btn {
            display:inline-block; padding:0.9rem 2rem; border-radius:10px;
            font-weight:600; text-decoration:none; border:none; cursor:pointer;
            font-size:0.95rem; transition:all 0.25s ease; width:100%;
            text-align:center;
        }
        .btn:hover {transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,105,55,0.2);}
        .btn-primary {background:#006937; color:#ffffff; margin:0.5rem 0;}
        .btn-primary:hover {background:#00552d;}
        .btn-secondary {background:transparent; color:#006937; border:2px solid #006937; margin:0.5rem 0;}
        .btn-secondary:hover {background:#006937; color:#ffffff;}
        .btn-sm {padding:0.6rem 1.2rem; font-size:0.85rem; width:auto;}

        /* DOCUMENTS LIST */
        .docs-list {text-align:left; margin-top:1rem;}
        .doc-category {margin-bottom:1.5rem;}
        .doc-category h4 {color:#006937; margin-bottom:0.6rem; font-size:0.95rem; padding-bottom:0.4rem; border-bottom:2px solid #e2eae5; font-weight:600;}
        .doc-item {padding:0.5rem 0; font-size:0.9rem; color:#333; border-bottom:1px solid #eef3f0;}
        .doc-item:before {content:"• "; color:#006937; font-weight:bold;}

        /* FORM */
        .form-grid {display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1.5rem;}
        .form-full {grid-column:1/-1;}
        label {display:block; text-align:left; font-weight:600; font-size:0.88rem; margin-bottom:0.4rem; color:#333;}
        input, select, textarea {
            width:100%; padding:0.9rem; border:2px solid #d1ddd7; border-radius:8px;
            font-size:0.95rem;
        }
        input:focus, select:focus, textarea:focus {outline:none; border-color:#006937;}
        .note {margin-top:1rem; font-size:0.85rem; color:#666; text-align:left; line-height:1.6; background:#f9fbf9; padding:1rem; border-radius:8px; border-left:3px solid #006937;}

        /* PAYMENT SECTION */
        .payment-section {margin-top:2rem; padding-top:2rem; border-top:2px dashed #d1ddd7;}
        .payment-section h3 {color:#006937; font-size:1.15rem; margin-bottom:1.2rem; text-align:center; font-weight:600;}
        .payment-tabs {display:flex; gap:0.6rem; margin-bottom:1.5rem; flex-wrap:wrap; justify-content:center;}
        .pay-tab {
            flex:1; min-width:130px; padding:0.9rem; border:2px solid #e2eae5; background:#ffffff;
            border-radius:10px; cursor:pointer; text-align:center; font-weight:600; color:#555; transition:all 0.25s;
        }
        .pay-tab:hover {border-color:#006937; color:#006937;}
        .pay-tab.active {border-color:#006937; background:#f0f7f2; color:#006937;}
        .pay-content {display:none; animation:fadeIn 0.3s ease;}
        .pay-content.active {display:block;}
        @keyframes fadeIn {from{opacity:0; transform:translateY(5px);} to{opacity:1; transform:translateY(0);}}
        .pay-box {background:#f8faf9; padding:1.3rem; border-radius:12px; margin-bottom:1rem; border-left:4px solid #006937;}
        .pay-box h4 {font-size:0.95rem; color:#006937; margin-bottom:0.6rem; font-weight:600;}
        .pay-box p {font-size:0.9rem; color:#444; line-height:1.7;}
        .acc-no {font-family:'Courier New', monospace; font-weight:700; font-size:1rem; color:#006937; background:#e6f2eb; padding:0.4rem 0.7rem; border-radius:6px; display:inline-block; margin:0.4rem 0;}
        .ref-badge {background:#f5b82e; color:#222; padding:0.5rem 1.2rem; border-radius:24px; font-weight:700; font-size:1rem; display:inline-block; margin:0.5rem 0;}
        .amount-box {background:#fff9e6; padding:1.2rem; border-radius:10px; text-align:center; margin:1.2rem 0; border:2px solid #f5b82e;}
        .amount {font-size:1.6rem; font-weight:700; color:#926c00; margin-top:0.3rem;}

        /* CONTACT ITEMS */
        .contact-item {
            text-align:left; background:#f0f7f2; padding:1.4rem; border-radius:12px; margin-bottom:1rem;
        }
        .contact-item h4 {color:#006937; margin-bottom:0.5rem; font-weight:600;}
        .contact-item p {color:#444; margin:0; line-height:1.6;}

        /* MODAL */
        .modal {
            position:fixed; inset:0; background:rgba(0,0,0,0.55); display:flex; align-items:center; justify-content:center;
            z-index:200; opacity:0; visibility:hidden; transition:all 0.3s ease;
        }
        .modal.show {opacity:1; visibility:visible;}
        .modal-content {
            background:#ffffff; padding:2.5rem; border-radius:16px; max-width:440px; width:90%; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.2);
        }
        .ref-box {
            background:#f0f7f2; padding:1rem; border-radius:10px; font-family:'Courier New', monospace;
            font-weight:700; color:#006937; margin:1.2rem 0; font-size:1.15rem; letter-spacing:1px;
        }

        /* ADMIN STYLES */
        .admin-table {width:100%; border-collapse:collapse; margin-top:1.5rem;}
        .admin-table th {background:#006937; color:#ffffff; padding:0.9rem; text-align:left; font-weight:600; font-size:0.88rem;}
        .admin-table td {padding:0.9rem; border-bottom:1px solid #e2eae5; font-size:0.9rem;}
        .admin-table tr:hover {background:#f8faf9;}
        .admin-header {display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:1rem;}
        .admin-header h2 {margin:0;}
        .empty-state {text-align:center; padding:3rem 1rem; color:#666;}
        .back-link {display:inline-block; margin-top:1.5rem; color:#006937; font-weight:600; text-decoration:none;}
        .back-link:hover {text-decoration:underline;}

        /* FOOTER */
        .page-footer {
            text-align:center; padding:1.5rem; color:rgba(255,255,255,0.75); font-size:0.8rem;
            margin-top:1rem;
        }

        @media(max-width:600px) {
            .form-grid {grid-template-columns:1fr;}
            .nav-links {gap:0.3rem;}
            .nav-link {padding:0.6rem 1rem; font-size:0.8rem;}
            .main-card, .hero-card {padding:2rem 1.5rem;}
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
                    <img src="maincampus.jpg" alt="SLSU Main Campus">
                </div>
                <div class="logo-slot">
                    <img src="jge.jpg" alt="SLSU JGE Tagkawayan">
                </div>
                <div class="brand-name">
                    <h1>SLSU · JGE Tagkawayan</h1>
                    <p>Office of the Registrar</p>
                </div>
            </div>
            <div class="nav-links">
                <a href="/" class="nav-link {{home_active}}">Home</a>
                <a href="/services" class="nav-link {{services_active}}">Services</a>
                <a href="/appointment" class="nav-link {{book_active}}">Appointment</a>
                <a href="/contact" class="nav-link {{contact_active}}">Contact</a>
            </div>
        </div>
    </nav>
"""

FOOTER = """
    <div class="page-footer">
        © 2026 Southern Luzon State University — Judge Guillermo Eleazar College of Agriculture and Technology – Tagkawayan. 
        Office of the Registrar. All Rights Reserved.
    </div>
</body>
</html>
"""

# ========== HOME PAGE — Clean Version ==========
@app.route('/')
def home():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="hero-card">
            <div class="hero-logo">
                <img src="jge.jpg" alt="SLSU JGE Tagkawayan Official Seal">
            </div>
            <h2>Welcome, Students!</h2>
            <p>Official Appointment and Payment System<br>Office of the Registrar</p>
            
            <a href="/appointment" class="btn btn-primary">Schedule an Appointment</a>
        </div>
    </div>
""" + FOOTER, home_active='active', services_active='', book_active='', contact_active='', admin_active='')

# ========== SERVICES PAGE ==========
@app.route('/services')
def services():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card">
            <h2>Services and Schedule of Fees</h2>
            <p>Complete list of documents, transactions, and corresponding rates</p>
            
            <div class="docs-list">
                <div class="doc-category">
                    <h4>Academic Records and Transcripts</h4>
                    <div class="doc-item">Transcript of Records — One Hundred Fifty Pesos (PHP 150.00) per copy</div>
                    <div class="doc-item">Certificate of Grades — Fifty Pesos (PHP 50.00) per copy</div>
                    <div class="doc-item">Certificate of Registration — Fifty Pesos (PHP 50.00)</div>
                    <div class="doc-item">Certificate of Units Earned — Fifty Pesos (PHP 50.00)</div>
                    <div class="doc-item">Evaluation of Records and Subject Equivalency — One Hundred Pesos (PHP 100.00)</div>
                    <div class="doc-item">Honorable Dismissal / Transfer Credentials — One Hundred Pesos (PHP 100.00)</div>
                    <div class="doc-item">Form 137 / Permanent Student Record — Eighty Pesos (PHP 80.00)</div>
                    <div class="doc-item">Certificate of Good Moral Character — Fifty Pesos (PHP 50.00)</div>
                </div>

                <div class="doc-category">
                    <h4>Graduation and Diplomas</h4>
                    <div class="doc-item">Original Diploma — Included in Graduation Fee</div>
                    <div class="doc-item">Certified True Copy of Diploma — One Hundred Pesos (PHP 100.00)</div>
                    <div class="doc-item">Certificate of Graduation — Eighty Pesos (PHP 80.00)</div>
                    <div class="doc-item">Replacement of Lost Diploma — Five Hundred Pesos (PHP 500.00)</div>
                    <div class="doc-item">Graduation Clearance Processing — Two Hundred Pesos (PHP 200.00)</div>
                </div>

                <div class="doc-category">
                    <h4>Enrollment and Registration</h4>
                    <div class="doc-item">Add/Drop or Change of Subject — Thirty Pesos (PHP 30.00) per subject</div>
                    <div class="doc-item">Change of Course or Major — One Hundred Fifty Pesos (PHP 150.00)</div>
                    <div class="doc-item">Cross-Enrollment Request — One Hundred Pesos (PHP 100.00)</div>
                    <div class="doc-item">Correction of Name or Student Details — Fifty Pesos (PHP 50.00)</div>
                    <div class="doc-item">Late Registration — Two Hundred Pesos (PHP 200.00)</div>
                </div>

                <div class="doc-category">
                    <h4>Certifications and Authentication</h4>
                    <div class="doc-item">Certificate for Scholarship Purposes — Fifty Pesos (PHP 50.00)</div>
                    <div class="doc-item">Certificate for Employment Purposes — Fifty Pesos (PHP 50.00)</div>
                    <div class="doc-item">Certificate for Board Examination — Fifty Pesos (PHP 50.00)</div>
                    <div class="doc-item">Authentication of Document — Thirty Pesos (PHP 30.00) per page</div>
                    <div class="doc-item">Clearance — Thirty Pesos (PHP 30.00)</div>
                </div>
            </div>
            
            <p class="note">
                <strong>Payment Instruction:</strong> Proceed to Appointment page to generate your Reference Number before making any payment.
            </p>
        </div>
    </div>
""" + FOOTER, home_active='', services_active='active', book_active='', contact_active='', admin_active='')

# ========== APPOINTMENT AND PAYMENT PAGE ==========
@app.route('/appointment')
def appointment_page():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card">
            <h2>Appointment and Payment</h2>
            <p>Generate your Reference Number and proceed with payment</p>
            
            <form id="aptForm">
                <div class="form-grid">
                    <div>
                        <label>Full Name *</label>
                        <input type="text" name="fullname" placeholder="Last, First, Middle Initial" required>
                    </div>
                    <div>
                        <label>Student Identification Number *</label>
                        <input type="text" name="studentId" placeholder="Example: 2023J-00123" required>
                    </div>
                    <div>
                        <label>Email Address *</label>
                        <input type="email" name="email" placeholder="name@gmail.com" required>
                    </div>
                    <div>
                        <label>Contact Number *</label>
                        <input type="tel" name="contact" placeholder="09XX-XXX-XXXX" required>
                    </div>
                    <div>
                        <label>Program or Course *</label>
                        <select name="course" required>
                            <option value="">SELECT</option>
                            <option>Bachelor of Science in Industrial Technology — Computer Technology</option>
                            <option>Bachelor of Science in Industrial Technology — Food Technology</option>
                            <option>Bachelor of Science in Fisheries and Aquatic Science</option>
                            <option>Bachelor of Science in Business Administration — Financial Management</option>
                            <option>Bachelor of Science in Business Administration — Marketing Management</option>
                            <option>Bachelor of Science in Public Administration</option>
                            <option>Bachelor of Secondary Education</option>
                            <option>Bachelor of Elementary Education</option>
                            <option>Other / Non-Student</option>
                        </select>
                    </div>
                    <div>
                        <label>Document or Service Requested *</label>
                        <select name="purpose" id="docType" required>
                            <option value="">SELECT</option>
                            <option value="TOR-150">Transcript of Records — PHP 150.00</option>
                            <option value="GRADESCERT-50">Certificate of Grades — PHP 50.00</option>
                            <option value="COR-50">Certificate of Registration — PHP 50.00</option>
                            <option value="GOODMORAL-50">Certificate of Good Moral Character — PHP 50.00</option>
                            <option value="HONDISMISS-100">Honorable Dismissal — PHP 100.00</option>
                            <option value="FORM137-80">Form 137 / Permanent Record — PHP 80.00</option>
                            <option value="DIPLOMACOPY-100">Certified Diploma Copy — PHP 100.00</option>
                            <option value="DIPLOMAREPLACE-500">Replacement of Lost Diploma — PHP 500.00</option>
                            <option value="ADDDROP-30">Add/Drop Subject — PHP 30.00 per subject</option>
                            <option value="CROSSENROLL-100">Cross-Enrollment — PHP 100.00</option>
                            <option value="SCHOLARCERT-50">Certificate for Scholarship — PHP 50.00</option>
                            <option value="AUTH-30">Document Authentication — PHP 30.00 per page</option>
                            <option value="GRADCLEAR-200">Graduation Clearance — PHP 200.00</option>
                            <option value="OTHER">Other — Please See Cashier</option>
                        </select>
                    </div>
                    <div>
                        <label>Preferred Appointment Date *</label>
                        <input type="date" name="aptDate" id="minDate" required>
                    </div>
                    <div>
                        <label>Preferred Time Slot *</label>
                        <select name="aptTime" required>
                            <option value="">SELECT</option>
                            <option>09:00 AM — 10:00 AM</option>
                            <option>10:00 AM — 11:00 AM</option>
                            <option>01:00 PM — 02:00 PM</option>
                            <option>02:00 PM — 03:00 PM</option>
                            <option>03:00 PM — 04:00 PM</option>
                        </select>
                    </div>
                    <div class="form-full">
                        <label>Remarks, Number of Copies, or Additional Details</label>
                        <textarea name="remarks" rows="3" placeholder="Specify purpose, number of copies, or other details..."></textarea>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary">Generate Reference Number</button>
            </form>

            <!-- PAYMENT SECTION -->
            <div class="payment-section" id="paymentSection" style="display:none;">
                <h3>Payment Instructions</h3>
                
                <div class="amount-box">
                    <div>Amount Due</div>
                    <div class="amount" id="payAmount">PHP 0.00</div>
                </div>

                <p style="text-align:center; margin-bottom:0.5rem;">Official Reference Number</p>
                <div class="ref-badge" id="refDisplayPmt">—</div>

                <p style="text-align:center; font-size:0.85rem; color:#666; margin:1rem 0;">
                    Please use this Reference Number when making payment. Retain your proof of payment.
                </p>

                <div class="payment-tabs">
                    <div class="pay-tab active" data-tab="bank">Bank Payment</div>
                    <div class="pay-tab" data-tab="ewallet">Electronic Wallet</div>
                    <div class="pay-tab" data-tab="over">Over-the-Counter</div>
                </div>

                <div class="pay-content active" id="bank">
                    <div class="pay-box">
                        <h4>Land Bank of the Philippines</h4>
                        <p>Account Name: Southern Luzon State University<br>
                        Account Number: <span class="acc-no">3072-1008-95</span><br>
                        Account Type: Savings Account</p>
                    </div>
                    <div class="pay-box">
                        <h4>Development Bank of the Philippines</h4>
                        <p>Account Name: SLSU — Trust Fund<br>
                        Account Number: <span class="acc-no">000-1005-004567</span><br>
                        Account Type: Current Account</p>
                    </div>
                    <div class="pay-box">
                        <h4>Philippine National Bank</h4>
                        <p>Account Name: Southern Luzon State University<br>
                        Account Number: <span class="acc-no">1234-7890-12</span><br>
                        Account Type: Savings Account</p>
                    </div>
                </div>

                <div class="pay-content" id="ewallet">
                    <div class="pay-box">
                        <h4>GCash</h4>
                        <p>Account Name: SLSU — Official Collection<br>
                        Account Number: <span class="acc-no">0917-123-4567</span><br>
                        Remarks: Enter Reference Number and Full Name</p>
                    </div>
                    <div class="pay-box">
                        <h4>Maya</h4>
                        <p>Account Name: Southern Luzon State University<br>
                        Account Number: <span class="acc-no">0918-987-6543</span><br>
                        Remarks: Enter Reference Number and Student Identification Number</p>
                    </div>
                    <div class="pay-box">
                        <h4>Coins.ph</h4>
                        <p>Account Name: SLSU Finance Office<br>
                        Account Number: <span class="acc-no">0998-123-4567</span><br>
                        Purpose: Registrar Document Fee</p>
                    </div>
                </div>

                <div class="pay-content" id="over">
                    <div class="pay-box">
                        <h4>SLSU Cashier — Main Campus</h4>
                        <p>Administration Building, Lucban, Quezon<br>
                        Operating Hours: 8:00 AM — 4:00 PM, Monday to Friday<br>
                        Present your Reference Number at the payment window</p>
                    </div>
                    <div class="pay-box">
                        <h4>SLSU JGE Tagkawayan — Cashier Office</h4>
                        <p>Registrar Building, Tagkawayan Campus<br>
                        Operating Hours: 8:30 AM — 3:30 PM, Monday to Friday<br>
                        On-site payment is available at this campus</p>
                    </div>
                    <div class="pay-box">
                        <h4>Authorized Payment Centers</h4>
                        <p>Biller Name: Southern Luzon State University<br>
                        Enter Reference Number as Account Number<br>
                        Additional convenience fee of PHP 15.00 may apply</p>
                    </div>
                </div>

                <p class="note">
                    <strong>After Payment:</strong> Send a copy of your proof of payment to 
                    treasury.tagkawayan@slsu.edu.ph or present the original receipt at the Office of the Registrar 
                    on your scheduled appointment date.
                </p>
            </div>
        </div>
    </div>

    <!-- CONFIRMATION MODAL -->
    <div class="modal" id="successModal">
        <div class="modal-content">
            <div style="font-size:2.5rem;">✓</div>
            <h3 style="color:#006937; margin:1rem 0;">Reference Generated Successfully</h3>
            <p>Your Official Reference Number</p>
            <div class="ref-box" id="refModal">—</div>
            <p style="font-size:0.85rem; color:#666; margin-bottom:1.5rem;">Please scroll down to view payment options.</p>
            <button class="btn btn-primary" onclick="closeModal()">Acknowledged</button>
        </div>
    </div>

    <script>
        document.getElementById('minDate').min = new Date().toISOString().split('T')[0];

        const feeMap = {
            'TOR-150': 150, 'GRADESCERT-50': 50, 'COR-50': 50, 'GOODMORAL-50': 50,
            'HONDISMISS-100': 100, 'FORM137-80': 80, 'DIPLOMACOPY-100': 100,
            'DIPLOMAREPLACE-500': 500, 'ADDDROP-30': 30, 'CROSSENROLL-100': 100,
            'SCHOLARCERT-50': 50, 'AUTH-30': 30, 'GRADCLEAR-200': 200, 'OTHER': 0
        };

        document.querySelectorAll('.pay-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.pay-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.pay-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });

        document.getElementById('aptForm').addEventListener('submit', async e => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const res = await fetch('/submit-appointment', {
                method: 'POST',
                body: formData
            });
            
            const data = await res.json();
            
            if (data.success) {
                document.getElementById('refModal').textContent = data.ref_num;
                document.getElementById('refDisplayPmt').textContent = data.ref_num;
                
                const selected = document.getElementById('docType').value;
                const amount = feeMap[selected] || 0;
                document.getElementById('payAmount').textContent = amount > 0 
                    ? 'PHP ' + amount.toFixed(2) 
                    : 'Please See Cashier';
                
                document.getElementById('paymentSection').style.display = 'block';
                document.getElementById('successModal').classList.add('show');
                
                setTimeout(() => {
                    document.getElementById('paymentSection').scrollIntoView({behavior:'smooth'});
                }, 300);
            }
        });

        function closeModal() {
            document.getElementById('successModal').classList.remove('show');
        }
    </script>
""" + FOOTER, home_active='', services_active='', book_active='active', contact_active='', admin_active='')

# ========== CONTACT PAGE ==========
@app.route('/contact')
def contact():
    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card">
            <h2>Contact Information</h2>
            <p>Office of the Registrar — SLSU JGE Tagkawayan College</p>
            
            <div style="margin-top:1.5rem;">
                <div class="contact-item">
                    <h4>Office Location</h4>
                    <p>SLSU Judge Guillermo Eleazar — Tagkawayan<br>
                    Registrar Building, Brgy. Rizal, Tagkawayan, Quezon Province</p>
                </div>
                <div class="contact-item">
                    <h4>Email Address</h4>
                    <p>registrar.tagkawayan@slsu.edu.ph — Registrar Office<br>
                    treasury.tagkawayan@slsu.edu.ph — Payment and Finance Concerns</p>
                </div>
                <div class="contact-item">
                    <h4>Telephone and Contact Numbers</h4>
                    <p>(042) XXX-XXXX — Registrar Office<br>
                    (042) XXX-XXXX — Cashier and Finance Office</p>
                </div>
                <div class="contact-item">
                    <h4>Official Bank and Payment Channels</h4>
                    <p>Land Bank of the Philippines: 3072-1008-95<br>
                    Development Bank of the Philippines: 000-1005-004567<br>
                    Philippine National Bank: 1234-7890-12<br>
                    GCash: 0917-123-4567 | Maya: 0918-987-6543</p>
                </div>
                <div class="contact-item">
                    <h4>Operating Hours</h4>
                    <p>Monday through Friday<br>
                    8:00 AM to 5:00 PM<br>
                    Payment transactions are accepted until 4:00 PM only</p>
                </div>
            </div>
        </div>
    </div>
""" + FOOTER, home_active='', services_active='', book_active='', contact_active='active', admin_active='')

# ========== ADMINISTRATOR LOGIN ==========
@app.route('/administrator/login', methods=['GET', 'POST'])
def administrator_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('administrator'))
        return render_template_string(SHARED_HEAD + """
        <div class="page-container">
            <div class="main-card" style="max-width:460px;">
                <div class="card-logo">
                    <img src="jge.jpg" alt="SLSU JGE Tagkawayan">
                </div>
                <h2>Administrator Login</h2>
                <p>Authorized personnel only.</p>
                <div class="note" style="border-left-color:#b42318; background:#fff6f5; color:#8a1c13;">
                    Incorrect administrator password.
                </div>
                <form method="post" style="margin-top:1rem;">
                    <label for="password">Administrator Password</label>
                    <input id="password" type="password" name="password" placeholder="Enter password" required autofocus>
                    <button type="submit" class="btn btn-primary" style="margin-top:1rem;">Sign In</button>
                </form>
                <a href="/" class="back-link">← Return to Homepage</a>
            </div>
        </div>
        """ + FOOTER, home_active='', services_active='', book_active='', contact_active='', admin_active='')

    return render_template_string(SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card" style="max-width:460px;">
            <div class="card-logo">
                <img src="jge.jpg" alt="SLSU JGE Tagkawayan">
            </div>
            <h2>Administrator Login</h2>
            <p>Authorized personnel only. Please sign in to view appointment records.</p>
            <form method="post" style="margin-top:1rem;">
                <label for="password">Administrator Password</label>
                <input id="password" type="password" name="password" placeholder="Enter password" required autofocus>
                <button type="submit" class="btn btn-primary" style="margin-top:1rem;">Sign In</button>
            </form>
            <a href="/" class="back-link">← Return to Homepage</a>
        </div>
    </div>
    """ + FOOTER, home_active='', services_active='', book_active='', contact_active='', admin_active='')


@app.route('/administrator/logout')
def administrator_logout():
    session.pop('is_admin', None)
    return redirect(url_for('administrator_login'))


# ========== ADMINISTRATOR PAGE ==========
@app.route('/administrator')
def administrator():
    if not session.get('is_admin'):
        return redirect(url_for('administrator_login'))

    if not appointments:
        return render_template_string(SHARED_HEAD + """
        <div class="page-container">
            <div class="main-card">
                <h2>Administrator — Appointment Records</h2>
                <p>Office of the Registrar — SLSU JGE Tagkawayan College</p>
                <div class="empty-state">
                    <p style="font-size:1.1rem; color:#555; margin-bottom:0.5rem;">No appointment records found.</p>
                    <p style="font-size:0.9rem; color:#888;">Appointments submitted through the system will appear here.</p>
                </div>
                <a href="/" class="back-link">← Return to Homepage</a>
            </div>
        </div>
        """ + FOOTER, home_active='', services_active='', book_active='', contact_active='', admin_active='active')
    
    html_content = SHARED_HEAD + """
    <div class="page-container">
        <div class="main-card" style="max-width:900px;">
            <div class="admin-header">
                <div>
                    <h2>Administrator — Appointment Records</h2>
                    <p style="color:#666; font-size:0.85rem; margin-top:0.3rem;">Office of the Registrar — SLSU JGE Tagkawayan College</p>
                </div>
                <a href="/administrator/logout" class="btn btn-secondary btn-sm" style="width:auto;">Sign Out</a>
            </div>
            
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Reference Number</th>
                        <th>Full Name</th>
                        <th>Student ID</th>
                        <th>Service Requested</th>
                        <th>Appointment Schedule</th>
                        <th>Contact Information</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for record in appointments:
        html_content += f"""
                    <tr>
                        <td><strong>{escape(str(record['ref_num']))}</strong></td>
                        <td>{escape(str(record['fullname']))}</td>
                        <td>{escape(str(record['student_id']))}</td>
                        <td>{escape(str(record['purpose']))}</td>
                        <td>{escape(str(record['apt_date']))} — {escape(str(record['apt_time']))}</td>
                        <td>{escape(str(record['contact']))}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
            <p style="margin-top:1.5rem; font-size:0.8rem; color:#888; text-align:right;">
                Total Records: """ + str(len(appointments)) + """
            </p>
        </div>
    </div>
    """ + FOOTER
    
    return render_template_string(html_content, home_active='', services_active='', book_active='', contact_active='', admin_active='active')

# ========== APPOINTMENT SUBMISSION ==========
@app.route('/submit-appointment', methods=['POST'])
def submit_appointment():
    try:
        form_data = request.form
        current_datetime = datetime.now()
        date_prefix = current_datetime.strftime('%y%m%d')
        unique_suffix = str(uuid.uuid4())[:5].upper()
        reference_number = f"SLSU-TG-{date_prefix}-{unique_suffix}"
        
        new_appointment = {
            "ref_num": reference_number,
            "fullname": form_data.get('fullname'),
            "student_id": form_data.get('studentId'),
            "email": form_data.get('email'),
            "contact": form_data.get('contact'),
            "course": form_data.get('course'),
            "purpose": form_data.get('purpose'),
            "apt_date": form_data.get('aptDate'),
            "apt_time": form_data.get('aptTime'),
            "remarks": form_data.get('remarks', ''),
            "submitted_at": current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        appointments.append(new_appointment)
        
        print(f"\nNEW APPOINTMENT RECORD: {reference_number}")
        for key, value in new_appointment.items():
            print(f"  {key}: {value}")
        
        return jsonify({"success": True, "ref_num": reference_number})
    except Exception as error:
        print(f"SYSTEM ERROR: {str(error)}")
        return jsonify({"success": False, "message": "An error occurred. Please try again."}), 400

# ========== SERVER START ==========
if __name__ == '__main__':
    print("="*70)
    print("SOUTHERN LUZON STATE UNIVERSITY — JGE TAGKAWAYAN COLLEGE")
    print("OFFICE OF THE REGISTRAR — APPOINTMENT AND PAYMENT SYSTEM")
    print("="*70)
    print("System Status: ONLINE")
    print("Homepage:      http://127.0.0.1:5000")
    print("Administrator: http://127.0.0.1:5000/administrator")
    print("="*70)
    app.run(debug=True)