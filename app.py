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
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp-relay.brevo.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'vuyiswaandile176@gmail.com'

# Additional mail settings
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
                return redirect(url_for('fail'))

            print(f"📧 Attempting to send email from {email}")
            print(f"📧 EMAIL_USER: {os.getenv('EMAIL_USER')}")
            print(f"📧 MAIL_SERVER: {app.config['MAIL_SERVER']}")
            print(f"📧 MAIL_PORT: {app.config['MAIL_PORT']}")

            # Create and send email
            msg = Message(
                subject=f"{subject} - From {name}",
                sender='vuyiswaandile176@gmail.com',
                recipients=['vuyiswaandile176@gmail.com'],
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
            
            mail.send(msg)
            print(f"✅ Email sent successfully from {email}")
            return redirect(url_for('sent'))
            
        except Exception as e:
            # Detailed error logging
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
            
            return redirect(url_for('fail'))
    
    # If the request method is GET, render the feedback template
    return render_template('feedback.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')
    
@app.route('/fail')
def fail():
    return render_template('fail.html')

# Health check endpoint
@app.route('/health')
def health():
    email_configured = bool(os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD'))
    
    return {
        'status': 'healthy',
        'email_configured': email_configured,
        'email_user': os.getenv('EMAIL_USER', 'not_set'),
        'mail_server': app.config['MAIL_SERVER'],
        'mail_port': app.config['MAIL_PORT']
    }, 200

# Test email endpoint for debugging
@app.route('/test-email')
def test_email():
    """Test endpoint to check email configuration"""
    try:
        msg = Message(
            subject="Test Email from Render",
            sender='vuyiswaandile176@gmail.com',
            recipients=['vuyiswaandile176@gmail.com']
        )
        msg.body = "This is a test email to verify SMTP configuration with Brevo."
        
        mail.send(msg)
        return {"status": "success", "message": "Test email sent!"}, 200
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }, 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)