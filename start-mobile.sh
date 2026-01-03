#!/bin/bash

# GymPro Mobile Access Setup Script
# This script helps you access GymPro from mobile phones

echo "🏋️  GymPro Mobile Access Setup"
echo "=================================="
echo ""

# Get local IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ Could not find your local IP address"
    echo "Make sure you're connected to WiFi"
    exit 1
fi

echo "✅ Your local IP address: $LOCAL_IP"
echo ""
echo "📱 Access GymPro from mobile phones:"
echo "   http://$LOCAL_IP:5001"
echo ""
echo "Instructions:"
echo "1. Make sure your mobile phone is on the SAME WiFi network"
echo "2. Open a web browser on your phone"
echo "3. Enter: http://$LOCAL_IP:5001"
echo "4. You should see GymPro login page!"
echo ""
echo "Starting Flask server..."
echo ""

# Stop any running Flask servers
pkill -f "python.*app.py" 2>/dev/null
sleep 1

# Start the Flask server
cd /Users/sachinsingh/GymPro
python3 app.py
