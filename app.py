from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_security import SQLAlchemyUserDatastore, Security
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

if __name__ == '__main__':
    app.run(debug=True)
