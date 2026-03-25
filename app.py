from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# DB create
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

    # ADMIN LOGIN
    if admin_user and admin_pass:
        if admin_user == "admin" and admin_pass == "123":
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return "Wrong Admin Credentials"

    # STUDENT LOGIN
    return redirect('/register')

# -------- REGISTER PAGE --------
@app.route('/register')
def register():
    return render_template('register.html')

# -------- SUBMIT --------
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    class_name = request.form['class']
    section = request.form['section']
    roll = request.form['roll']
    event = request.form['event']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
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


if __name__ == '__main__':
    app.run(debug=True)