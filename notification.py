import smtplib
from email.message import EmailMessage
from twilio.rest import Client

# Email configuration
EMAIL_ADDRESS = "your_email@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "your_email_password"  # Use App Password if using Gmail

# Twilio Configuration
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE = "+1234567890"  # Your Twilio number

def send_email(to_email, name, date, time, guests):
    """Send reservation confirmation via email."""
    msg = EmailMessage()
    msg.set_content(f"Hello {name},\n\nYour reservation for {guests} guests on {date} at {time} is confirmed!\n\nThank you!")
    
    msg["Subject"] = "Reservation Confirmation"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_sms(to_phone, name, date, time, guests):
    """Send reservation confirmation via SMS."""
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=f"Hello {name}, your reservation for {guests} guests on {date} at {time} is confirmed!",
        from_=TWILIO_PHONE,
        to=to_phone
    )
    
    print("SMS sent successfully!" if message.sid else "Error sending SMS.")
