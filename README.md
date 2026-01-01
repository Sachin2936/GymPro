# 💪 GymPro - Gym Management System

A modern, feature-rich web application for managing gym members, tracking attendance, and managing membership fees with automated payment reminders.

## ✨ Features

### 👥 Member Management
- **Add Members**: Register new gym members with personal details
  - Full name
  - Phone number
  - Email address
  - Starting weight
- **Member Profiles**: Comprehensive member dashboard with:
  - Personal information
  - Attendance statistics
  - Weight tracking history
  - Fee payment records
  - Recent attendance logs

### ✓ Attendance Tracking
- **Mark Attendance**: Quick and easy attendance marking with status options:
  - ✓ Present
  - ✗ Absent
  - ~ Leave
  - 🕐 Late
- **Attendance History**: View complete attendance records with filtering
- **Monthly Statistics**: Track monthly attendance patterns per member
- **Automatic Sunday Holiday**: System automatically excludes Sundays

### 💳 Fee Management System
- **Payment Recording**: Record membership fee payments with automatic 30-day renewal
- **Fee Tracking**: Monitor payment status (Paid/Pending)
- **Automated Reminders**: 
  - 2-3 days before due date: Payment reminder alerts
  - Display on dashboard for quick access
- **Overdue Tracking**: Automatic detection and display of overdue payments
- **Fee Dashboard**: Centralized view of all pending and overdue fees
- **Member-wise History**: Complete payment history for each member

### ⚖️ Weight Tracking
- **Monthly Weight Logs**: Record and track member weight progress
- **Weight History**: View weight trends over time
- **Progress Monitoring**: Track fitness journey with historical data

### 📊 Dashboard Analytics
- **Quick Stats**: 
  - Total active members
  - Pending payments
  - Overdue fees
  - Total amount due
- **Alert System**: 
  - Fee reminders (2-3 days prior)
  - Overdue payment alerts
- **Easy Navigation**: Quick action buttons for common tasks

## 🎨 User Interface

