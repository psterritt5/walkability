from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from processor.Processor import Processor
import os
import json

app = Flask(__name__, template_folder="ui/templates")

# Load API keys
def load_api_keys():
    keys = {}
    with open(os.path.join(os.path.dirname(__file__), 'api_keys.txt'), 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=')
                keys[key] = value
    return keys

api_keys = load_api_keys()
app.secret_key = api_keys['FLASK_SECRET_KEY']

# MongoDB instance
app.config["MONGO_URI"] = "mongodb://localhost:27017/walkability"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
users_collection = mongo.db.users

# Store Google Maps API key in app config
app.config['GOOGLE_MAPS_API_KEY'] = api_keys['GOOGLE_MAPS_API_KEY']


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        address = request.form["address"]
        return redirect(url_for('result', address=address))
    return render_template('index.html')


@app.route("/result", methods=['GET', 'POST'])
def result():
    address = request.args.get('address') or request.form.get('address')
    if not address:
        flash("Please enter an address")
        return redirect(url_for('home'))
    
    try:
        # Initialize processor and get results
        processor = Processor(address)
        score, interpretation = processor.process_location(address)
        
        # Get the GPS coordinates for the map
        data_fetcher = processor.data_fetcher
        if not data_fetcher or not data_fetcher.gps_coordinates:
            flash("Could not find the specified address. Please try a different address.")
            return redirect(url_for('home'))
            
        lat, lng = data_fetcher.gps_coordinates
        print(f"Processing address: {address}, coordinates: ({lat}, {lng})")

        # Prepare category data with icons and place details
        categories = []
        category_icons = {
            'grocery': 'fa-shopping-cart',
            'eat_out': 'fa-utensils',
            'public_transit': 'fa-bus',
            'health_and_well_being': 'fa-heartbeat'
        }
        
        category_markers = {
            'grocery': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
            'eat_out': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
            'public_transit': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
            'health_and_well_being': 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png'
        }

        places_by_category = data_fetcher.get_places_by_category()
        print(f"Found places by category: {places_by_category}")
        
        for category_name in data_fetcher.CATEGORY_NAMES:
            places = places_by_category.get(category_name, set())
            places_with_coords = []
            
            # Get coordinates for each place
            for place_name in places:
                place_id = None
                for pid, details in data_fetcher.place_details.items():
                    if details['name'] == place_name:
                        place_id = pid
                        break
                
                if place_id and place_id in data_fetcher.place_details:
                    place_details = data_fetcher.place_details[place_id]
                    location = place_details.get('location', {})
                    if location and 'lat' in location and 'lng' in location:
                        places_with_coords.append({
                            'name': place_name,
                            'lat': location['lat'],
                            'lng': location['lng']
                        })
            
            categories.append({
                'name': category_name.replace('_', ' ').title(),
                'count': len(places),
                'places': sorted(places),
                'places_with_coords': places_with_coords,
                'icon': category_icons.get(category_name, 'fa-map-marker'),
                'marker_icon': category_markers.get(category_name)
            })

        # Check if we have a valid API key
        api_key = app.config.get('GOOGLE_MAPS_API_KEY')
        if not api_key:
            flash("Google Maps API key is not configured. Map functionality will be limited.")
            print("Warning: No Google Maps API key found")
        else:
            print("Using Google Maps API key:", api_key[:10] + "...")
            
        return render_template(
            "result.html",
            address=address,
            score=score,
            interpretation=interpretation.split('\n\n')[0],  # Just the score interpretation
            categories=categories,
            lat=lat,
            lng=lng,
            google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY']  # Pass the API key directly
        )
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        flash("Error processing address. Please try a different address.")
        return redirect(url_for('home'))


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
            address = request.form['address']
            rental_cost = request.form['rental_cost']
            notes = request.form['notes']
            
            try:
                processor = Processor(address)
                score, interpretation = processor.process_location(address)
                
                # Prepare favorite location data
                favorite_data = {
                    'address': address,
                    'rental_cost': rental_cost,
                    'notes': notes,
                    'walkability_score': score,
                    'walkability_details': interpretation
                }

                # Append to the user's favorites in MongoDB
                users_collection.update_one(
                    {'username': session['user']},
                    {'$push': {'favorites': favorite_data}}
                )

                flash('Location added to favorites successfully!')
            except Exception as e:
                flash('Error processing address. Please try again.')
                
        return redirect(url_for('dashboard'))
    else:
        flash('Please log in to save favorites.')
        return redirect(url_for('login'))


@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user' in session:
        user = users_collection.find_one({'username': session['user']})
        if user:
            address = request.form['address']

            # Remove the favorite with the matching address
            users_collection.update_one(
                {'username': session['user']},
                {'$pull': {'favorites': {'address': address}}}
            )

            flash('Favorite location removed successfully!')
        return redirect(url_for('dashboard'))
    else:
        flash('Please log in to access this feature.')
        return redirect(url_for('login'))

app.run(host="0.0.0.0", port=80)
