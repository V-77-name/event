from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# -------- DB CREATE --------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            class TEXT,
            section TEXT,
            roll TEXT,
            event TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------- LOGIN PAGE --------
@app.route('/')
def login():
    return render_template('login.html')

# -------- LOGIN LOGIC --------
@app.route('/login', methods=['POST'])
def do_login():

    admin_user = request.form.get('admin_user')
    admin_pass = request.form.get('admin_pass')

    student_id = request.form.get('id')
    roll = request.form.get('roll')

    # -------- ADMIN LOGIN --------
    if admin_user and admin_pass:
        if admin_user == "admin" and admin_pass == "123":
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return "❌ Wrong Admin Credentials"

    # -------- STUDENT VALIDATION --------
    if student_id:
        if not student_id.isalnum():
            return "❌ College ID must contain only letters and numbers"

    if roll:
        if not roll.isdigit():
            return "❌ Roll number must be numeric only"

    return redirect('/register')

# -------- REGISTER PAGE --------
@app.route('/register')
def register():
    return render_template('register.html')

# -------- SUBMIT WITH VALIDATION --------
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    class_name = request.form['class']
    section = request.form['section']
    roll = request.form['roll']
    event = request.form['event']

    # -------- VALIDATIONS --------

    # Class (1–12 only)
    if not class_name.isdigit() or int(class_name) < 1 or int(class_name) > 12:
        return "❌ Class must be between 1 and 12 only"

    # Section (A/B/C/D only)
    if section not in ['A', 'B', 'C', 'D']:
        return "❌ Section must be A, B, C or D only"

    # Roll must be number
    if not roll.isdigit():
        return "❌ Roll number must be numeric only"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # -------- DUPLICATE CHECK --------
    c.execute("SELECT * FROM registrations WHERE roll=? AND event=?", (roll, event))
    existing = c.fetchone()

    if existing:
        conn.close()
        return "❌ You already registered for this event"

    # -------- INSERT --------
    c.execute(
        "INSERT INTO registrations (name, class, section, roll, event) VALUES (?, ?, ?, ?, ?)",
        (name, class_name, section, roll, event)
    )
    conn.commit()
    conn.close()

    return render_template('success.html')

# -------- ADMIN DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registrations")
    data = c.fetchall()
    conn.close()

    return render_template('admin.html', data=data)

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

# -------- RUN --------
if __name__ == '__main__':
    app.run(debug=True)