from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
from dotenv import load_dotenv
import os



load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure PostgreSQL
# Use environment variables
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Fallback if SECRET_KEY is missing
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')  # Fallback to SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    password = db.Column(db.String(200), nullable=False)

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        dogs = [
            {"id": 1, "name": "Buddy", "breed": "Labrador", "age": "3 Years", "image": "dog1.jpg"},
            {"id": 2, "name": "Max", "breed": "Golden Retriever", "age": "2 Years", "image": "dog2.jpg"},
            {"id": 3, "name": "Luna", "breed": "Beagle", "age": "4 Years", "image": "dog3.jpg"},
            {"id": 4, "name": "Charlie", "breed": "German Shepherd", "age": "5 Years", "image": "dog4.jpg"},
            {"id": 5, "name": "Bella", "breed": "Poodle", "age": "2 Years", "image": "dog5.jpg"}
        ]
        return render_template('index.html', user=user, dogs=dogs)
    return redirect(url_for('login'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        address = request.form['address']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Add new user to database
        try:
            new_user = User(username=username, full_name=full_name, email=email, address=address, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists. Try again.', 'danger')
    return render_template('register.html')

@app.route('/dog/<int:dog_id>', methods=['GET', 'POST'])

@login_required
def dog_profile(dog_id):
    # Simulating a database or dictionary for demo purposes
    dogs = [
        {"id": 1, "name": "Buddy", "breed": "Labrador", "age": "3 Years", "color": "Golden", "image": "dog1.jpg"},
        {"id": 2, "name": "Max", "breed": "Golden Retriever", "age": "2 Years", "color": "Cream", "image": "dog2.jpg"},
        {"id": 3, "name": "Luna", "breed": "Beagle", "age": "4 Years", "color": "Tricolor", "image": "dog3.jpg"},
        {"id": 4, "name": "Charlie", "breed": "German Shepherd", "age": "5 Years", "color": "Black & Tan", "image": "dog4.jpg"},
        {"id": 5, "name": "Bella", "breed": "Poodle", "age": "2 Years", "color": "White", "image": "dog5.jpg"},
    ]

    # Find the specific dog by ID
    dog = next((d for d in dogs if d["id"] == dog_id), None)

    if dog is None:
        return "Dog not found", 404

    user = db.session.get(User, session['user_id'])  # Get the logged-in user
    return render_template('dog_profile.html', dog=dog, user=user)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')


if __name__ == '__main__':
    # Ensure database tables are created within an application context
    with app.app_context():
        db.create_all()
    app.run(debug=True)


@app.route('/adopt/<int:dog_id>', methods=['POST'])
@login_required
def adopt_dog(dog_id):
    # Simulating adoption logic
    flash(f'You have successfully adopted the dog!', 'success')
    return redirect(url_for('dog_profile', dog_id=dog_id))


@app.route('/delete/<int:dog_id>', methods=['POST'])
def delete_dog(dog_id):
    flash(f'Dog with ID {dog_id} has been deleted!', 'danger')
    return redirect(url_for('home'))

