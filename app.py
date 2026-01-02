from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "gympro-secret-key"

DB_NAME = "gym.db"

# ---------------- DB UTILS ----------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- TABLES ----------------
def create_tables():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            email TEXT,
            join_date TEXT,
            start_weight REAL,
            status TEXT DEFAULT 'active'
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            date TEXT,
            status TEXT,
            UNIQUE(member_id, date)
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            month TEXT,
            weight REAL
        )""")

        db.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            amount REAL,
            last_paid TEXT,
            next_due TEXT,
            paid_status TEXT DEFAULT 'pending'
        )""")

create_tables()

# ---------------- HOME ----------------
@app.route("/")
def index():
    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as db:
        members = db.execute(
            "SELECT * FROM members WHERE status='active' ORDER BY name"
        ).fetchall()

        reminders = db.execute("""
            SELECT m.id, m.name, f.next_due, f.amount
            FROM fees f JOIN members m ON f.member_id=m.id
            WHERE f.paid_status='pending'
            AND f.next_due BETWEEN date(?, '+2 day') AND date(?, '+3 day')
        """, (today, today)).fetchall()

        overdue = db.execute("""
            SELECT m.id, m.name, f.next_due, f.amount
            FROM fees f JOIN members m ON f.member_id=m.id
            WHERE f.paid_status='pending' AND f.next_due < ?
        """, (today,)).fetchall()

    return render_template("index.html",
                           members=members,
                           reminders=reminders,
                           overdue=overdue)

# ---------------- ADD MEMBER ----------------
@app.route("/add-member", methods=["POST"])
def add_member():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name is required", "error")
        return redirect("/")

    with get_db() as db:
        try:
            db.execute("""
                INSERT INTO members (name, phone, email, join_date, start_weight)
                VALUES (?, ?, ?, ?, ?)
            """, (
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
def member_details(member_id):
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    with get_db() as db:
        member = db.execute(
            "SELECT * FROM members WHERE id=?", (member_id,)
        ).fetchone()

        attendance_data = db.execute("""
            SELECT status, COUNT(*) FROM attendance
            WHERE member_id=? AND date>=?
            GROUP BY status
        """, (member_id, month_start)).fetchall()

        weight_logs = db.execute("""
            SELECT month, weight FROM weight_logs
            WHERE member_id=? ORDER BY month DESC LIMIT 6
        """, (member_id,)).fetchall()

        fees = db.execute("""
            SELECT * FROM fees WHERE member_id=?
            ORDER BY next_due DESC
        """, (member_id,)).fetchall()

        recent_attendance = db.execute("""
            SELECT date, status FROM attendance
            WHERE member_id=? ORDER BY date DESC LIMIT 10
        """, (member_id,)).fetchall()

    return render_template(
        "member_details.html",
        member=member,
        attendance_data=attendance_data,
        weight_logs=weight_logs,
        fees=fees,
        recent_attendance=recent_attendance
    )

# ---------------- MARK ATTENDANCE ----------------
@app.route("/attendance/<int:member_id>", methods=["GET", "POST"])
def attendance(member_id):
    today = datetime.now().strftime("%Y-%m-%d")

    if datetime.now().weekday() == 6:
        flash("Sunday is holiday 💤", "info")
        return redirect("/")

    if request.method == "POST":
        status = request.form.get("status", "Present")

        with get_db() as db:
            try:
                db.execute("""
                    INSERT INTO attendance (member_id, date, status)
                    VALUES (?, ?, ?)
                """, (member_id, today, status))
                flash("Attendance marked", "success")
            except sqlite3.IntegrityError:
                flash("Attendance already marked today", "error")

        return redirect("/")

    with get_db() as db:
        member = db.execute(
            "SELECT name FROM members WHERE id=?", (member_id,)
        ).fetchone()

    return render_template(
        "mark_attendance.html",
        member_name=member["name"]
    )

# ---------------- ADD WEIGHT ----------------
@app.route("/add-weight", methods=["POST"])
def add_weight():
    with get_db() as db:
        db.execute("""
            INSERT INTO weight_logs (member_id, month, weight)
            VALUES (?, ?, ?)
        """, (
            request.form["member_id"],
            request.form["month"],
            request.form["weight"]
        ))

    flash("Weight updated", "success")
    return redirect(f"/member/{request.form['member_id']}")

# ---------------- ADD FEES ----------------
@app.route("/add-fees", methods=["POST"])
def add_fees():
    last_paid = datetime.now()
    next_due = last_paid + timedelta(days=30)

    with get_db() as db:
        db.execute("""
            INSERT INTO fees (member_id, amount, last_paid, next_due, paid_status)
            VALUES (?, ?, ?, ?, 'paid')
        """, (
            request.form["member_id"],
            request.form["amount"],
            last_paid.strftime("%Y-%m-%d"),
            next_due.strftime("%Y-%m-%d")
        ))

    flash("Payment recorded", "success")
    return redirect(f"/member/{request.form['member_id']}")

# ---------------- FEES DASHBOARD ----------------
@app.route("/fees")
def fees_dashboard():
    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as db:
        pending_fees = db.execute("""
            SELECT f.id, m.id, m.name, f.amount, f.next_due
            FROM fees f JOIN members m ON f.member_id=m.id
            WHERE f.paid_status='pending'
        """).fetchall()

    overdue_count = sum(1 for f in pending_fees if f["next_due"] < today)

    return render_template(
        "fees.html",
        pending_fees=pending_fees,
        overdue_count=overdue_count
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)

