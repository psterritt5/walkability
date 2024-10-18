from flask import request, jsonify, session
from app import app, mongo, bcrypt
from processor.Processor import Processor

users_collection = mongo.db.users

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to Walkability API!"})


@app.route("/result", methods=['POST'])
def result():
    data = request.get_json()
    coordinates = data.get('coordinates')

    try:
        result = obtain_result(coordinates)
        return jsonify({"coordinates": coordinates, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def obtain_result(coordinates):
    processor = Processor(gps_coordinates=coordinates)
    return processor.process_location()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    existing_user = users_collection.find_one({
        '$or': [{'username': username}, {'email': email}]
    })
    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    users_collection.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password
    })

    return jsonify({"message": "Registration successful"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = users_collection.find_one({'username': username})

    if user and bcrypt.check_password_hash(user['password'], password):
        session['user'] = username
        return jsonify({"message": "Login successful", "username": username})
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' in session:
        user = users_collection.find_one({'username': session['user']})
        if user:
            favorites = user.get('favorites', [])
            return jsonify({"favorites": favorites})
    return jsonify({"error": "Unauthorized access"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out successfully"})


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'user' in session:
        data = request.get_json()
        coordinates = data['coordinates']
        address = data['address']
        rental_cost = data['rental_cost']
        notes = data['notes']
        walkability_score = obtain_result(coordinates)

        favorite_data = {
            'coordinates': coordinates,
            'address': address,
            'rental_cost': rental_cost,
            'notes': notes,
            'walkability_score': walkability_score
        }

        users_collection.update_one(
            {'username': session['user']},
            {'$push': {'favorites': favorite_data}}
        )

        return jsonify({"message": "Favorite added successfully"}), 201
    return jsonify({"error": "Unauthorized access"}), 401


@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user' in session:
        data = request.get_json()
        coordinates = data['coordinates']

        users_collection.update_one(
            {'username': session['user']},
            {'$pull': {'favorites': {'coordinates': coordinates}}}
        )

        return jsonify({"message": "Favorite removed successfully"}), 200
    return jsonify({"error": "Unauthorized access"}), 401
