# 🔧 GymPro - Installation & Troubleshooting Guide

## 📋 System Requirements

### Minimum Requirements
- **OS**: macOS, Windows, Linux
- **Python**: 3.7 or higher
- **RAM**: 512MB minimum
- **Disk Space**: 50MB minimum
- **Browser**: Any modern browser (Chrome, Firefox, Safari, Edge)

### Recommended
- **Python**: 3.9 or higher
- **RAM**: 1GB or more
- **Modern Browser**: Latest version

---

## ✅ Installation Steps

### Step 1: Verify Python Installation
```bash
python --version
# Should output: Python 3.7+ 
```

### Step 2: Install Flask (if needed)
```bash
pip install flask
```

### Step 3: Navigate to Project Directory
```bash
cd /Users/sachinsingh/Desktop/GYM
```

### Step 4: Start the Application
```bash
python app.py
```

### Step 5: Open in Browser
```
http://127.0.0.1:5000
```

---

## 🎯 Successful Start Indicators

When you run `python app.py`, you should see:
```
* Serving Flask app 'app'
* Debug mode: on
WARNING: This is a development server...
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
* Restarting with stat
* Debugger is active!
* Debugger PIN: 100-412-960
```

✅ This means the app started successfully!

---

## 🔴 Troubleshooting

### Problem 1: Python Not Found
```
Error: 'python' is not recognized as an internal or external command
```

**Solution:**
1. Install Python from python.org
2. Make sure to check "Add Python to PATH" during installation
3. Restart terminal after installation
4. Try `python --version` again

### Problem 2: Port 5000 Already in Use
```
Error: Address already in use
Port 5000 is in use by another program
```

**Solutions:**

**Option A: Kill the existing process (macOS/Linux)**
```bash
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
python app.py
```

**Option B: Use a different port**
1. Open `app.py` in editor
2. Find the last line: `app.run(debug=True)`
3. Change to: `app.run(debug=True, port=5001)`
4. Save and run `python app.py`
5. Open: `http://127.0.0.1:5001`

**Option C: Restart computer**
- Simple solution that usually works

### Problem 3: Flask Not Installed
```
Error: No module named 'flask'
```

**Solution:**
```bash
pip install flask
```

If that doesn't work:
```bash
pip3 install flask
```

### Problem 4: Permission Denied
```
Error: Permission denied while trying to connect to socket
```

**Solution:**
```bash
# Try with sudo (macOS/Linux)
sudo python app.py

# Or change port as shown above
```

### Problem 5: Database Issues
```
Error: database is locked
```

**Solution:**
1. Close the application (press CTRL+C)
2. Wait 2 seconds
3. Delete `gym.db` file (will be recreated)
4. Run `python app.py` again

### Problem 6: Browser Shows "Connection Refused"
```
Error: Connection refused
```

**Solution:**
1. Make sure you see the Flask startup messages
2. Check that the URL is correct: `http://127.0.0.1:5000`
3. Wait a few seconds after seeing "Running on..."
4. Try refreshing the page (Cmd+R on Mac)
5. Try a different browser

### Problem 7: Changes Not Reflecting
```
Changes to code don't appear in browser
```

**Solution:**
- Flask is in debug mode, so it auto-reloads
- Refresh browser (Cmd+R on Mac, Ctrl+R on Windows)
- If still not working:
  1. Close browser tab
  2. Stop Flask (Ctrl+C in terminal)
  3. Wait 2 seconds
  4. Run `python app.py` again
  5. Open fresh tab with `http://127.0.0.1:5000`

### Problem 8: Dates Not Showing Correctly
```
Reminder system not showing payments
```

**Solution:**
1. Check system date/time
2. Make sure today's date is set correctly
3. Add a fee with today's date
4. Payment should show as reminder in 2-3 days or as pending if past due

### Problem 9: Database Not Creating
```
Error when trying to create tables
```

**Solution:**
1. Check write permissions in project folder
2. Make sure you're not running from a read-only location
3. Try moving project to Desktop or Documents
4. Run `python app.py` again

---

## 🛠️ Maintenance Tasks

### Regular Maintenance
```bash
# Check database size
ls -lh gym.db

# Backup database (weekly)
cp gym.db gym.db.backup

# Clear old records (if needed)
# Edit app.py to add cleanup function
```

### Update Code
```bash
# Stop running app (Ctrl+C)
# Edit files
# Start app again (python app.py)
```

### Reset Database
```bash
# Stop the app (Ctrl+C)
# Delete database
rm gym.db
# Restart app (it will create fresh database)
python app.py
```

---

## 🔍 Debugging Tips

### Check Status
1. Open browser to `http://127.0.0.1:5000`
2. Look at terminal for any error messages
3. Check database exists (`gym.db` in project folder)

