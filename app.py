from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("gym.db")

def get_member_id_by_name(name):
    db = get_db()
    member = db.execute(
        "SELECT id FROM members WHERE name = ?",
        (name,)
    ).fetchone()
    db.close()
    return member[0] if member else None

# ---------------- TABLES ----------------
def create_tables():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        phone TEXT,
        email TEXT,
        join_date TEXT,
        start_weight REAL,
        status TEXT DEFAULT 'active'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        date TEXT,
        status TEXT,
        FOREIGN KEY (member_id) REFERENCES members(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS weight_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        month TEXT,
        weight REAL,
        FOREIGN KEY (member_id) REFERENCES members(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        amount REAL,
        last_paid TEXT,
        next_due TEXT,
        paid_status TEXT DEFAULT 'pending',
        FOREIGN KEY (member_id) REFERENCES members(id)
    )
    """)

    db.commit()
    db.close()

create_tables()

# ---------------- HOME ----------------
@app.route("/")
def index():
    db = get_db()
    members = db.execute("SELECT * FROM members WHERE status = 'active' ORDER BY name").fetchall()
    
    # Get fee reminders (due within 2-3 days)
    today = datetime.now()
    reminder_date_start = today + timedelta(days=2)
    reminder_date_end = today + timedelta(days=3)
    
    reminders = db.execute("""
        SELECT members.id, members.name, fees.next_due, fees.amount
        FROM fees
        JOIN members ON fees.member_id = members.id
        WHERE fees.next_due BETWEEN ? AND ? AND fees.paid_status = 'pending'
        ORDER BY fees.next_due ASC
    """, (reminder_date_start.strftime("%Y-%m-%d"), reminder_date_end.strftime("%Y-%m-%d"))).fetchall()
    
    # Get overdue payments
    overdue = db.execute("""
        SELECT members.id, members.name, fees.next_due, fees.amount
        FROM fees
        JOIN members ON fees.member_id = members.id
        WHERE fees.next_due < ? AND fees.paid_status = 'pending'
        ORDER BY fees.next_due ASC
    """, (today.strftime("%Y-%m-%d"),)).fetchall()
    
    db.close()
    return render_template("index.html", members=members, reminders=reminders, overdue=overdue)

# ---------------- ADD MEMBER ----------------
@app.route("/add-member", methods=["POST"])
def add_member():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    weight = request.form.get("weight", "0")
    join_date = datetime.now().strftime("%Y-%m-%d")

    if not name:
        return redirect("/")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO members (name, phone, email, join_date, start_weight, status) VALUES (?, ?, ?, ?, ?, 'active')",
            (name, phone, email, join_date, weight)
        )
        db.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        db.close()

    return redirect("/")

# ---------------- MEMBER DETAILS ----------------
@app.route("/member/<int:member_id>")
def member_details(member_id):
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    
    if not member:
        db.close()
        return redirect("/")
    
    # Get attendance stats
    today = datetime.now()
    this_month_start = today.replace(day=1).strftime("%Y-%m-%d")
    
    attendance_data = db.execute("""
        SELECT status, COUNT(*) as count
        FROM attendance
        WHERE member_id = ? AND date >= ?
        GROUP BY status
    """, (member_id, this_month_start)).fetchall()
    
    # Get weight logs
    weight_logs = db.execute("""
        SELECT month, weight FROM weight_logs WHERE member_id = ? ORDER BY month DESC LIMIT 6
    """, (member_id,)).fetchall()
    
    # Get fee information
    fees = db.execute("""
        SELECT * FROM fees WHERE member_id = ? ORDER BY next_due DESC
    """, (member_id,)).fetchall()
    
    # Get recent attendance
    recent_attendance = db.execute("""
        SELECT date, status FROM attendance WHERE member_id = ? ORDER BY date DESC LIMIT 10
    """, (member_id,)).fetchall()
    
    db.close()
    
    return render_template("member_details.html", member=member, attendance_data=attendance_data, 
                         weight_logs=weight_logs, fees=fees, recent_attendance=recent_attendance)

# ---------------- MARK ATTENDANCE ----------------
@app.route("/attendance/<int:member_id>", methods=["GET", "POST"])
def attendance(member_id):
    today = datetime.now()

    if today.strftime("%A") == "Sunday":
        return "Sunday is Holiday 💤"

    db = get_db()
    member = db.execute("SELECT name FROM members WHERE id = ?", (member_id,)).fetchone()
    
    if request.method == "POST":
        status = request.form.get("status", "Present")
        db.execute(
            "INSERT INTO attendance (member_id, date, status) VALUES (?, ?, ?)",
            (member_id, today.strftime("%Y-%m-%d"), status)
        )
        db.commit()
        db.close()
        return redirect("/")
    
    db.close()
    return render_template("mark_attendance.html", member_id=member_id, member_name=member[0] if member else "Member")

# ---------------- ATTENDANCE HISTORY ----------------
@app.route("/attendance-history")
def attendance_history():
    db = get_db()
    records = db.execute("""
        SELECT members.id, members.name, attendance.date, attendance.status
        FROM attendance
        JOIN members ON attendance.member_id = members.id
        ORDER BY attendance.date DESC
        LIMIT 50
    """).fetchall()
    db.close()

    return render_template("attendance.html", records=records)

# ---------------- ADD MONTHLY WEIGHT ----------------
@app.route("/add-weight", methods=["POST"])
def add_weight():
    member_id = request.form.get("member_id")
    month = request.form.get("month")
    weight = request.form.get("weight")

    if not all([member_id, month, weight]):
        return redirect("/")

    db = get_db()
    db.execute(
        "INSERT INTO weight_logs (member_id, month, weight) VALUES (?, ?, ?)",
        (member_id, month, weight)
    )
    db.commit()
    db.close()

    return redirect(f"/member/{member_id}")

# ---------------- ADD FEES ----------------
@app.route("/add-fees", methods=["POST"])
def add_fees():
    member_id = request.form.get("member_id")
    amount = request.form.get("amount", "0")

    if not member_id:
        return redirect("/")

    last_paid = datetime.now()
    next_due = last_paid + timedelta(days=30)

    db = get_db()
    db.execute(
        "INSERT INTO fees (member_id, amount, last_paid, next_due, paid_status) VALUES (?, ?, ?, ?, 'paid')",
        (
            member_id,
            amount,
            last_paid.strftime("%Y-%m-%d"),
            next_due.strftime("%Y-%m-%d")
        )
    )
    db.commit()
    db.close()

    return redirect(f"/member/{member_id}")

# ---------------- UPDATE FEE STATUS ----------------
@app.route("/update-fee/<int:fee_id>/<status>", methods=["POST"])
def update_fee_status(fee_id, status):
    db = get_db()
    fee = db.execute("SELECT member_id FROM fees WHERE id = ?", (fee_id,)).fetchone()
    
    if fee and status in ['paid', 'pending']:
        db.execute("UPDATE fees SET paid_status = ? WHERE id = ?", (status, fee_id))
        db.commit()
        member_id = fee[0]
        db.close()
        return redirect(f"/member/{member_id}")
    
    db.close()
    return redirect("/")

# ---------------- FEES DASHBOARD ----------------
@app.route("/fees")
def fees_dashboard():
    db = get_db()
    today = datetime.now()
    
    # All pending fees with member info
    pending_fees = db.execute("""
        SELECT fees.id, members.id, members.name, fees.amount, fees.next_due
        FROM fees
        JOIN members ON fees.member_id = members.id
        WHERE fees.paid_status = 'pending' AND members.status = 'active'
        ORDER BY fees.next_due ASC
    """).fetchall()
    
    # Overdue
    overdue_count = sum(1 for f in pending_fees if f[4] < today.strftime("%Y-%m-%d"))
    
    db.close()
    return render_template("fees.html", pending_fees=pending_fees, overdue_count=overdue_count)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
