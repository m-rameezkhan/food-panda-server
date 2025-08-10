from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import os
import random
import time

app = Flask(__name__)
CORS(app, origins=[
    "https://rameez-foodpanda.netlify.app",
    "http://127.0.0.1:5500"
])

# Store OTPs temporarily in memory
otp_storage = {}  # {email: {"otp": 123456, "timestamp": 1723456789}}

@app.route('/')
def home():
    return "Server is running!"

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    recipient = data.get("email")

    if not recipient:
        return jsonify({"success": False, "message": "Email is required"}), 400

    # Generate OTP
    otp = random.randint(100000, 999999)
    otp_storage[recipient] = {
        "otp": otp,
        "timestamp": time.time()
    }

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = "Your Food Panda Account OTP Verification Code"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg.set_content(f"""
Dear User,

We have received a request to verify your identity for your Food Panda account.

🔐 Your One-Time Password (OTP) is: {otp}

This code is valid for the next 5 minutes.

If you did not request this, please ignore this email.

Best regards,  
Food Panda Team  
https://rameez-foodpanda.netlify.app
""")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return jsonify({"success": True, "message": "OTP sent"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"success": False, "message": "Email and OTP are required"}), 400

    stored = otp_storage.get(email)
    if not stored:
        return jsonify({"success": False, "message": "No OTP found"}), 400

    if time.time() - stored["timestamp"] > 300:  # 5 minutes expiry
        del otp_storage[email]
        return jsonify({"success": False, "message": "OTP expired"}), 400

    if str(stored["otp"]) == str(otp):
        del otp_storage[email]
        return jsonify({"success": True, "message": "OTP verified"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400

if __name__ == "__main__":
    app.run(debug=True)