### Modern Design Features
- **Dark Theme**: Eye-friendly dark interface optimized for gym environment
- **Gradient UI**: Professional orange-themed gradients (#ff6b35 primary color)
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Smooth Animations**: Hover effects and transitions for better UX
- **Card-based Layout**: Clean, organized card-based interface
- **Icons & Emojis**: Visual cues for quick navigation and identification

### Color Scheme
- **Primary**: #ff6b35 (Gym Orange)
- **Background**: Dark blue gradient (#1a1a2e to #16213e)
- **Text**: Light colors for readability
- **Status Colors**: 
  - Green (#4caf50) for Present/Paid
  - Red (#ff4343) for Absent/Overdue
  - Yellow (#ffc107) for Leave/Pending
  - Orange (#ff9800) for Late

## 📱 Pages Overview

### 1. **Home Dashboard** (`/`)
- Welcome banner with gym branding
- **Alert Boxes**:
  - Payment reminders (due in 2-3 days)
  - Overdue payments alert
- **Quick Actions**:
  - Add new member form
  - Fee management link
  - Attendance records link
- **Members Grid**: Display all active members with:
  - Member avatar
  - Name and join date
  - Quick action buttons (Profile, Mark Attendance)

### 2. **Member Profile** (`/member/<id>`)
- Complete member information
- **Sections**:
  - Member details (name, phone, email, join date, weight)
  - Quick action buttons
  - Monthly attendance statistics
  - Weight progress tracking
  - Fee payment history
  - Recent attendance records (last 10)
  - Forms to add weight and record payments

### 3. **Mark Attendance** (`/attendance/<id>`)
- Full-screen attendance marking interface
- Large member avatar and name
- Current date display
- Status selection buttons:
  - Present
  - Absent
  - Leave
  - Late
- Confirmation button

### 4. **Attendance History** (`/attendance-history`)
- Complete table of all attendance records
- Sortable by member and date
- Status badges (color-coded)
- Links to member profiles
- Displays latest records first

### 5. **Fee Dashboard** (`/fees`)
- Statistics cards showing:
  - Total pending payments
  - Overdue count
  - Total amount due
- Complete list of all pending fees with:
  - Member name and avatar
  - Fee amount
  - Due date
  - Status badge (Overdue/Pending)
  - Quick action buttons

## 🗄️ Database Schema

### members
```
id (PRIMARY KEY)
name (UNIQUE)
phone
email
join_date
start_weight
status (active/inactive)
```

### attendance
```
id (PRIMARY KEY)
member_id (FOREIGN KEY)
date
status (Present/Absent/Leave/Late)
```

### weight_logs
```
id (PRIMARY KEY)
member_id (FOREIGN KEY)
month
weight
```

### fees
```
id (PRIMARY KEY)
member_id (FOREIGN KEY)
amount
last_paid
next_due
paid_status (paid/pending)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7+
- Flask
- SQLite3 (built-in with Python)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd /Users/sachinsingh/Desktop/GYM
   ```

2. **Install Flask** (if not already installed)
   ```bash
   pip install flask
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:5000`
   - Or click the Simple Browser in VS Code

### Database
- The application automatically creates a SQLite database (`gym.db`)
- No manual setup required for the database
- Database is stored in the project root directory

## 📖 Usage Guide

### Adding a New Member
1. Go to Home page (`/`)
2. Fill in the "Add New Member" form:
   - Full Name (required)
   - Phone Number (optional)
   - Email Address (optional)
   - Starting Weight (optional)
3. Click "Add Member"
4. New member appears in the members grid

### Marking Attendance
1. Click "✓ Attend" button on any member card from home
2. Or navigate to member profile and click "Mark Attendance"
3. Select attendance status:
   - **Present**: Member attended the gym
   - **Absent**: Member didn't show up
   - **Leave**: Member took a leave
   - **Late**: Member arrived late
4. Click "✓ Mark Attendance"

### Recording Fee Payment
1. Go to member profile
2. Scroll to "Fee Payment History" section
3. Enter fee amount in the form
4. Click "Record Payment"
5. System automatically sets next due date as 30 days from today
6. Payment appears in member's fee history

### Viewing Fee Reminders
1. Home dashboard automatically shows:
   - **Reminders**: Fees due in 2-3 days
   - **Overdue**: Fees past the due date
2. Click member name in reminder to navigate to their profile
3. Or go to "Fee Management" dashboard for complete overview

### Tracking Weight Progress
1. Go to member profile
2. Scroll to "Weight Progress" section
3. Enter month (YYYY-MM format) and weight
4. Click "Add Weight"
5. Weight history shows last 6 entries with progression

### Viewing Member Details
1. Click "Profile" button on any member card
2. View complete member information:
   - Personal details
   - Attendance statistics for current month
   - Weight progress
   - Complete fee history
   - Recent attendance records

### Managing Fees
1. Click "View All Payments" from home or navigate to `/fees`
2. See all pending payments with:
   - Member name
   - Fee amount
   - Due date
   - Status
3. Click member profile to record payment or manage account

## 💡 Key Features Explained

### Automatic Reminder System
- Fees are set to be due 30 days after payment
- System checks for fees due in **2-3 days** and displays reminders
- **Overdue Fees**: Automatically tracked if payment date has passed
- Reminders visible on home dashboard for quick action

### Status Tracking
- Members have active/inactive status
- Only active members display on home dashboard
- Deactivate members when they cancel membership

### Monthly Attendance Stats
- Automatically calculated from attendance records
- Shows breakdown of Present/Absent/Leave/Late for current month
- Helps identify attendance patterns

### Smart Member Profiles
- Each member has a dedicated profile page
- Shows complete history and current metrics
- All member-related actions accessible from one page

## 🔒 Data Security
- All data stored locally in SQLite database
- No data sent to external servers
- Database file: `gym.db` in project root
- Password protection can be added if needed

## 🎯 Future Enhancements

Potential features for future versions:
- [ ] Member authentication/login
- [ ] SMS/Email notifications for fee reminders
- [ ] Membership packages and pricing tiers
- [ ] Payment history reports
- [ ] Monthly attendance reports
- [ ] Member statistics and analytics
- [ ] Batch member import
- [ ] Member leave management
- [ ] Payment method tracking
- [ ] Admin dashboard with advanced analytics

## 🐛 Troubleshooting

### Port Already in Use
```bash
# If port 5000 is busy, edit app.py and change:
app.run(debug=True, port=5001)
```

### Database Not Creating
- Ensure you have write permissions in the project directory
- Check that `gym.db` is not locked by another application

### Reminders Not Showing
- Check that fees have been recorded
- Ensure due dates are set correctly
- Verify current date on your system

## 📞 Support
For issues or questions, check:
- Member profile pages for complete history
- Fee dashboard for payment overview
- Attendance history for records

## 📄 License
This project is for personal use in gym management.

---

**Version**: 1.0  
**Last Updated**: December 31, 2025  
**Created for**: GymPro Management System
