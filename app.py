from flask import Flask, render_template, request, redirect, flash, session
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = "gympro-secret-key-multi-tenant"

DB_NAME = "gym.db"

# -------- AUTHENTICATION UTILITIES --------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'gym_owner_id' not in session:
            flash("Please login to access this page", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# -------- DB UTILITIES --------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# -------- TABLES --------
def create_tables():
    with get_db() as db:
        # GYM OWNERS TABLE (NEW - Multi-tenant support)
        db.execute("""
        CREATE TABLE IF NOT EXISTS gym_owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_name TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            owner_name TEXT,
            phone TEXT,
            city TEXT,
            country TEXT,
            created_date TEXT,
            subscription_plan TEXT DEFAULT 'basic',
            is_active INTEGER DEFAULT 1
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_owner_id INTEGER NOT NULL,
            name TEXT,
            phone TEXT,
            email TEXT,
            join_date TEXT,
            start_weight REAL,
            status TEXT DEFAULT 'active',
            goal_type TEXT DEFAULT 'weight_loss',
            target_weight REAL,
            goal_deadline TEXT,
            FOREIGN KEY(gym_owner_id) REFERENCES gym_owners(id),
            UNIQUE(gym_owner_id, name)
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_owner_id INTEGER NOT NULL,
            member_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(gym_owner_id) REFERENCES gym_owners(id),
            UNIQUE(gym_owner_id, member_id, date)
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_owner_id INTEGER NOT NULL,
            member_id INTEGER,
            month TEXT,
            weight REAL,
            FOREIGN KEY(gym_owner_id) REFERENCES gym_owners(id)
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_owner_id INTEGER NOT NULL,
            member_id INTEGER,
            amount REAL,
            last_paid TEXT,
            next_due TEXT,
            paid_status TEXT DEFAULT 'pending',
            FOREIGN KEY(gym_owner_id) REFERENCES gym_owners(id)
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS profits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_owner_id INTEGER NOT NULL,
            member_id INTEGER,
            amount REAL,
            payment_date TEXT,
            fee_id INTEGER,
            FOREIGN KEY(gym_owner_id) REFERENCES gym_owners(id),
            UNIQUE(gym_owner_id, fee_id)
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS member_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gym_owner_id INTEGER NOT NULL,
            member_id INTEGER,
            goal_type TEXT,
            target_weight REAL,
            deadline TEXT,
            created_date TEXT,
            achieved INTEGER DEFAULT 0,
            FOREIGN KEY(gym_owner_id) REFERENCES gym_owners(id),
            UNIQUE(gym_owner_id, member_id)
        )""")
        db.commit()

create_tables()

# ========== AUTHENTICATION ROUTES ==========

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gym_name = request.form.get("gym_name", "").strip()
        password = request.form.get("password", "").strip()
        
        if not gym_name or not password:
            flash("Gym name and password are required", "error")
            return redirect("/login")
        
        with get_db() as db:
            gym_owner = db.execute(
                "SELECT * FROM gym_owners WHERE gym_name=?",
                (gym_name,)
            ).fetchone()
            
            if gym_owner and gym_owner['password'] == hash_password(password):
                session['gym_owner_id'] = gym_owner['id']
                session['gym_name'] = gym_owner['gym_name']
                session['owner_name'] = gym_owner['owner_name']
                flash(f"Welcome back, {gym_owner['owner_name']}!", "success")
                return redirect("/")
            else:
                flash("Invalid gym name or password", "error")
                return redirect("/login")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        gym_name = request.form.get("gym_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        
        # Validation
        if not all([gym_name, email, password, owner_name]):
            flash("All fields are required", "error")
            return redirect("/register")
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect("/register")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return redirect("/register")
        
        with get_db() as db:
            # Check if gym name or email already exists
            existing = db.execute(
                "SELECT * FROM gym_owners WHERE gym_name=? OR email=?",
                (gym_name, email)
            ).fetchone()
            
            if existing:
                flash("Gym name or email already registered", "error")
                return redirect("/register")
            
            try:
                cursor = db.execute("""
                    INSERT INTO gym_owners 
                    (gym_name, email, password, owner_name, created_date, subscription_plan, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    gym_name,
                    email,
                    hash_password(password),
                    owner_name,
                    datetime.now().strftime("%Y-%m-%d"),
                    "free",
                    1
                ))
                db.commit()
                gym_owner_id = cursor.lastrowid
                
                session['gym_owner_id'] = gym_owner_id
                session['gym_name'] = gym_name
                session['owner_name'] = owner_name
                
                flash("Account created successfully! Welcome to GymPro!", "success")
                return redirect("/")
            
            except sqlite3.IntegrityError as e:
                db.rollback()
                flash("Gym name or email already registered", "error")
                return redirect("/register")
            except Exception as e:
                db.rollback()
                flash(f"Registration error: {str(e)}", "error")
                return redirect("/register")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect("/login")

# ========== PROTECTED ROUTES START HERE ==========

# ---------------- HOME ----------------
@app.route("/")
@login_required
def index():
    today = datetime.now().strftime("%Y-%m-%d")
    gym_owner_id = session.get('gym_owner_id')

    with get_db() as db:
        members = db.execute(
            "SELECT * FROM members WHERE gym_owner_id=? AND status='active' ORDER BY name",
            (gym_owner_id,)
        ).fetchall()

        reminders = db.execute("""
            SELECT m.id, m.name, f.next_due, f.amount
            FROM fees f JOIN members m ON f.member_id=m.id
            WHERE m.gym_owner_id=? AND f.paid_status='pending'
            AND f.next_due BETWEEN date(?, '+2 day') AND date(?, '+3 day')
        """, (gym_owner_id, today, today)).fetchall()

        # Get total profits for this gym owner
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits WHERE gym_owner_id=?",
            (gym_owner_id,)
        ).fetchone()[0]

    return render_template("index.html",
                           members=members,
                           reminders=reminders,
                           total_profit=total_profit)

# ---------------- INACTIVE MEMBERS ----------------
@app.route("/inactive-members")
@login_required
def inactive_members():
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        inactive = db.execute(
            "SELECT * FROM members WHERE gym_owner_id=? AND status='inactive' ORDER BY name",
            (gym_owner_id,)
        ).fetchall()

    return render_template("inactive_members.html", inactive_members=inactive)

# ---------------- ADD MEMBER ----------------
@app.route("/add-member", methods=["POST"])
@login_required
def add_member():
    gym_owner_id = session.get('gym_owner_id')
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name is required", "error")
        return redirect("/")

    with get_db() as db:
        try:
            db.execute("""
                INSERT INTO members (gym_owner_id, name, phone, email, join_date, start_weight)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                gym_owner_id,
                name,
                request.form.get("phone"),
                request.form.get("email"),
                datetime.now().strftime("%Y-%m-%d"),
                request.form.get("weight", 0)
            ))
            flash("Member added successfully", "success")
        except sqlite3.IntegrityError:
            flash("Member already exists", "error")

    return redirect("/")

# ---------------- MEMBER PROFILE ----------------
@app.route("/member/<int:member_id>")
@login_required
def member_details(member_id):
    gym_owner_id = session.get('gym_owner_id')
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    with get_db() as db:
        member = db.execute(
            "SELECT * FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")

        attendance_data = db.execute("""
            SELECT status, COUNT(*) FROM attendance
            WHERE member_id=? AND gym_owner_id=? AND date>=?
            GROUP BY status
        """, (member_id, gym_owner_id, month_start)).fetchall()

        weight_logs = db.execute("""
            SELECT month, weight FROM weight_logs
            WHERE member_id=? AND gym_owner_id=? ORDER BY month DESC
        """, (member_id, gym_owner_id)).fetchall()

        fees = db.execute("""
            SELECT * FROM fees WHERE member_id=? AND gym_owner_id=?
            ORDER BY next_due DESC
        """, (member_id, gym_owner_id)).fetchall()

        recent_attendance = db.execute("""
            SELECT date, status FROM attendance
            WHERE member_id=? AND gym_owner_id=? ORDER BY date DESC LIMIT 10
        """, (member_id,)).fetchall()

        # Get member goal
        goal = db.execute("""
            SELECT goal_type, target_weight, deadline, achieved
            FROM member_goals WHERE member_id=?
        """, (member_id,)).fetchone()

    return render_template(
        "member_details.html",
        member=member,
        attendance_data=attendance_data,
        weight_logs=weight_logs,
        fees=fees,
        recent_attendance=recent_attendance,
        goal=goal
    )

# ---------------- MARK ATTENDANCE ----------------
@app.route("/attendance/<int:member_id>", methods=["GET", "POST"])
@login_required
def attendance(member_id):
    gym_owner_id = session.get('gym_owner_id')
    today = datetime.now().strftime("%Y-%m-%d")

    if datetime.now().weekday() == 6:
        flash("Sunday is holiday 💤", "info")
        return redirect("/")

    if request.method == "POST":
        status = request.form.get("status", "Present")

        with get_db() as db:
            # Verify member belongs to this gym owner
            member = db.execute(
                "SELECT id FROM members WHERE id=? AND gym_owner_id=?",
                (member_id, gym_owner_id)
            ).fetchone()
            
            if not member:
                flash("Member not found", "error")
                return redirect("/")
            
            try:
                db.execute("""
                    INSERT INTO attendance (member_id, gym_owner_id, date, status)
                    VALUES (?, ?, ?, ?)
                """, (member_id, gym_owner_id, today, status))
                flash("Attendance marked", "success")
            except sqlite3.IntegrityError:
                flash("Attendance already marked today", "error")

        return redirect("/")

    with get_db() as db:
        member = db.execute(
            "SELECT name FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")

    return render_template(
        "mark_attendance.html",
        member_name=member["name"]
    )

# ---------------- ADD WEIGHT ----------------
@app.route("/add-weight", methods=["POST"])
@login_required
def add_weight():
    gym_owner_id = session.get('gym_owner_id')
    member_id = request.form.get("member_id")
    weight = request.form.get("weight")
    
    if not member_id or not weight:
        flash("Invalid weight data", "error")
        return redirect(f"/member/{member_id}")
    
    try:
        weight = float(weight)
    except ValueError:
        flash("Invalid weight value", "error")
        return redirect(f"/member/{member_id}")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    with get_db() as db:
        # Verify member belongs to this gym owner
        member = db.execute(
            "SELECT id FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")
        
        db.execute("""
            INSERT INTO weight_logs (member_id, gym_owner_id, month, weight)
            VALUES (?, ?, ?, ?)
        """, (member_id, gym_owner_id, today, weight))

    flash("Weight updated successfully 💪", "success")
    return redirect(f"/member/{member_id}")

# ---------------- ADD FEES ----------------
@app.route("/add-fees", methods=["POST"])
@login_required
def add_fees():
    gym_owner_id = session.get('gym_owner_id')
    member_id = request.form.get("member_id")
    amount = request.form.get("amount")

    if not member_id or not amount:
        flash("Invalid fee data", "error")
        return redirect("/")

    try:
        amount = float(amount)
    except ValueError:
        flash("Invalid amount", "error")
        return redirect("/")

    last_paid = datetime.now()
    next_due = last_paid + timedelta(days=30)

    with get_db() as db:
        # Verify member belongs to this gym owner
        member = db.execute(
            "SELECT id FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")
        
        db.execute("""
            INSERT INTO fees (member_id, gym_owner_id, amount, last_paid, next_due, paid_status)
            VALUES (?, ?, ?, ?, ?, 'paid')
        """, (
            member_id,
            gym_owner_id,
            amount,
            last_paid.strftime("%Y-%m-%d"),
            next_due.strftime("%Y-%m-%d")
        ))

        # Get the fee id that was just inserted (using gym_owner_id for isolation)
        fee_id = db.execute(
            "SELECT id FROM fees WHERE member_id=? AND gym_owner_id=? ORDER BY id DESC LIMIT 1",
            (member_id, gym_owner_id)
        ).fetchone()[0]

        # Add to profits
        db.execute("""
            INSERT INTO profits (member_id, gym_owner_id, amount, payment_date, fee_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            member_id,
            gym_owner_id,
            amount,
            last_paid.strftime("%Y-%m-%d"),
            fee_id
        ))

    flash("Fee added successfully 💰", "success")
    return redirect(f"/member/{member_id}")

# ---------------- MARK FEE AS PAID ----------------
@app.route("/pay-fees/<int:member_id>", methods=["POST"])
@login_required
def pay_fees(member_id):
    gym_owner_id = session.get('gym_owner_id')
    today = datetime.now()

    with get_db() as db:
        # Verify member belongs to this gym owner
        member = db.execute(
            "SELECT id FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")
        
        # Get the pending fee to be marked as paid
        fee = db.execute("""
            SELECT id, amount FROM fees
            WHERE member_id = ? AND gym_owner_id = ? AND paid_status = 'pending'
            ORDER BY next_due DESC
            LIMIT 1
        """, (member_id, gym_owner_id)).fetchone()

        if fee:
            fee_id, amount = fee[0], fee[1]
            
            # Update the fee status
            db.execute("""
                UPDATE fees
                SET paid_status = 'paid', last_paid = ?
                WHERE id = ? AND gym_owner_id = ?
            """, (today.strftime("%Y-%m-%d"), fee_id, gym_owner_id))

            # Add to profits
            db.execute("""
                INSERT OR IGNORE INTO profits (member_id, gym_owner_id, amount, payment_date, fee_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                member_id,
                gym_owner_id,
                amount,
                today.strftime("%Y-%m-%d"),
                fee_id
            ))

    flash("Fee marked as paid ✅", "success")
    return redirect(f"/member/{member_id}")


# ---------------- FEES DASHBOARD ----------------
@app.route("/fees")
@login_required
def fees_dashboard():
    gym_owner_id = session.get('gym_owner_id')
    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as db:
        pending_fees = db.execute("""
            SELECT f.id, m.id, m.name, f.amount, f.next_due
            FROM fees f JOIN members m ON f.member_id=m.id
            WHERE f.gym_owner_id=? AND f.paid_status='pending'
        """, (gym_owner_id,)).fetchall()

        # Get total profit data for this gym owner
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits WHERE gym_owner_id=?",
            (gym_owner_id,)
        ).fetchone()[0]

        profit_entries = db.execute("""
            SELECT m.name, p.amount, p.payment_date
            FROM profits p JOIN members m ON p.member_id=m.id
            WHERE p.gym_owner_id=?
            ORDER BY p.payment_date DESC
            LIMIT 20
        """, (gym_owner_id,)).fetchall()

    overdue_count = sum(1 for f in pending_fees if f["next_due"] < today)

    return render_template(
        "fees.html",
        pending_fees=pending_fees,
        overdue_count=overdue_count,
        total_profit=total_profit,
        profit_entries=profit_entries
    )