### Enable Detailed Logging
Edit `app.py` bottom to add:
```python
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
```

### Test Database Connection
Open terminal in project folder:
```bash
python
>>> import sqlite3
>>> db = sqlite3.connect("gym.db")
>>> print("Database works!")
>>> exit()
```

### Clear Browser Cache
- Chrome: Cmd+Shift+Delete (Mac) or Ctrl+Shift+Delete (Windows)
- Firefox: Cmd+Shift+Delete (Mac) or Ctrl+Shift+Delete (Windows)
- Safari: Develop menu → Empty Web Caches

---

## 📊 Performance Tips

### Optimize Database
If app gets slow after many records:
```bash
# Stop app
rm gym.db
python app.py
```

### Monitor Memory
```bash
# macOS
top -l 1 | grep python

# Linux
ps aux | grep python
```

### Check Port Usage
```bash
# See all ports in use
lsof -i -P -n | grep LISTEN
```

---

## 🌐 Network Issues

### App Only Accessible Locally
**By design** - the app runs on `127.0.0.1:5000` (localhost)

**To access from other computers on network:**
Edit the bottom of `app.py`:
```python
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
```

Then access from other computer using your IP:
```
http://YOUR_IP_ADDRESS:5000
```

### CORS Issues
Usually not a problem for local use. If needed, install flask-cors:
```bash
pip install flask-cors
```

---

## 📱 Mobile Access

### Access from Phone on Same Network

1. Find your computer's IP address:
```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig

# Linux
hostname -I
```

2. Edit `app.py` to allow external access:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

3. On your phone, open:
```
http://YOUR_COMPUTER_IP:5000
```

---

## 🔐 Security Notes

### Development vs Production
The app is configured for development:
- Debug mode: ON
- Uses Flask development server
- Not suitable for production with many users

### For Production
You would need:
- Gunicorn or uWSGI (production server)
- Nginx or Apache (reverse proxy)
- SSL/HTTPS certificates
- Database backups
- Authentication system

### Local Security
- Database stored locally: `gym.db`
- No passwords currently (add if needed)
- No external connections
- All data stays on your computer

---

## 📞 Quick Reference

### Common Commands
```bash
# Start app
python app.py

# Stop app
Ctrl+C

# Kill specific port
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Check Python version
python --version

# Install Flask
pip install flask

# List active connections
netstat -an | grep LISTEN
```

### Common URLs
```
Home:              http://127.0.0.1:5000/
Member Profile:    http://127.0.0.1:5000/member/1
Mark Attendance:   http://127.0.0.1:5000/attendance/1
Attendance History: http://127.0.0.1:5000/attendance-history
Fee Dashboard:     http://127.0.0.1:5000/fees
```

---

## 🆘 Still Having Issues?

### Checklist
- [ ] Python is installed (check with `python --version`)
- [ ] Flask is installed (check with `pip show flask`)
- [ ] No other app is using port 5000
- [ ] Project folder has write permissions
- [ ] Using correct URL: `http://127.0.0.1:5000`
- [ ] Waited a few seconds after seeing "Running on..."
- [ ] Tried refreshing browser (Cmd+R)

### Last Resort
1. Delete `gym.db`
2. Stop Flask (Ctrl+C)
3. Close all terminals
4. Reopen terminal
5. Run: `python app.py`
6. Open: `http://127.0.0.1:5000`

---

## 📚 Additional Resources

### Python Help
```bash
python -m help
```

### Flask Help
```bash
pip show flask
```

### Troubleshooting Tips
- Check terminal for error messages
- Read Flask documentation
- Search for error message online
- Try the Last Resort steps above

---

## 🎯 Common Questions

**Q: Do I need internet?**  
A: No, everything runs locally. Only needed if accessing from another device.

**Q: Can I close the terminal while using the app?**  
A: No, terminal must stay open. The app runs in it.

**Q: Will I lose data if I close the terminal?**  
A: No, all data is saved in `gym.db`. You'll just need to restart the app.

**Q: Can multiple people use it at once?**  
A: Yes, if they're on the same network (with `host='0.0.0.0'`).

**Q: What if I accidentally delete gym.db?**  
A: Just restart the app and it creates a new empty database.

**Q: Can I backup my data?**  
A: Yes, copy `gym.db` to another location.

---

## 🔄 Update Process

### To Update Code
1. Stop app (Ctrl+C)
2. Edit the files
3. Restart app (python app.py)
4. Changes take effect immediately

### To Backup Data
```bash
cp gym.db gym.db.backup.$(date +%Y%m%d)
```

### To Restore Data
```bash
cp gym.db.backup.DATE gym.db
```

---

**Version**: 1.0  
**Last Updated**: December 31, 2025  
**Status**: Ready for Use
