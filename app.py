from flask import Flask,send_from_directory
from flask_migrate import Migrate
from server.config import Config
from server.models.models import db, User, Destination 
from flask_cors import CORS
from flask import Flask, request, jsonify
import os
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import bcrypt
# from faker import Faker
from flask import request


app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
app.config.from_object(Config)
CORS(app, supports_credentials=True)
#Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
jwt = JWTManager(app)
# Initialize DB before running migrations
db.init_app(app)  
migrate = Migrate(app, db)
# Create the tables in the database 
with app.app_context():
    db.create_all()

#routes
@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

# @app.route('/users')
# def get_users():
#     users = User.query.all()
#     return {"users": [user.to_dict() for user in users]}

# @app.route('/users/<int:id>')
# def get_user(id):
#     user = User.query.get(id)
#     return user.to_dict()

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()  # Get JSON data from request
        fname = data.get("fname")
        sname = data.get("sname")
        email = data.get("email")
        password = data.get("password")
        role_id = data.get("role_id", 2)  # Default role is 2 (user)
        # Perform validation
        if not data:
            return {"error": "Invalid request, no data provided"}, 400
        # Check if required fields are present
        if not fname or not sname or not email or not password:
            return {"error": "Invalid request, missing required data"}, 400
        # First name and surname length validation
        if len(fname) < 3 or len(sname) < 3:
            return {"error": "First name and surname must be at least 3 characters long each"}, 400
        # First name and surname character validation
        if not fname.isalpha() or not sname.isalpha():
            return {"error": "First name and surname must contain only letters"}, 400
        # Password validation
        if len(password) < 6:
            return {"error": "Password must be at least 6 characters"}, 400
        if password.isalpha() or password.isdigit():
            return {"error": "Password must contain both letters and numbers"}, 400
        #email validation
        if "@" not in email or "." not in email:
            return {"error": "Invalid email"}, 400
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return {"error": "Invalid request, email already exists"}, 400
        # Hash password
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Create new user object
        new_user = User(fname=fname, sname=sname, email=email, password=password, role_id=role_id)

        db.session.add(new_user)  # Add new user to database session
        db.session.commit()

        return new_user.to_dict(), 201  # Return user object with success code

    except Exception as e:
        print("Error:", e) # Print any errors to console
        return {"error": str(e)}, 500

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()  # Get JSON data from request
        email = data.get("email")
        password = data.get("password")
        # Perform validation
        if not data:
            return {"error": "Invalid request, no data provided"}, 400
        if not email or not password:
            return {"error": "Invalid request, missing required data"}, 400
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"error": "Invalid email or password"}, 400
        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            return {"error": "Invalid email or password"}, 400
        #create JWT access token    
        access_token=create_access_token(identity={"id": user.id, "role_id": user.role_id})

        return {"token": access_token, "user": user.to_dict()}, 200
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}, 500
#protected route
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity() # Get the identity of the current user
    user_id=current_user["id"]
    role_id = current_user["role_id"]
    user = User.query.get(current_user["id"])
    if not user:
        return {"error": "User not found"}, 404
    return jsonify({
        "message": "You are authorized",
        "user": user.to_dict(),
        "role":"admin" if role_id==1 else "user"
    }),200

@app.route('/destinations')
def get_destinations():
    destinations = Destination.query.all()
    return {"destinations": [destination.to_dict() for destination in destinations]}

#get a single destination
@app.route('/destinations/<int:id>', methods=['GET'])
@jwt_required()
def get_destination(id):
    destination = Destination.query.get(id)
    if not destination:
        return jsonify({"error": "Destination not found"}), 404

    return jsonify(destination.to_dict()), 200

@app.route('/destinations', methods=['POST'])
def add_destinations():
    try:
        data = request.get_json() 
        if not data or not isinstance(data, list):
            return {"error": "Invalid request, expected a list of destinations"}, 400

        new_destinations = []
        
        for item in data:
            name = item.get("name")
            description = item.get("description")
            category = item.get("category")
            safety_rating = item.get("safety_rating")
            activities = item.get("activities")
            image = item.get("image")

            # Validate required fields
            if not name or not description or not category or not safety_rating or not activities or not image:
                return {"error": f"Invalid request, missing required data for {name}"}, 400

            new_destination = Destination(
                name=name,
                description=description,
                category=category,
                safety_rating=safety_rating,
                activities=activities,
                image=image
            )
            db.session.add(new_destination)
            new_destinations.append(new_destination)

        db.session.commit()

        return {"message": f"Successfully added {len(new_destinations)} destinations", 
                "destinations": [dest.to_dict() for dest in new_destinations]}, 201

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}, 500
#admin routes
@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    current_user = get_jwt_identity()
    role_id = current_user["role_id"]
    user = User.query.get(current_user["id"])
    if not user:
        return {"error": "User not found"}, 404
    if role_id != 1:
        return {"error": "You are not authorized to access this route"}, 401
    return jsonify({
        "message": "You are authorized",
        "user": user.to_dict(),
        "role":"admin" if role_id==1 else "user"
    }),200

@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    role_id = current_user["role_id"]
    if role_id != 1:
        return {"error": "You are not authorized to access this route"}, 401
    users = User.query.all()
    return {"users": [user.to_dict() for user in users]}
@app.route('/admin/destinations', methods=['GET'])
@jwt_required()
def get_admin_destinations():
    current_user = get_jwt_identity()
    role_id = current_user["role_id"]
    if role_id != 1:
        return {"error": "You are not authorized to access this route"}, 401
    destinations = Destination.query.all()
    return {"destinations": [destination.to_dict() for destination in destinations]}

if __name__ == '__main__':
    app.run(debug=True)