# ---------------- PROFITS DASHBOARD ----------------
@app.route("/profits")
@login_required
def profits_dashboard():
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits WHERE gym_owner_id=?",
            (gym_owner_id,)
        ).fetchone()[0]

        profit_entries = db.execute("""
            SELECT m.name, p.amount, p.payment_date
            FROM profits p JOIN members m ON p.member_id=m.id
            WHERE p.gym_owner_id=?
            ORDER BY p.payment_date DESC
        """, (gym_owner_id,)).fetchall()

        # Get profit by member for this gym owner
        profit_by_member = db.execute("""
            SELECT m.name, COUNT(*) as payments, SUM(p.amount) as total_amount
            FROM profits p JOIN members m ON p.member_id=m.id
            WHERE p.gym_owner_id=?
            GROUP BY p.member_id
            ORDER BY total_amount DESC
        """, (gym_owner_id,)).fetchall()

    return render_template(
        "profits.html",
        total_profit=total_profit,
        profit_entries=profit_entries,
        profit_by_member=profit_by_member
    )

# ---------------- REMOVE MEMBER ----------------
@app.route("/remove-member/<int:member_id>", methods=["POST"])
@login_required
def remove_member(member_id):
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        # Get member name before marking inactive, verify ownership
        member = db.execute(
            "SELECT name FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if member:
            # Mark member as inactive instead of deleting
            db.execute(
                "UPDATE members SET status='inactive' WHERE id=? AND gym_owner_id=?",
                (member_id, gym_owner_id)
            )
            flash(f"Member '{member['name']}' has been removed from the gym", "success")
        else:
            flash("Member not found", "error")
    
    return redirect("/")

# ---------------- REACTIVATE MEMBER ----------------
@app.route("/reactivate-member/<int:member_id>", methods=["POST"])
@login_required
def reactivate_member(member_id):
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        # Get member name before reactivation, verify ownership
        member = db.execute(
            "SELECT name FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if member:
            # Mark member as active again
            db.execute(
                "UPDATE members SET status='active' WHERE id=? AND gym_owner_id=?",
                (member_id, gym_owner_id)
            )
            flash(f"Member '{member['name']}' has been reactivated", "success")
        else:
            flash("Member not found", "error")
    
    return redirect("/inactive-members")

# ---------------- SET MEMBER GOAL ----------------
@app.route("/set-goal/<int:member_id>", methods=["POST"])
@login_required
def set_goal(member_id):
    gym_owner_id = session.get('gym_owner_id')
    goal_type = request.form.get("goal_type")
    target_weight = request.form.get("target_weight")
    deadline = request.form.get("deadline")
    
    if not goal_type or not target_weight or not deadline:
        flash("All goal fields are required", "error")
        return redirect(f"/member/{member_id}")
    
    try:
        target_weight = float(target_weight)
    except ValueError:
        flash("Invalid target weight", "error")
        return redirect(f"/member/{member_id}")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    with get_db() as db:
        # Verify member belongs to this gym owner
        member = db.execute(
            "SELECT id FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")
        
        # Check if goal already exists
        existing_goal = db.execute(
            "SELECT id FROM member_goals WHERE member_id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if existing_goal:
            # Update existing goal
            db.execute("""
                UPDATE member_goals
                SET goal_type=?, target_weight=?, deadline=?
                WHERE member_id=? AND gym_owner_id=?
            """, (goal_type, target_weight, deadline, member_id, gym_owner_id))
            flash("Goal updated successfully 🎯", "success")
        else:
            # Create new goal
            db.execute("""
                INSERT INTO member_goals (member_id, gym_owner_id, goal_type, target_weight, deadline, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (member_id, gym_owner_id, goal_type, target_weight, deadline, today))
            flash("Goal set successfully 🎯", "success")
    
    return redirect(f"/member/{member_id}")

# ---------------- GOALS DASHBOARD ----------------
@app.route("/goals")
@login_required
def goals_dashboard():
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        # Get all members with their goals for this gym owner
        members_with_goals = db.execute("""
            SELECT m.id, m.name, m.start_weight, mg.goal_type, mg.target_weight, mg.deadline
            FROM members m
            LEFT JOIN member_goals mg ON m.id = mg.member_id AND m.gym_owner_id = mg.gym_owner_id
            WHERE m.gym_owner_id=? AND m.status = 'active'
            ORDER BY m.name
        """, (gym_owner_id,)).fetchall()
        
        # Get goal statistics for this gym owner
        total_goals = db.execute(
            "SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND achieved=0",
            (gym_owner_id,)
        ).fetchone()[0]
        
        achieved_goals = db.execute(
            "SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND achieved=1",
            (gym_owner_id,)
        ).fetchone()[0]
        
        # Get members by goal type for this gym owner
        weight_loss_members = db.execute("""
            SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND goal_type='weight_loss' AND achieved=0
        """, (gym_owner_id,)).fetchone()[0]
        
        weight_gain_members = db.execute("""
            SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND goal_type='weight_gain' AND achieved=0
        """, (gym_owner_id,)).fetchone()[0]
    
    return render_template(
        "goals.html",
        members_with_goals=members_with_goals,
        total_goals=total_goals,
        achieved_goals=achieved_goals,
        weight_loss_members=weight_loss_members,
        weight_gain_members=weight_gain_members
    )

# -------- LEADERBOARD ROUTE --------
@app.route("/leaderboard")
@login_required
def leaderboard():
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        # Get all members with goal progress for this gym owner
        members = db.execute("""
            SELECT m.*, 
                   COUNT(CASE WHEN a.status='present' THEN 1 END) as attendance_count,
                   ROUND(AVG(CASE WHEN wl.weight IS NOT NULL THEN wl.weight END), 1) as current_weight
            FROM members m
            LEFT JOIN attendance a ON m.id = a.member_id AND a.gym_owner_id = ?
            LEFT JOIN weight_logs wl ON m.id = wl.member_id AND wl.gym_owner_id = ?
            WHERE m.gym_owner_id=? AND m.status='active'
            GROUP BY m.id
            ORDER BY attendance_count DESC
        """, (gym_owner_id, gym_owner_id, gym_owner_id)).fetchall()
        
        # Calculate progress for each member
        leaderboard_data = []
        for member in members:
            goal = db.execute(
                "SELECT * FROM member_goals WHERE member_id=? AND gym_owner_id=?", 
                (member['id'], gym_owner_id)
            ).fetchone()
            
            progress = 0
            if goal and member['current_weight']:
                if goal['goal_type'] == 'weight_loss':
                    progress = max(0, min(100, ((member['start_weight'] - member['current_weight']) / (member['start_weight'] - goal['target_weight']) * 100))) if (member['start_weight'] - goal['target_weight']) != 0 else 0
                else:  # weight_gain
                    progress = max(0, min(100, ((member['current_weight'] - member['start_weight']) / (goal['target_weight'] - member['start_weight']) * 100))) if (goal['target_weight'] - member['start_weight']) != 0 else 0
            
            leaderboard_data.append({
                'member': member,
                'attendance': member['attendance_count'] or 0,
                'goal': goal,
                'progress': round(progress)
            })
        
        # Sort by attendance + progress
        leaderboard_data.sort(key=lambda x: (x['attendance'], x['progress']), reverse=True)
        
    return render_template("leaderboard.html", leaderboard=leaderboard_data)

# -------- STATISTICS ROUTE --------
@app.route("/statistics")
@login_required
def statistics():
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        # Overall stats for this gym owner
        total_members = db.execute(
            "SELECT COUNT(*) FROM members WHERE gym_owner_id=? AND status='active'",
            (gym_owner_id,)
        ).fetchone()[0]
        
        total_attended = db.execute(
            "SELECT COUNT(DISTINCT member_id) FROM attendance WHERE gym_owner_id=?",
            (gym_owner_id,)
        ).fetchone()[0]
        
        avg_attendance = db.execute(
            "SELECT ROUND(AVG(attendance_count)) FROM (SELECT COUNT(*) as attendance_count FROM attendance WHERE gym_owner_id=? GROUP BY member_id)",
            (gym_owner_id,)
        ).fetchone()[0] or 0
        
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits WHERE gym_owner_id=?",
            (gym_owner_id,)
        ).fetchone()[0]
        
        # Goal stats
        active_goals = db.execute(
            "SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND achieved=0",
            (gym_owner_id,)
        ).fetchone()[0]
        
        achieved_goals = db.execute(
            "SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND achieved=1",
            (gym_owner_id,)
        ).fetchone()[0]
        
        goal_completion_rate = (achieved_goals / (active_goals + achieved_goals) * 100) if (active_goals + achieved_goals) > 0 else 0
        
        # Weight stats
        weight_loss_count = db.execute(
            "SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND goal_type='weight_loss' AND achieved=0",
            (gym_owner_id,)
        ).fetchone()[0]
        
        weight_gain_count = db.execute(
            "SELECT COUNT(*) FROM member_goals WHERE gym_owner_id=? AND goal_type='weight_gain' AND achieved=0",
            (gym_owner_id,)
        ).fetchone()[0]
        
        # Top members by attendance for this gym owner
        top_members = db.execute("""
            SELECT m.name, COUNT(a.id) as count
            FROM members m
            LEFT JOIN attendance a ON m.id = a.member_id AND a.gym_owner_id = ?
            WHERE m.gym_owner_id=? AND m.status='active'
            GROUP BY m.id
            ORDER BY count DESC
            LIMIT 5
        """, (gym_owner_id, gym_owner_id)).fetchall()
        
    return render_template(
        "statistics.html",
        total_members=total_members,
        total_attended=total_attended,
        avg_attendance=avg_attendance,
        total_profit=total_profit,
        active_goals=active_goals,
        achieved_goals=achieved_goals,
        goal_completion_rate=round(goal_completion_rate, 1),
        weight_loss_count=weight_loss_count,
        weight_gain_count=weight_gain_count,
        top_members=top_members
    )

# -------- MEMBER SEARCH ROUTE --------
@app.route("/search")
@login_required
def search():
    gym_owner_id = session.get('gym_owner_id')
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        with get_db() as db:
            results = db.execute(
                "SELECT * FROM members WHERE gym_owner_id=? AND (name LIKE ? OR phone LIKE ? OR email LIKE ?) ORDER BY name",
                (gym_owner_id, f'%{query}%', f'%{query}%', f'%{query}%')
            ).fetchall()
    
    return render_template("search.html", query=query, results=results)

# -------- ACHIEVEMENT ROUTE --------
@app.route("/achievement/<int:member_id>")
@login_required
def mark_achievement(member_id):
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        # Verify member belongs to this gym owner before marking achievement
        member = db.execute(
            "SELECT id FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")
        
        # Mark goal as achieved
        db.execute(
            "UPDATE member_goals SET achieved=1 WHERE member_id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        )
        db.commit()
    
    flash(f"🎉 Goal achievement recorded! Congratulations!", "success")
    return redirect(f"/member/{member_id}")

# -------- MEMBER INSIGHTS ROUTE --------
@app.route("/insights/<int:member_id>")
@login_required
def member_insights(member_id):
    gym_owner_id = session.get('gym_owner_id')
    
    with get_db() as db:
        member = db.execute(
            "SELECT * FROM members WHERE id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        if not member:
            flash("Member not found", "error")
            return redirect("/")
        
        # Attendance trend (last 30 days) for this gym owner
        attendance_data = db.execute("""
            SELECT date, status FROM attendance 
            WHERE member_id=? AND gym_owner_id=? AND date >= date('now', '-30 days')
            ORDER BY date DESC
        """, (member_id, gym_owner_id)).fetchall()
        
        # Weight trend for this gym owner
        weight_data = db.execute("""
            SELECT month, weight FROM weight_logs 
            WHERE member_id=? AND gym_owner_id=?
            ORDER BY month DESC 
            LIMIT 12
        """, (member_id, gym_owner_id)).fetchall()
        
        # Goal info for this gym owner
        goal = db.execute(
            "SELECT * FROM member_goals WHERE member_id=? AND gym_owner_id=?",
            (member_id, gym_owner_id)
        ).fetchone()
        
        # Fees summary for this gym owner
        fees_paid = db.execute(
            "SELECT COALESCE(COUNT(*), 0) FROM fees WHERE member_id=? AND gym_owner_id=? AND paid_status='paid'",
            (member_id, gym_owner_id)
        ).fetchone()[0]
        
        # Calculate stats
        attendance_percent = (len([a for a in attendance_data if a['status'] == 'present']) / len(attendance_data) * 100) if attendance_data else 0
        
    return render_template(
        "insights.html",
        member=member,
        goal=goal,
        attendance_data=attendance_data,
        weight_data=weight_data,
        attendance_percent=round(attendance_percent),
        fees_paid=fees_paid
    )

# -------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)