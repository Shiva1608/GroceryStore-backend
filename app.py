from celery.result import AsyncResult
from celery.schedules import crontab
from flask import Flask, send_file
from flask_cors import CORS
from flask_restful import Api
from flask_security import SQLAlchemyUserDatastore, Security, hash_password, verify_password
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Template
from adminapi import AdminAction, Changes
from caching import cache
from configuration import DevelopmentConfig
import flask_excel as excel
from model import *
from worker import celery_init_app
from task import daily_reminder, download_csv, monthly_report, download_csv2


def initialize():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    excel.init_excel(app)
    cache.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    app.app_context().push()
    API = Api(app)
    CORS(app)
    return app, API, datastore


app, API, datastore = initialize()

celery_app = celery_init_app(app)
from api import *


@celery_app.on_after_configure.connect
def send_mail(sender, **kwargs):
    users = User.query.filter(User.roles.any(name='customer')).all()
    for user in users:
        order = Order.query.filter_by(email=user.email).all()
        f = open("report.html")
        report_html = Template(f.read())
        sender.add_periodic_task(crontab(day_of_month="0"), monthly_report.s(user.email, "OrderReport",
                                                                             report_html.render(email=user.email,
                                                                                                orders=order)))


@celery_app.on_after_configure.connect
def send_reminder(sender, **kwargs):
    users = User.query.filter(User.roles.any(name='customer')).all()
    for user in users:
        f = open("reminder.html")
        reminder_html = Template(f.read())
        sender.add_periodic_task(crontab(hour="17"), daily_reminder.s(user.email, "Reminder",
                                                                      reminder_html.render()))


@auth_required("token")
@roles_accepted("manager")
@app.get("/download-sales")
def download_sales():
    res = download_csv.delay()
    return jsonify({"id": res.id})


@auth_required("token")
@roles_accepted("manager")
@app.get("/download-stock")
def download_stock():
    res = download_csv2.delay()
    return jsonify({"id": res.id})


@auth_required("token")
@roles_accepted("manager")
@app.get("/get-csv/<task_id>")
def result_csv(task_id):
    result = AsyncResult(task_id)
    if result.ready():
        if result.result is None:
            return jsonify({"message": "No data!"}), 404
        filename = result.result
        return send_file(filename, as_attachment=True, mimetype="text/csv", download_name=filename)
    else:
        return jsonify({"message": "Action pending!"}), 404


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


API.add_resource(Categories, '/categories', '/categories/<cate_id>')
API.add_resource(Cart_items, '/cart/<username>')
API.add_resource(Products, '/products/<cate_id>', '/products')
API.add_resource(AdminAction, '/admin')
API.add_resource(Changes, '/adminitems')

if __name__ == '__main__':
    app.run(debug=True)
