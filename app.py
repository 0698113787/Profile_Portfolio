from flask import Flask, url_for, render_template, request, redirect, session, flash
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables from .env file (only in development)
if os.path.exists('.env'):
    load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the app with environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'your-fallback-secret-key'
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

# FIXED: Proper SSL/TLS configuration
mail_port = int(os.getenv('MAIL_PORT', 587))
if mail_port == 465:
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
else:
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

# ADDED: Connection timeout settings
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Initialize Mail
mail = Mail(app)

# Define routes for the application

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

@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            subject = request.form.get('subject', '').strip()

            # Validate inputs
            if not all([name, email, message, subject]):
                print("❌ Missing form fields")
                flash("Please fill in all fields", "error")
                return redirect(url_for('fail'))

            print(f"📧 Attempting to send email from {email}")
            print(f"📧 EMAIL_USER: {os.getenv('EMAIL_USER')}")
            print(f"📧 MAIL_SERVER: {app.config['MAIL_SERVER']}")
            print(f"📧 MAIL_PORT: {app.config['MAIL_PORT']}")
            print(f"📧 MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"📧 MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")

            # FIXED: Better error handling and connection test
            with mail.connect() as conn:
                msg = Message(
                    subject=f"{subject} - From {name}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[app.config['MAIL_USERNAME']],
                    reply_to=email
                )
                msg.body = f"""
Contact Form Submission:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Reply to: {email}
                """
                
                conn.send(msg)
                print(f"✅ Email sent successfully from {email}")
            
            return redirect(url_for('sent'))
            
        except Exception as e:
            # IMPROVED: More detailed error logging
            import traceback
            error_msg = str(e)
            print(f"❌ ERROR sending email: {error_msg}")
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Full traceback:\n{traceback.format_exc()}")
            
            # Check configuration
            if not os.getenv('EMAIL_USER'):
                print("❌ EMAIL_USER not set!")
            if not os.getenv('EMAIL_PASSWORD'):
                print("❌ EMAIL_PASSWORD not set!")
            
            # Check for common errors
            if "authentication failed" in error_msg.lower():
                print("❌ SMTP Authentication Failed - Check your EMAIL_PASSWORD")
                print("❌ For Gmail, you need an App Password, not your regular password")
            elif "timed out" in error_msg.lower():
                print("❌ Connection timed out - Check MAIL_SERVER and MAIL_PORT")
            elif "name or service not known" in error_msg.lower():
                print("❌ Cannot resolve MAIL_SERVER - Check your MAIL_SERVER setting")
            
            return redirect(url_for('fail'))
    
    # If the request method is GET, render the feedback template
    return render_template('feedback.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')
    
@app.route('/fail')
def fail():
    return render_template('fail.html')

# ADDED: Better health check endpoint
@app.route('/health')
def health():
    email_configured = bool(os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD'))
    
    # Test email configuration
    test_result = "not_tested"
    if email_configured:
        try:
            with mail.connect() as conn:
                test_result = "connection_success"
        except Exception as e:
            test_result = f"connection_failed: {str(e)[:100]}"
    
    return {
        'status': 'healthy',
        'email_configured': email_configured,
        'email_user': os.getenv('EMAIL_USER', 'not_set'),
        'mail_server': app.config['MAIL_SERVER'],
        'mail_port': app.config['MAIL_PORT'],
        'mail_use_tls': app.config.get('MAIL_USE_TLS'),
        'mail_use_ssl': app.config.get('MAIL_USE_SSL'),
        'smtp_test': test_result
    }, 200

# ADDED: Test email endpoint for debugging
@app.route('/test-email')
def test_email():
    """Test endpoint to check email configuration"""
    try:
        msg = Message(
            subject="Test Email from Render",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]
        )
        msg.body = "This is a test email to verify SMTP configuration."
        
        mail.send(msg)
        return {"status": "success", "message": "Test email sent!"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)