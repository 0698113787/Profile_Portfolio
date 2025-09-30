from flask import Flask, url_for, render_template, request, redirect, session
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
from threading import Thread

# Load environment variables from .env file (only in development)
if os.path.exists('.env'):
    load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the app with environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'your-fallback-secret-key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

# Initialize Mail
mail = Mail(app)

# Async email sending function
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

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
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        subject = request.form['subject']

        # Create a Message object
        msg = Message(
            subject=f"{subject} - From {name} ({email})",
            sender=os.getenv('EMAIL_USER'),
            recipients=[os.getenv('EMAIL_USER')],
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
You can reply directly to this email to respond to {email}.
        """
        
        # Send email asynchronously in background thread
        Thread(target=send_async_email, args=(app, msg)).start()
        
        # Redirect immediately without waiting for email to send
        return redirect(url_for('sent'))
    
    # If the request method is GET, render the feedback template
    return render_template('feedback.html')

@app.route('/sent')
def sent():
    return render_template('sent.html')
    
@app.route('/fail')
def fail():
    return render_template('fail.html')

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)