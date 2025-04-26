from flask import Flask, render_template, request, redirect, session, g, send_file
import sqlite3
from datetime import datetime  # Correct import
from fpdf import FPDF
import click
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change to something secure
DATABASE = 'eco_data.db'

@app.route('/admin')
def admin_panel():
    if 'admin' not in session:
        return redirect('/admin-login')

    conn = sqlite3.connect('eco_data.db')
    c = conn.cursor()

    # Get all users
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()

    # Get all quiz responses
    c.execute('SELECT * FROM quiz_responses')
    responses = c.fetchall()

    conn.close()
    return render_template('admin.html', users=users, responses=responses)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded admin credentials (for demo only, use secure login in production)
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid admin credentials"

    return render_template('admin_login.html')

@app.cli.command("init-db")
@click.option('--admin', default='admin', help='Username to make admin')
def init_db_command(admin):
    """Initialize the database with admin flag"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    try:
        # Add admin column if needed
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]

        if 'admin' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN admin BOOLEAN DEFAULT 0")
            print("Added admin column")

        # Set admin user
        c.execute("UPDATE users SET admin = 1 WHERE username = ?", (admin,))

        if c.rowcount == 0:
            print(f"Warning: User '{admin}' not found")
        else:
            print(f"User '{admin}' is now an admin")

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

@app.route('/generate-report')
def generate_report():
    # Create PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="EcoTracker Monthly Report", ln=1, align='C')
    pdf.set_font("Arial", size=12)

    # Add date - FIXED: Using datetime.now() directly
    month_year = datetime.now().strftime("%B %Y")
    pdf.cell(200, 10, txt=f"Report for {month_year}", ln=1, align='C')
    pdf.ln(10)

    # Add user data (replace with actual data from your database)
    pdf.cell(200, 10, txt="Your Eco Score This Month: 85/100", ln=1)
    pdf.cell(200, 10, txt="Carbon Footprint Reduction: 12%", ln=1)
    pdf.ln(5)

    # Add comparison chart (placeholder)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="[Your monthly progress chart would appear here]", ln=1)
    pdf.ln(10)

    # Add achievements (without emoji)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Achievements Earned:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="- Reduced plastic usage by 30%", ln=1)
    pdf.cell(200, 10, txt="- Biked to work 15 days this month", ln=1)
    pdf.ln(10)

    # Add tips
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Tips for Next Month:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="- Try meatless Mondays to reduce food carbon footprint", ln=1)
    pdf.cell(200, 10, txt="- Unplug devices when not in use to save energy", ln=1)

    # Save to bytes buffer
    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin-1'))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"EcoTracker_Report_{month_year.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/donate')
def donate():
    return render_template('donate.html')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already exists"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/quiz')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        transport = request.form.get('transport')
        diet = request.form.get('diet')
        electricity = request.form.get('electricity')

        score = 0
        if transport == 'car': score += 5
        elif transport == 'bus': score += 3
        elif transport == 'bike': score += 1

        if diet == 'meat': score += 4
        elif diet == 'vegetarian': score += 2
        elif diet == 'vegan': score += 1

        if electricity == 'high': score += 5
        elif electricity == 'medium': score += 3
        elif electricity == 'low': score += 1

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_id = session['user_id']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO quiz_responses (transport, diet, electricity, score, user_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transport, diet, electricity, score, user_id, timestamp))
        conn.commit()
        conn.close()

        return render_template('result.html', score=score)

    return render_template('quiz.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    c = db.cursor()
    c.execute('''
        SELECT timestamp, score FROM quiz_responses
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (session['user_id'],))
    results = c.fetchall()
    return render_template('dashboard.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)