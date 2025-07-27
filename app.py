from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ import CORS
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
# CORS(app)  # ✅ allow all origins
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
    msg.set_content(f"Your OTP is: {otp}")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient

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
