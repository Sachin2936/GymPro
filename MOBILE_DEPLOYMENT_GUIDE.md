# GymPro Mobile Deployment Guide 📱

Deploy your GymPro gym management system to make it accessible from mobile phones and other devices on your network or the internet.

---

## Quick Options Comparison

| Option | Setup Time | Cost | Access | Best For |
|--------|-----------|------|--------|----------|
| **Local Network (WiFi)** | 5 mins | Free | Same WiFi | Testing with team |
| **ngrok (Tunnel)** | 5 mins | Free/Paid | Internet | Quick demo |
| **Render/Railway** | 15 mins | $0-7/mo | Internet 24/7 | Production |
| **AWS/Heroku** | 30 mins | $5-50/mo | Internet 24/7 | Enterprise |

---

## Option 1: Local Network Access (Easiest - Start Here!)

### Step 1: Stop current Flask server
```bash
pkill -9 -f "python.*app.py"
sleep 1
```

### Step 2: Find your Mac's IP address
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
You'll see something like: `192.168.x.x` or `10.0.x.x`

**Example output:**
```
inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255
```
Copy this IP: `192.168.1.100`

### Step 3: Modify app.py to accept external connections

Edit your `app.py` and find this line:
```python
if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5001)
```

Replace it with:
```python
if __name__ == "__main__":
    create_tables()
    app.run(debug=True, host="0.0.0.0", port=5001)
```

**The change:** Add `host="0.0.0.0"` to accept connections from any device on the network.

### Step 4: Start the server
```bash
cd /Users/sachinsingh/GymPro && python3 app.py
```

You'll see:
```
Running on http://0.0.0.0:5001
Press CTRL+C to quit
```

### Step 5: Access from mobile phone on same WiFi

On your mobile phone:
1. Connect to the **same WiFi network** as your Mac
2. Open a browser
3. Go to: `http://192.168.1.100:5001` (use YOUR IP from Step 2)
4. You should see GymPro login page!

### ✅ This is working!

**Who can access:** Anyone on your WiFi network
**Cost:** Free
**Best for:** Testing with staff/trainers before going live

---

## Option 2: Use ngrok for Internet Access (5 minutes)

Perfect for quick demos or temporary external access without any server costs.

### Step 1: Install ngrok
```bash
# Using Homebrew
brew install ngrok

# Or download from https://ngrok.com/download
```

### Step 2: Create ngrok account (free)
1. Go to https://ngrok.com
2. Sign up (free)
3. Copy your auth token

### Step 3: Authenticate ngrok
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 4: Start your Flask server (if not running)
```bash
cd /Users/sachinsingh/GymPro && python3 app.py
```

### Step 5: In a NEW terminal, run ngrok
```bash
ngrok http 5001
```

You'll see:
```
Session Status                online
Account                       your@email.com
Version                       3.x.x
Region                        us (United States)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123-456.ngrok.io -> http://localhost:5001
```

### Step 6: Share the public URL
Copy the URL: `https://abc123-456.ngrok.io`

Send this to gym members or staff. They can access from **anywhere in the world**!

**Lifespan:** URL lasts while ngrok is running (restart = new URL)

---

## Option 3: Deploy to Render (Best for Production) 🚀

Deploy your website to a real server. **Free tier available!**

### Step 1: Prepare your app for production

Create a `requirements.txt` file:
```bash
cd /Users/sachinsingh/GymPro
pip3 freeze > requirements.txt
```

Create `Procfile` (tells Render how to start your app):
```
web: python app.py
```

Modify `app.py` for production (change this line):
```python
# OLD:
if __name__ == "__main__":
    create_tables()
    app.run(debug=True, host="0.0.0.0", port=5001)

# NEW:
if __name__ == "__main__":
    create_tables()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
```

Add this import at the top of `app.py`:
```python
import os
```

### Step 2: Push code to GitHub

Initialize git (if not already done):
```bash
cd /Users/sachinsingh/GymPro
git init
git add .
git commit -m "Initial commit for GymPro deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/GymPro.git
git push -u origin main
```

