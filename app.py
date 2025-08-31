# app.py
# Main file for our Flask backend

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

# --- Basic Setup ---

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing) to allow our React frontend 
# to communicate with this backend.
CORS(app)

# --- In-Memory Database (for simplicity) ---
# In a real application, you would use a proper database like PostgreSQL or MongoDB.
# Here, we're just using a Python dictionary to store user data.
users = {} # Will store users like: {"username": "password"}


# --- API Endpoints ---

@app.route("/")
def index():
    """
    A simple route to check if the server is running.
    """
    return jsonify({"message": "Backend server is running!"})


# --- Authentication Routes ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Handles user registration.
    Expects a JSON payload with 'username' and 'password'.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        # Return a 400 Bad Request error if data is missing
        return jsonify({"message": "Username and password are required"}), 400

    if username in users:
        # Return a 409 Conflict error if the user already exists
        return jsonify({"message": "User already exists"}), 409

    # Add the new user to our in-memory database
    users[username] = password
    print(f"Registered new user: {username}") # Log for debugging
    
    # Return a 201 Created success message
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Handles user login.
    Expects a JSON payload with 'username' and 'password'.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Check if the user exists and the password is correct
    if username not in users or users[username] != password:
        # Return a 401 Unauthorized error for bad credentials
        return jsonify({"message": "Invalid credentials"}), 401

    print(f"User logged in: {username}") # Log for debugging
    
    # In a real app, you would return a JWT token here.
    # For simplicity, we'll just return a success message.
    return jsonify({"message": "Login successful", "username": username})


# --- File Processing Route ---

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """
    Handles the Excel file upload and processing.
    Expects the file to be sent as 'multipart/form-data'.
    """
    # Check if a file was included in the request
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']

    # Check if the user selected a file
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    # Check if the file is an Excel file
    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        try:
            # Use pandas to read the Excel file directly from memory
            df = pd.read_excel(file)

            # Get the column headers
            headers = df.columns.tolist()

            # Get the row data (converted to a list of dictionaries)
            data = df.to_dict(orient='records')
            
            print(f"Successfully processed file: {file.filename}") # Log for debugging

            # Return the extracted headers and data as JSON
            return jsonify({
                "message": "File processed successfully",
                "filename": file.filename,
                "headers": headers,
                "data": data
            })
        except Exception as e:
            # Handle any errors during file processing
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"message": "Invalid file type. Please upload an Excel file (.xlsx or .xls)"}), 400


# --- Main Execution ---

if __name__ == '__main__':
    """
    This block runs the Flask app.
    'debug=True' allows the server to auto-reload when you save changes.
    'port=5000' sets the server to run on http://localhost:5000
    """
    app.run(debug=True, port=5000)
