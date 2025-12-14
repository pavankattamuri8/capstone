from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3, os, datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['DATABASE'] = 'database.db'
app.secret_key = 'change_this_secret'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db_conn():
    return sqlite3.connect(app.config['DATABASE'])
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if len(password) < 6:
            return "Password must be at least 6 characters"

        conn = get_db_conn()
        try:
            conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                         (name, email, generate_password_hash(password)))
            conn.commit()
        except:
            return "Email already registered"
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db_conn()
        user = conn.execute("SELECT id,name,email,password FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect('/')


@app.route('/')
def index():
    conn = get_db_conn()
    jobs = conn.execute("SELECT id,title,type,description FROM jobs").fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

@app.route('/apply/<int:job_id>')
def apply(job_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('apply.html', job_id=job_id)


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name','').strip()
    email = request.form.get('email','').strip()
    job_id = request.form.get('job_id')
    f = request.files.get('resume')
    filename = None
    if f and f.filename:
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    score = 0
    conn = get_db_conn()
    conn.execute("INSERT INTO applications (job_id,name,email,resume_file,timestamp,match_score) VALUES (?,?,?,?,?,?)",
                 (job_id,name,email,filename,t,score))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username','')
        p = request.form.get('password','')
        if u=='admin' and p=='admin':
            session['admin'] = True
            return redirect(url_for('admin_dash'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return fn(*a, **kw)
    return wrapper

@app.route('/admin/dashboard')
@admin_required
def admin_dash():
    conn = get_db_conn()
    jobs = conn.execute("SELECT id,title,type,description FROM jobs").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', jobs=jobs)

@app.route('/admin/job/<int:job_id>')
@admin_required
def admin_job(job_id):
    conn = get_db_conn()
    apps = conn.execute("SELECT id,job_id,name,email,resume_file,timestamp,match_score FROM applications WHERE job_id=? ORDER BY timestamp DESC",(job_id,)).fetchall()
    conn.close()
    return render_template('admin_applicants.html', apps=apps)

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
