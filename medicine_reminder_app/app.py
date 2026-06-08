from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reminder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# -------------------
# MODELS
# -------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)


class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medicine_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    time = db.Column(db.String(20))
    medicine_date = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Pending")
    notes = db.Column(db.Text)

    # NEW FIELDS (IMPORTANT UPGRADE)
    reminder_sent = db.Column(db.Boolean, default=False)
    last_sent_time = db.Column(db.String(50))


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    action = db.Column(db.String(50))

    medicine_name = db.Column(db.String(100))

    dosage = db.Column(db.String(50))

    medicine_time = db.Column(db.String(20))

    medicine_date = db.Column(db.String(50))

    notes = db.Column(db.Text)

    action_time = db.Column(
        db.String(50),
        default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


def add_log(user_id, action):

    log = ActivityLog(
        user_id=user_id,
        action=action
    )

    db.session.add(log)
    db.session.commit()


def add_history(
    user_id,
    action,
    medicine_name,
    dosage="",
    medicine_time="",
    medicine_date="",
    notes=""
):

    history = History(
        user_id=user_id,
        action=action,
        medicine_name=medicine_name,
        dosage=dosage,
        medicine_time=medicine_time,
        medicine_date=medicine_date,
        notes=notes
    )

    db.session.add(history)
    db.session.commit()
# -------------------
# LOGIN REQUIRED
# -------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# -------------------
# HOME
# -------------------

@app.route("/")
def home():
    return redirect(url_for("login"))


# -------------------
# REGISTER
# -------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password required")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)

        user = User(username=username, email=email, phone=phone, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login")
        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------
# LOGIN
# -------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user"] = user.username
            add_log(
                user.id,
                "Logged In"
            )
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")
        return redirect(url_for("login"))

    return render_template("login.html")

#-----------------------
# forgot password
#-----------------------


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()

        user = User.query.filter_by(email=email).first()

        if user:

            token = serializer.dumps(
                user.email,
                salt='password-reset'
            )

            reset_link = url_for(
                'reset_password',
                token=token,
                _external=True
            )

            msg = Message(
                'Reset Your Password',
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]
            )

            msg.body = f"""
Hello {user.username},

Click the link below to reset your password:

{reset_link}

This link expires in 30 minutes.
"""

            mail.send(msg)

        flash("If the email exists, a reset link has been sent.")
        return redirect(url_for('login'))

    return render_template('forgot_password.html')


#----------------------
# reset password
#----------------------


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    try:
        email = serializer.loads(
            token,
            salt='password-reset',
            max_age=1800
        )

    except Exception:
        flash("Invalid or expired reset link")
        return redirect(url_for('login'))

    if request.method == 'POST':

        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:

            user.password = generate_password_hash(password)

            db.session.commit()

            flash("Password reset successful")
            return redirect(url_for('login'))

    return render_template(
        'reset_password.html',
        token=token
    )


# -------------------
# DASHBOARD
# -------------------

@app.route("/dashboard")
@login_required
def dashboard():
    meds = Medicine.query.filter_by(user_id=session["user_id"]).all()
    return render_template(
    "dashboard.html",
    username=session.get("user"),
    medicines=meds)


# -------------------
# ADD MEDICINE
# -------------------

@app.route("/add", methods=["POST"])
@login_required
def add():
    med = Medicine(
        user_id=session["user_id"],
        medicine_name=request.form.get("medicine"),
        dosage=request.form.get("dose"),
        time=request.form.get("time"),
        medicine_date=request.form.get("date"),
        notes=request.form.get("notes")
    )

    db.session.add(med)
    db.session.commit()

    add_history(
        session["user_id"],
        "Added",
        med.medicine_name,
        med.dosage,
        med.time,
        med.medicine_date,
        med.notes
    )

    add_log(
        session["user_id"],
        f"Added Medicine: {med.medicine_name} | Notes: {med.notes}"
    )

    flash("Medicine added")
    return redirect(url_for("dashboard"))


#---------------------------
# History
#---------------------------

@app.route("/history")
@login_required
def history():

    records = History.query.filter_by(
        user_id=session["user_id"]
    ).order_by(History.id.desc()).all()

    return render_template(
        "history.html",
        records=records
    )


#------------------
# Delete and Clear History
#------------------

@app.route('/delete_history/<int:id>')
@login_required
def delete_history(id):

    history = History.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if not history:
        flash("History record not found")
        return redirect(url_for('history'))

    db.session.delete(history)
    db.session.commit()

    flash("History record deleted successfully")

    return redirect(url_for('history'))


@app.route('/clear_history')
@login_required
def clear_history():

    History.query.filter_by(
        user_id=session["user_id"]
    ).delete()

    db.session.commit()

    add_log(
        session["user_id"],
        "Cleared History"
    )

    flash("All history cleared successfully")

    return redirect(url_for('history'))
#-------------------------
# Taken
#-------------------------


@app.route("/taken/<int:id>")
@login_required
def taken(id):

    med = Medicine.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if not med:
        flash("Medicine not found")
        return redirect(url_for("dashboard"))

    # Prevent duplicate clicks
    if med.status == "Taken":
        flash("Medicine already marked as taken")
        return redirect(url_for("dashboard"))

    # Update medicine status
    med.status = "Taken"

    # Save to history
    add_history(
        session["user_id"],
        "Taken",
        med.medicine_name,
        med.dosage,
        med.time,
        med.medicine_date,
        med.notes
    )


    db.session.commit()
    add_log(session["user_id"],f"Marked Taken: {med.medicine_name} | Notes: {med.notes}")

    flash("Medicine marked as taken successfully")
    return redirect(url_for("dashboard"))

#----------------------
# Edit
#----------------------

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):

    med = Medicine.query.filter_by(
        id=id,
        user_id=session['user_id']
    ).first()

    if not med:
        flash("Medicine not found")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        med.medicine_name = request.form.get('medicine', '').strip()
        med.dosage = request.form.get('dose', '').strip()
        med.time = request.form.get('time')
        med.medicine_date = request.form.get('date')
        med.notes = request.form.get("notes")

        # Reset reminder if medicine schedule changed
        med.status = "Pending"

        # If you added these fields for reminders
        if hasattr(med, 'reminder_sent'):
            med.reminder_sent = False

        if hasattr(med, 'last_sent_time'):
            med.last_sent_time = None
        

        add_history(session["user_id"],"Edited",med.medicine_name,
                    med.dosage,med.time,med.medicine_date,med.notes)

        db.session.commit()

        add_log(
            session["user_id"],
            f"Edited Medicine: {med.medicine_name} | Notes: {med.notes}"
        )
        flash("Medicine updated successfully")
        return redirect(url_for('dashboard'))

    return render_template(
        'edit.html',
        med=med
    )


