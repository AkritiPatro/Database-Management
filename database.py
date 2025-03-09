from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import secrets
print(secrets.token_hex(16))

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User class
class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already registered! Please login.', 'danger')
            return redirect(url_for('login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, username, email, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[3], password):
            login_user(User(user[0], user[1], user[2]))
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT subject, grade FROM grades WHERE user_id = %s", (current_user.id,))
    grades = cur.fetchall()
    cur.execute("SELECT id, filename FROM documents WHERE user_id = %s", (current_user.id,))
    documents = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', grades=grades, documents=documents)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file selected!', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file type!', 'danger')
        return redirect(url_for('dashboard'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO documents (user_id, filename, filepath) VALUES (%s, %s, %s)", (current_user.id, file.filename, filepath))
    mysql.connection.commit()
    cur.close()

    flash('File uploaded successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename, filepath FROM documents WHERE id = %s AND user_id = %s", (doc_id, current_user.id))
    doc = cur.fetchone()
    cur.close()
    
    if doc:
        return send_file(doc[1], as_attachment=True)
    else:
        flash('File not found!', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s, email = %s WHERE user_id = %s", (new_username, new_email, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('update_profile.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            mysql.connection.commit()
            cur.close()
            flash('Password reset successfully! Please log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email not found. Please enter a registered email.', 'danger')

    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
