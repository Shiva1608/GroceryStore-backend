from app import app, datastore
from model import db


with app.app_context():
    db.create_all()
    datastore.find_or_create_role(name="Admin", description="This user is an Admin")
    datastore.find_or_create_role(name="StoreManager", description="This user is a Store Manager")
    datastore.find_or_create_role(name="Customer", description="This user is a Customer")
    db.session.commit()
    datastore.create_user(username="Shiva", email="admin@gmail.com", password="12345", roles=["Admin"])
    datastore.create_user(username="Harshita", email="manager@gmail.com", password="123456", roles=["StoreManager"])
    datastore.create_user(username="Ana", email="customer@gmail.com", password="123456", roles=["Customer"])
    db.session.commit()
