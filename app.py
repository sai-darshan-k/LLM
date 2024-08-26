import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from werkzeug.utils import secure_filename
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import logging
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sign up'  # Your database name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the language model
groqllm = ChatGroq(model="llama3-8b-8192", temperature=0)
prompt = """(system: You are a cyber security assistant specialized only with cyber security amd ethical hacking. If the user's question is related to cyber secutity, vulnerabilities, netwok security, ethical hacking concepts provide a detailed and helpful response. If the question is not related to cyber security and related, respond with "I'm sorry, I can only assist with Cyber Security queries.)
(user: Question: {question})"""
promptinstance = ChatPromptTemplate.from_template(prompt)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Authenticate user
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            flash('', 'success')
            return redirect(url_for('cybercare')) 
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Hash the password
        new_user = User(email=email, password=hashed_password)
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/cybercare')
def cybercare():
    if 'user_id' not in session:  # Check if user is logged in
        flash('You need to log in to access this page.', 'danger')
        return redirect(url_for('login'))
    return render_template('cybercare.html')


@app.route('/speech')
def speech():
    if 'user_id' not in session:  # Check if user is logged in
        flash('You need to log in to access this page.', 'danger')
        return redirect(url_for('login'))
    return render_template('speech.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    logging.info(f"Received question: {question}")
    try:
        response = promptinstance | groqllm | StrOutputParser()
        answer = response.invoke({'question': question})

        formatted_answer = format_answer(answer)
        logging.info(f"Response generated: {formatted_answer}")
        return jsonify({'answer': formatted_answer})
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return jsonify({'answer': f'Error processing your request: {str(e)}'}), 500

def format_answer(answer):
    answer = answer.replace("**", "<strong>").replace("**", "</strong>")
    formatted_answer = "<div style='text-align: left;'>"
    lines = answer.split('\n')
    for line in lines:
        if line.strip():
            formatted_answer += f"<p>{line.strip()}</p>"
    formatted_answer += "</div>"
    return formatted_answer

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True, port=5000)
