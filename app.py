from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_security import SQLAlchemyUserDatastore, Security, hash_password, verify_password
from flask_sqlalchemy import SQLAlchemy
from configuration import DevelopmentConfig
from model import db, User, Role


def initialize():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    app.app_context().push()
    API = Api(app)
    CORS(app)
    return app, API, datastore


app, API, datastore = initialize()
from api import *
API.add_resource(Categories, '/categories', '/categories/<cate_id>')
API.add_resource(Cart_items, '/cart/<username>')
API.add_resource(Products, '/products/<cate_id>', '/products')


@app.post("/user-login")
def login():
    data = request.json
    user = datastore.find_user(email=data['email'])
    if not user:
        return jsonify({"error": "No user found"})
    if verify_password(data['password'], user.password):
        return jsonify({"message": "Success", "email": user.email, "token": user.get_auth_token(), "role": user.roles[0].name})
    return jsonify({"error": "Incorrect password!"})


@app.post("/user-signup")
def signup():
    data = request.json
    print(data)
    username = data['username']
    email = data['email']
    password = data['password']
    role_name = data['role']
    role_name = role_name.lower()
    try:
        if not email or not password or not role_name:
            return jsonify({"error": "Missing required fields!"}), 400
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({"error": "Invalid role!"}), 400
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists!"}), 400
        hashed_password = hash_password(password)
        datastore.create_user(username=username, email=email, password=hashed_password, roles=[role])
        db.session.commit()
        user = datastore.find_user(email=data['email'])
        return jsonify({"message": "Success", "email": user.email, "token": user.get_auth_token(), "role": user.roles[0].name})
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True)
