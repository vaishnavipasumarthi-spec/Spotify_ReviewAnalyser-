import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

def draft_email():
    report_path = 'reports/weekly_note.md'
    if not os.path.exists(report_path):
        print(f"Error: {report_path} not found.")
        return
        
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
        
    # Email configuration from .env (Optional for now)
    sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
    receiver_email = os.getenv("RECEIVER_EMAIL", sender_email) # Send to self by default
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_password = os.getenv("SMTP_PASSWORD") # App Password if using Gmail
    
    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Weekly Spotify Review Discovery Note"
    
    # Convert Markdown to simple HTML or just use plain text
    # Here we'll use plain text for simplicity as a "draft"
    message.attach(MIMEText(report_content, "plain"))
    
    print("\n--- EMAIL DRAFT PREVIEW ---")
    print(f"From: {sender_email}")
    print(f"To: {receiver_email}")
    print(f"Subject: {message['Subject']}")
    print("-" * 30)
    print(report_content[:500] + "...") # Show first 500 chars
    print("-" * 30)
    
    if smtp_password and smtp_password != "your_smtp_password_here":
        try:
            print("Attempting to send email...")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, smtp_password)
                server.send_message(message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
            print("Tip: If using Gmail, ensure you have 'App Passwords' set up.")
    else:
        print("\n[NOTE] SMTP_PASSWORD not configured in .env. Email was NOT sent.")
        print("To send the email, add SENDER_EMAIL, RECEIVER_EMAIL, and SMTP_PASSWORD to your .env file.")

if __name__ == "__main__":
    draft_email()
