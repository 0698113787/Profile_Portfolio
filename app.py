from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')


# FLASK-MAIL CONFIGURATION FOR GMAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('GMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('GMAIL_USER')

# Initialize Flask-Mail
mail = Mail(app)


#routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/certificates')
def certificates():
    return render_template('certificates.html')

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate inputs
        if not all([name, email, subject, message]):
            print("❌ Missing form fields")
            return redirect(url_for('fail'))
        
        try:
            print(f"📧 Sending email from contact form...")
            print(f"📧 Visitor: {name} ({email})")
            
            # Create email message
            msg = Message(
                subject=f"Portfolio Contact: {subject}",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[os.getenv('GMAIL_USER')],
                reply_to=email
            )
            
            # Email body
            msg.body = f"""
New Contact Form Submission

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Reply directly to: {email}
            """
            
            # HTML email (optional but looks better)
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #4a90e2;">New Contact Form Submission</h2>
                    <div style="background: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>From:</strong> {name}</p>
                        <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                        <p><strong>Subject:</strong> {subject}</p>
                    </div>
                    <div style="background: white; padding: 20px; border-left: 4px solid #4a90e2;">
                        <h3>Message:</h3>
                        <p style="white-space: pre-wrap;">{message}</p>
                    </div>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #888; font-size: 14px;">
                        Reply directly to: <a href="mailto:{email}">{email}</a>
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Send email
            mail.send(msg)
            print(f"✅ Email sent successfully!")
            
            return redirect(url_for('sent'))
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print(f"❌ Error Type: {type(e).__name__}")
            
            import traceback
            print(f"❌ Full Traceback:\n{traceback.format_exc()}")
            
            # Debug info
            if not os.getenv('GMAIL_USER'):
                print("❌ GMAIL_USER not set in .env!")
            if not os.getenv('GMAIL_APP_PASSWORD'):
                print("❌ GMAIL_APP_PASSWORD not set in .env!")
            
            return redirect(url_for('fail'))
    
    return render_template('feedback.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')

@app.route('/fail')
def fail():
    return render_template('fail.html')

@app.route('/test-email')
def test_email():
    """Test your Gmail configuration"""
    try:
        msg = Message(
            subject="Test Email - Portfolio Website",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[os.getenv('GMAIL_USER')]
        )
        msg.body = "This is a test email. If you receive this, your Gmail SMTP is configured correctly!"
        
        mail.send(msg)
        return {
            "status": "success", 
            "message": "Test email sent! Check your inbox."
        }, 200
        
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, 500

@app.route('/health')
def health():
    """Check if email is configured"""
    gmail_user = os.getenv('GMAIL_USER')
    gmail_pass = os.getenv('GMAIL_APP_PASSWORD')
    
    return {
        'status': 'healthy',
        'gmail_configured': bool(gmail_user and gmail_pass),
        'gmail_user': gmail_user if gmail_user else 'NOT SET',
        'mail_server': app.config['MAIL_SERVER'],
        'mail_port': app.config['MAIL_PORT']
    }, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)