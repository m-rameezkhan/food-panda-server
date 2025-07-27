from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
CORS(app, origins=["https://rameez-foodpanda.netlify.app"])

@app.route('/')
def home():
    return "Server is running!"

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    recipient = data.get("email")
    otp = data.get("otp")

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = "Your Food Panda Account OTP Verification Code"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient

    # Set detailed email body
    msg.set_content(f"""
Dear User,

We have received a request to verify your identity for your Food Panda account.

🔐 Your One-Time Password (OTP) is: {otp}

Please enter this OTP to complete your verification process. This code is valid for the next 5 minutes.

Why you're receiving this email:
You (or someone using your email) initiated a password reset or login verification on the Food Panda platform.

If you did not request this, please ignore this email. Your account is safe, and no changes have been made.

If you continue to receive such emails without initiating them, we recommend changing your password or contacting our support team.

Best regards,  
Food Panda Team  
https://rameez-foodpanda.netlify.app  
support@foodpanda.example.com
""")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return jsonify({"success": True, "message": "OTP sent"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run()
