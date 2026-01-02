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

        db.execute("""
        CREATE TABLE IF NOT EXISTS profits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            amount REAL,
            payment_date TEXT,
            fee_id INTEGER,
            UNIQUE(fee_id)
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

        # Get total profits
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits"
        ).fetchone()[0]

    return render_template("index.html",
                           members=members,
                           reminders=reminders,
                           total_profit=total_profit)

# ---------------- INACTIVE MEMBERS ----------------
@app.route("/inactive-members")
def inactive_members():
    with get_db() as db:
        inactive = db.execute(
            "SELECT * FROM members WHERE status='inactive' ORDER BY name"
        ).fetchall()

    return render_template("inactive_members.html", inactive_members=inactive)

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
            WHERE member_id=? ORDER BY month DESC
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
        db.execute("""
            INSERT INTO weight_logs (member_id, month, weight)
            VALUES (?, ?, ?)
        """, (member_id, today, weight))

    flash("Weight updated successfully 💪", "success")
    return redirect(f"/member/{member_id}")

# ---------------- ADD FEES ----------------
@app.route("/add-fees", methods=["POST"])
def add_fees():
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
        db.execute("""
            INSERT INTO fees (member_id, amount, last_paid, next_due, paid_status)
            VALUES (?, ?, ?, ?, 'paid')
        """, (
            member_id,
            amount,
            last_paid.strftime("%Y-%m-%d"),
            next_due.strftime("%Y-%m-%d")
        ))

        # Get the fee id that was just inserted
        fee_id = db.execute(
            "SELECT id FROM fees WHERE member_id = ? ORDER BY id DESC LIMIT 1",
            (member_id,)
        ).fetchone()[0]

        # Add to profits
        db.execute("""
            INSERT INTO profits (member_id, amount, payment_date, fee_id)
            VALUES (?, ?, ?, ?)
        """, (
            member_id,
            amount,
            last_paid.strftime("%Y-%m-%d"),
            fee_id
        ))

    flash("Fee added successfully 💰", "success")
    return redirect(f"/member/{member_id}")

# ---------------- MARK FEE AS PAID ----------------
@app.route("/pay-fees/<int:member_id>", methods=["POST"])
def pay_fees(member_id):
    today = datetime.now()

    with get_db() as db:
        # Get the pending fee to be marked as paid
        fee = db.execute("""
            SELECT id, amount FROM fees
            WHERE member_id = ? AND paid_status = 'pending'
            ORDER BY next_due DESC
            LIMIT 1
        """, (member_id,)).fetchone()

        if fee:
            fee_id, amount = fee[0], fee[1]
            
            # Update the fee status
            db.execute("""
                UPDATE fees
                SET paid_status = 'paid', last_paid = ?
                WHERE id = ?
            """, (today.strftime("%Y-%m-%d"), fee_id))

            # Add to profits
            db.execute("""
                INSERT OR IGNORE INTO profits (member_id, amount, payment_date, fee_id)
                VALUES (?, ?, ?, ?)
            """, (
                member_id,
                amount,
                today.strftime("%Y-%m-%d"),
                fee_id
            ))

    flash("Fee marked as paid ✅", "success")
    return redirect(f"/member/{member_id}")


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

        # Get total profit data
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits"
        ).fetchone()[0]

        profit_entries = db.execute("""
            SELECT m.name, p.amount, p.payment_date
            FROM profits p JOIN members m ON p.member_id=m.id
            ORDER BY p.payment_date DESC
            LIMIT 20
        """).fetchall()

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
def profits_dashboard():
    with get_db() as db:
        total_profit = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM profits"
        ).fetchone()[0]

        profit_entries = db.execute("""
            SELECT m.name, p.amount, p.payment_date
            FROM profits p JOIN members m ON p.member_id=m.id
            ORDER BY p.payment_date DESC
        """).fetchall()

        # Get profit by member
        profit_by_member = db.execute("""
            SELECT m.name, COUNT(*) as payments, SUM(p.amount) as total_amount
            FROM profits p JOIN members m ON p.member_id=m.id
            GROUP BY p.member_id
            ORDER BY total_amount DESC
        """).fetchall()

    return render_template(
        "profits.html",
        total_profit=total_profit,
        profit_entries=profit_entries,
        profit_by_member=profit_by_member
    )

# ---------------- REMOVE MEMBER ----------------
@app.route("/remove-member/<int:member_id>", methods=["POST"])
def remove_member(member_id):
    with get_db() as db:
        # Get member name before deletion
        member = db.execute(
            "SELECT name FROM members WHERE id=?", (member_id,)
        ).fetchone()
        
        if member:
            # Mark member as inactive instead of deleting
            db.execute(
                "UPDATE members SET status='inactive' WHERE id=?",
                (member_id,)
            )
            flash(f"Member '{member['name']}' has been removed from the gym", "success")
        else:
            flash("Member not found", "error")
    
    return redirect("/")

# ---------------- REACTIVATE MEMBER ----------------
@app.route("/reactivate-member/<int:member_id>", methods=["POST"])
def reactivate_member(member_id):
    with get_db() as db:
        # Get member name before reactivation
        member = db.execute(
            "SELECT name FROM members WHERE id=?", (member_id,)
        ).fetchone()
        
        if member:
            # Mark member as active again
            db.execute(
                "UPDATE members SET status='active' WHERE id=?",
                (member_id,)
            )
            flash(f"Member '{member['name']}' has been reactivated", "success")
        else:
            flash("Member not found", "error")
    
    return redirect("/inactive-members")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)