# -------------------
# DELETE
# -------------------

@app.route("/delete/<int:id>")
@login_required
def delete(id):

    med = Medicine.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if med:

        add_log(
            session["user_id"],
            f"Deleted Medicine: {med.medicine_name} | Notes: {med.notes}"
        )

        add_history(
            session["user_id"],
            "Deleted",
            med.medicine_name,
            med.dosage,
            med.time,
            med.medicine_date,
            med.notes
        )

        db.session.delete(med)
        db.session.commit()

    return redirect(url_for("dashboard"))
#----------------------
# Logs
#----------------------


@app.route("/logs")
@login_required
def logs():

    logs = ActivityLog.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        ActivityLog.timestamp.desc()
    ).all()

    return render_template(
        "logs.html",
        logs=logs
    )


#--------------------------
# Analytics
#--------------------------

@app.route("/analytics")
@login_required
def analytics():
    total = Medicine.query.filter_by(
        user_id=session["user_id"]
    ).count()

    taken = Medicine.query.filter_by(
        user_id=session["user_id"],
        status="Taken"
    ).count()

    pending = Medicine.query.filter_by(
        user_id=session["user_id"],
        status="Pending"
    ).count()

    percent = int((taken / total) * 100) if total > 0 else 0

    return render_template(
        "analytics.html",
        total=total,
        taken=taken,
        pending=pending,
        percent=percent
    )

def send_email(to_email, medicine_name):
    try:
        msg = Message(
            subject="💊 Medicine Reminder",
            sender=app.config['MAIL_USERNAME'],
            recipients=[to_email]
        )
        msg.body = f"Time to take your medicine: {medicine_name}"
        mail.send(msg)
        return True
    except Exception as e:
        print("[EMAIL ERROR]", e)
        return False
    
def send_sms(phone, medicine_name):
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

        client.messages.create(
            body=f"💊 Take your medicine: {medicine_name}",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=phone
        )
        return True
    except Exception as e:
        print("[SMS ERROR]", e)
        return False
    
def check_reminders():
    with app.app_context():

        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        medicines = Medicine.query.filter_by(
            status="Pending",
            medicine_date=current_date,
            time=current_time
        ).all()

        for med in medicines:

            # 🚨 prevent duplicate sending
            if med.reminder_sent:
                continue

            user = db.session.get(User, med.user_id)

            if user:
                email_ok = send_email(user.email, med.medicine_name)
                sms_ok = True

                if user.phone:
                    sms_ok = send_sms(user.phone, med.medicine_name)

                # mark only if at least one succeeded
                if email_ok or sms_ok:
                    med.reminder_sent = True
                    med.last_sent_time = current_time
                    med.status = "Reminder Sent"

                    db.session.commit()

                    print(f"Reminder sent → {user.email}")


# -------------------
# LOGOUT
# -------------------

@app.route("/logout")
def logout():

    if "user_id" in session:

        add_log(
            session["user_id"],
            "Logged Out"
        )

    session.clear()

    flash("Logged out successfully")

    return redirect(
        url_for("login")
    )


# -------------------
# RUN APP
# -------------------

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_reminders, "interval", minutes=1)
    scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    start_scheduler()
    app.run(debug=True)