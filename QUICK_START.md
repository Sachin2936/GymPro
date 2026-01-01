# 🏋️ GymPro - Quick Start Guide

## 🚀 Get Started in 30 Seconds

1. **Start the Application**
   ```bash
   cd /Users/sachinsingh/Desktop/GYM
   python app.py
   ```

2. **Open in Browser**
   - Visit: `http://127.0.0.1:5000`

3. **Add Your First Member**
   - Fill "Add New Member" form on home page
   - Click "Add Member"

4. **Mark Attendance**
   - Click "✓ Attend" on member card
   - Select status (Present/Absent/Leave/Late)
   - Confirm

5. **Record Payment**
   - Go to member profile
   - Enter fee amount in "Fee Payment History" section
   - Click "Record Payment"

---

## 🎯 Main Features at a Glance

| Feature | Access | Purpose |
|---------|--------|---------|
| **Mark Attendance** | Member card or Profile | Track daily gym visits |
| **Record Fees** | Member profile | Log membership payments |
| **View Reminders** | Home dashboard | Get alerts 2-3 days before due |
| **Member Profile** | Click "Profile" button | See complete member data |
| **Attendance History** | "View History" button | View all attendance records |
| **Fee Dashboard** | "View All Payments" link | Manage all payments |
| **Weight Tracking** | Member profile | Monitor fitness progress |

---

## 📋 Page URLs

```
Home Dashboard:         http://127.0.0.1:5000/
Member Profile:        http://127.0.0.1:5000/member/<id>
Mark Attendance:       http://127.0.0.1:5000/attendance/<id>
Attendance History:    http://127.0.0.1:5000/attendance-history
Fee Dashboard:         http://127.0.0.1:5000/fees
```

---

## ⚡ Quick Actions

### 1. Add Member
```
Home Page → "Add New Member" Form → Fill Details → Click "Add Member"
```

### 2. Mark Attendance
```
Home Page → Click "✓ Attend" → Select Status → Confirm
```

### 3. Record Payment
```
Member Profile → Fee Section → Enter Amount → "Record Payment"
```

### 4. Check Reminders
```
Home Page → Look at Alert Boxes (Top Section)
```

### 5. View All Members
```
Home Page → Scroll Down → Members Grid Shows All Active Members
```

---

## 🎨 UI Color Guide

- **Orange (#ff6b35)**: Primary actions and highlights
- **Green**: Present/Paid status ✓
- **Red**: Absent/Overdue status ✗
- **Yellow**: Leave/Pending status
- **Dark Blue**: Background

---

## 💡 Pro Tips

1. **Quick Payment Check**: Home page shows overdue and upcoming payments at the top
2. **Member Avatar**: First letter of member name appears in avatar
3. **Automatic Dates**: Payment due date auto-calculates to 30 days from payment
4. **Sunday Holiday**: System auto-skips Sundays for attendance
5. **Member Search**: Click member profile from any attendance record
6. **Fee Status**: Quickly see if payment is Pending or Paid from any page

---

## 📊 Dashboard Information

### Home Page Shows:
- ⏰ **Reminders**: Fees due in 2-3 days (with amounts)
- 🚨 **Overdue**: Payments past due date
- 👥 **Active Members**: All current members with quick actions
- 💳 **Fee Link**: Quick access to full fee dashboard
- 📊 **Attendance Link**: View all attendance records

### Member Profile Shows:
- 📅 Personal info (name, phone, email, join date)
- 📊 Monthly attendance stats
- ⚖️ Weight progress
- 💳 Fee history
- 📋 Recent attendance (last 10 records)
- ➕ Forms to add weight and record payments

---

## 🔄 Common Workflows

### Daily Check-in
1. Open home page
2. Review reminders and overdue fees
3. Mark attendance for arriving members
4. Record any payments received

### Weekly Member Check
1. Go to member profile
2. Review attendance for the week
3. Check if any payments are pending
4. Update weight if available

### Monthly Admin
1. Go to Fee Dashboard
2. Review all pending payments
3. Send reminders to members with due fees
4. Update member statuses as needed

---

## ❌ Status Meanings

| Status | Icon | Meaning |
|--------|------|---------|
| **Present** | ✓ | Member attended gym |
| **Absent** | ✗ | Member didn't show up |
| **Leave** | ~ | Member took approved leave |
| **Late** | 🕐 | Member arrived late |
| **Paid** | ✓ | Payment received |
| **Pending** | ⏳ | Payment awaiting |
| **Overdue** | 🚨 | Payment date passed |

---

## 📱 Responsive Design

✅ Works on:
- Desktop (Full features)
- Tablet (Optimized layout)
- Mobile (Touch-friendly buttons)

---

## 🆘 Quick Help

**Q: How do I mark attendance?**  
A: Home page → Click "✓ Attend" on member card

**Q: How do I record a payment?**  
A: Member profile → Fee section → Enter amount → Record

**Q: Where are the payment reminders?**  
A: Home page top section in alert boxes

**Q: Can I see member's history?**  
A: Yes! Click "Profile" to see complete history

**Q: What happens to payment dates?**  
A: Auto-set to 30 days from payment date

**Q: Are Sundays included in attendance?**  
A: No, Sundays are automatically holidays

---

## 🎯 Dashboard Buttons

### Home Page Buttons
- ➕ **Add Member**: Register new member
- 💳 **View All Payments**: Go to fee dashboard
- 📊 **View History**: See all attendance records
- **Profile**: Click on member card for details
- **✓ Attend**: Mark attendance for member

### Member Profile Buttons
- ✓ **Mark Attendance**: Record today's attendance
- ⚖️ **Add Weight**: Log weight for current month
- 💳 **Add Fee**: Record payment received
- 📊 **View History**: See attendance history
- ⬅️ **Back**: Return to home

---

## 🗄️ Database

- Automatically created on first run
- File: `gym.db` in project folder
- Contains: Members, Attendance, Fees, Weight logs
- No backup needed for demo use

---

## 🔑 Key Keyboard Tips

- **Tab**: Navigate between form fields
- **Enter**: Submit forms
- **Esc** (in future): Close dialogs (when added)

---

## 💬 Need Help?

1. Check README.md for detailed documentation
2. Hover over elements for tooltips
3. Check member profiles for historical data
4. Review attendance history for patterns

---

**Version**: 1.0 | **Last Updated**: Dec 31, 2025
