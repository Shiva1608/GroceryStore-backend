from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
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
    migrate = Migrate(app, db)
    return app, API, datastore, migrate


app, API, datastore, migrate = initialize()
from api import *


@app.post("/user-login")
def login():
    data = request.json
    user = datastore.find_user(email=data['email'])
    if not user:
        return jsonify({"error": "No user found"})
    elif verify_password(data['password'], user.password):
        if not user.active:
            return jsonify({"error": "Not yet approved by admin!"})
        return jsonify(
            {"message": "Success", "email": user.email, "token": user.get_auth_token(), "role": user.roles[0].name})
    return jsonify({"error": "Incorrect password!"})


@app.post("/user-signup")
def signup():
    try:
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']
        role_name = data['role']
        role_name = role_name.lower()
        if not email or not password or not role_name:
            return jsonify({"error": "Missing required fields!"})
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({"error": "Invalid role!"})
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists!"})
        hashed_password = hash_password(password)
        datastore.create_user(username=username, email=email, password=hashed_password, roles=[role])
        db.session.commit()
        if role_name != "manager":
            user = datastore.find_user(email=data['email'])
            return jsonify(
                {"message": "Success", "email": user.email, "token": user.get_auth_token(), "role": user.roles[0].name})
        elif role_name == "manager":
            obj = datastore.find_user(email=email)
            obj.active = False
            db.session.add(obj)
            db.session.commit()
            return jsonify({"error": "You will receive a mail once admin approves your request!"})
    except Exception as e:
        print(e)


class AdminAction(Resource):
    @auth_required("token")
    def get(self):
        try:
            data = User.query.filter_by(active=False).with_entities(User.username, User.email).all()
            result = [{'username': row.username, 'email': row.email} for row in data]
            return jsonify(result)
        except Exception as e:
            print(e)

    @auth_required("token")
    def patch(self):
        try:
            action = request.args.get("action")
            email = request.json["email"]
            if int(action) == 1:
                obj = datastore.find_user(email=email)
                obj.active = True
                db.session.add(obj)
                db.session.commit()
                return jsonify({"status": "success"})
            elif int(action) == 0:
                obj = datastore.find_user(email=email)
                obj1 = RolesUsers.query.filter_by(user_email=email).first()
                db.session.delete(obj1)
                db.session.commit()
                db.session.delete(obj)
                db.session.commit()
                return jsonify({"status": "success"})
        except Exception as e:
            print(e)


class Changes(Resource):
    def get(self):
        try:
            name = request.args.get("for")
            if name == "cat":
                cats = Category.query.all()
                print(cats)
                return jsonify(cats)
        except Exception as e:
            print(e)

    def put(self):
        try:
            name = request.args.get("for")
            cat_id = request.args.get("id")
            if name == "cat":
                obj = CategoryChange.query.filter_by(id=cat_id).first()
                obj1 = Category.query.filter_by(category_id=obj.category_id).first()
                if obj.delete:
                    obj2 = Product.query.filter_by(category_id=obj.category_id).all()
                    for i in obj2:
                        obj3 = ProductChange.query.filter_by(product_id=i.product_id).first()
                        db.session.delete(obj3)
                        db.session.delete(i)
                    db.session.commit()
                    db.session.delete(obj1)
                    db.session.commit()
                if obj.add == False and obj.delete == False:
                    obj1.category_name = obj.category_name
                    db.session.add(obj1)
                    db.session.commit()
                db.session.delete(obj)
                db.session.commit()
                return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failure"})

    def delete(self):
        try:
            name = request.args.get("for")
            cat_id = request.args.get("id")
            if name == "cat":
                obj = CategoryChange.query.filter_by(id=cat_id).first()
                if obj.add:
                    obj1 = Category.query.filter_by(category_id=obj.category_id).first()
                    db.session.delete(obj1)
                    db.session.commit()
                else:
                    db.session.delete(obj)
                    db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failure"})

API.add_resource(Categories, '/categories', '/categories/<cate_id>')
API.add_resource(Cart_items, '/cart/<username>')
API.add_resource(Products, '/products/<cate_id>', '/products')
API.add_resource(AdminAction, '/admin')
API.add_resource(Changes, '/adminitems')

if __name__ == '__main__':
    app.run(debug=True)