### Step 3: Create Render account
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your GymPro repository
5. Fill in:
   - **Name:** `GymPro`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
6. Choose **Free Plan** (or Starter $7/month for always-on)
7. Click **Create Web Service**

### Step 4: Wait for deployment
Render will build and deploy (2-5 minutes). You'll get a URL like:
```
https://gympro-abc123.onrender.com
```

### ✅ Your website is live!
- Accessible from anywhere
- Mobile phones can access instantly
- Automatic HTTPS (secure)
- Free tier runs on demand (sleeps after 15 mins inactivity)

---

## Option 4: Deploy to Railway (Alternative)

Similar to Render but with slightly different interface.

### Step 1: Prepare (same as Render)
- `requirements.txt`
- `Procfile`
- Modify app.py (see Option 3)

### Step 2: Deploy
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select GymPro
5. Add environment variable:
   - Key: `PORT`
   - Value: `5001`

Done! Your app is deployed and gets a public URL.

---

## Option 5: AWS Deployment (Most Powerful)

For serious production use with full control.

### Setup via AWS:
1. Create AWS account
2. Use **EC2** for a Linux server (t2.micro = free tier)
3. SSH into server
4. Install Python, Flask, dependencies
5. Run `python app.py`
6. Assign Elastic IP
7. Access via public IP

**Cost:** Free tier for 12 months, then ~$5-10/month

---

## Security Best Practices 🔒

### Before going live:

1. **Change Flask secret key** in `app.py`:
```python
app.secret_key = "YOUR_SUPER_SECRET_KEY_MIN_32_CHARS_LONG"
```

2. **Disable debug mode** in production:
```python
app.run(debug=False)  # Not debug=True
```

3. **Use HTTPS** (automatic on Render/Railway)

4. **Database backup** - Add to your deployment:
```bash
# Backup gym.db regularly
cp gym.db gym.db.backup.$(date +%Y%m%d)
```

5. **Rate limiting** for login attempts (prevent brute force):
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # ...
```

---

## Quick Start Recommendation

### For Immediate Testing (Today):
→ **Use Option 1 (Local Network)**
- Mac and mobile on same WiFi
- Zero setup complexity
- Test with your team

### For Demo to Clients:
→ **Use Option 2 (ngrok)**
- Share URL with anyone
- Temporary access
- No server costs

### For Production Use:
→ **Use Option 3 (Render)**
- Professional deployment
- Always accessible
- Automatic HTTPS
- Free tier or $7/month starter

---

## Troubleshooting

### Mobile can't access the website

**Problem:** `Connection refused` or `Can't reach server`

**Solutions:**
1. Check both devices on **same WiFi**
2. Check firewall isn't blocking port 5001:
   ```bash
   # On Mac, allow Flask
   sudo lsof -i :5001
   ```
3. Verify IP address is correct:
   ```bash
   ifconfig | grep "inet "
   ```
4. Restart Flask server with `host="0.0.0.0"`

### Website is slow on mobile

**Solutions:**
1. Check WiFi signal strength
2. Close other apps using bandwidth
3. Try on a different network
4. For production, upgrade from free tier

### Data not persisting

**Causes:**
1. Database file path issue
2. Permission denied on `gym.db`

**Fix:**
```bash
# Check database exists
ls -la gym.db

# Check permissions
chmod 644 gym.db
```

---

## Next Steps

1. **Test locally first** (Option 1)
2. **Share ngrok URL** for quick demo (Option 2)
3. **Deploy to Render** when ready for production (Option 3)
4. **Monitor and scale** as more users join

---

## Support Commands

```bash
# Check if Flask is running
ps aux | grep "python.*app.py"

# Kill Flask server
pkill -f "python.*app.py"

# View Flask logs
tail -f flask.log

# Restart Flask
python3 app.py

# Check database health
sqlite3 gym.db ".tables"
```

---

**Your GymPro is now ready to reach mobile devices! 🎉**

Questions? Check logs with errors or reach out to Sachin Singh.
