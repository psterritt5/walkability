from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS  # To handle cross-origin requests

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = open('SECRET_KEY.txt', 'r').read()

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/walkability"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Allow Cross-Origin Requests (CORS) from React frontend
CORS(app)

# Import routes after initializing app and dependencies
import routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
