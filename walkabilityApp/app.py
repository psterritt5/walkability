from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from walkabilityApp.processor.Processor import Processor

app = Flask(__name__, template_folder="ui/templates")
app.secret_key = open('SECRET_KEY.txt', 'r').read()

# MongoDB instance
app.config["MONGO_URI"] = "mongodb://localhost:27017/walkability"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
users_collection = mongo.db.users


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        coordinates = request.form["coordinates"]
        return redirect(url_for('result', name=coordinates))
    return render_template('index.html')


@app.route("/result", methods=['GET', 'POST'])
def result():
    coordinates = request.form.get('coordinates')
    try:
        result = obtain_result(coordinates)
    except:
        result = "Invalid coordinates. Try again by returning to the home page."
    return render_template("result.html", result=result,
                           coordinates=coordinates)


def obtain_result(coordinates):
    processor = Processor(gps_coordinates=coordinates)
    return processor.process_location()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists
        existing_user = users_collection.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            flash('Username or email already exists. Please try a different one.')
            return redirect(url_for('register'))

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store the new user
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user in the database
        user = users_collection.find_one({'username': username})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = username
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = users_collection.find_one({'username': session['user']})
        if user:
            favorites = user.get('favorites', [])
            return render_template('dashboard.html', username=session['user'], favorites=favorites)
    flash('Please log in to access the dashboard.')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'user' in session:
        user = users_collection.find_one({'username': session['user']})
        if user:
            coordinates = request.form['coordinates']
            address = request.form['address']
            rental_cost = request.form['rental_cost']
            notes = request.form['notes']
            walkability_score = obtain_result(
                coordinates)  # Assuming this returns the score

            # Prepare favorite location data
            favorite_data = {
                'coordinates': coordinates,
                'address': address,
                'rental_cost': rental_cost,
                'notes': notes,
                'walkability_score': walkability_score
            }

            # Append to the user's favorites in MongoDB
            users_collection.update_one(
                {'username': session['user']},
                {'$push': {'favorites': favorite_data}}
            )

            flash('Location added to favorites successfully!')
        return redirect(url_for('dashboard'))
    else:
        flash('Please log in to save favorites.')
        return redirect(url_for('login'))


@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user' in session:
        user = users_collection.find_one({'username': session['user']})
        if user:
            coordinates = request.form['coordinates']

            # Remove the favorite with the matching coordinates
            users_collection.update_one(
                {'username': session['user']},
                {'$pull': {'favorites': {'coordinates': coordinates}}}
            )

            flash('Favorite location removed successfully!')
        return redirect(url_for('dashboard'))
    else:
        flash('Please log in to access this feature.')
        return redirect(url_for('login'))

app.run(host="0.0.0.0", port=80)
