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

# Store OTPs temporarily: {email: {"otp": "123456", "timestamp": 1690000000}}
otp_storage = {}

@app.route('/')
def home():
    return "Server is running!"

# Generate and send OTP
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    recipient = data.get("email")

    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store OTP with timestamp
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

    # Set HTML email body (bold OTP)
    msg.set_content(f"""
Dear User,

Your OTP is: {otp}

(Plain text version – if HTML not supported)
""")
    msg.add_alternative(f"""
<html>
<body>
<p>Dear User,</p>

<p>We have received a request to verify your identity for your Food Panda account.</p>

<p>🔐 Your One-Time Password (OTP) is: <b>{otp}</b></p>

<p>Please enter this OTP to complete your verification process. This code is valid for the next 5 minutes.</p>

<p>Why you're receiving this email:<br>
You (or someone using your email) initiated a password reset or login verification on the Food Panda platform.</p>

<p>If you did not request this, please ignore this email. Your account is safe, and no changes have been made.</p>

<p>If you continue to receive such emails without initiating them, we recommend changing your password or contacting our support team.</p>

<p>Best regards,<br>
<b>Food Panda Team</b><br>
<a href="https://rameez-foodpanda.netlify.app">Visit our website</a></p>
</body>
</html>
""", subtype="html")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return jsonify({"success": True, "message": "OTP sent"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# Verify OTP
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    recipient = data.get("email")
    user_otp = data.get("otp")

    # Check if OTP exists
    if recipient not in otp_storage:
        return jsonify({"success": False, "message": "No OTP found for this email"})

    stored_otp_data = otp_storage[recipient]
    stored_otp = stored_otp_data["otp"]
    timestamp = stored_otp_data["timestamp"]

    # Check if OTP expired (5 minutes)
    if time.time() - timestamp > 300:
        del otp_storage[recipient]
        return jsonify({"success": False, "message": "OTP expired"})

    # Check if OTP matches
    if user_otp == stored_otp:
        del otp_storage[recipient]  # Remove after successful verification
        return jsonify({"success": True, "message": "OTP verified successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP"})

if __name__ == "__main__":
    app.run()
