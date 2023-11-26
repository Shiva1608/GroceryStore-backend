from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class Product(db.Model):
    category_id: int = Column(Integer, ForeignKey("category.category_id"))
    product_id: int = Column(Integer, primary_key=True, autoincrement=True)
    product_name: str = Column(String, nullable=False, unique=True)
    product_unit: str = Column(String, nullable=False)
    product_price: int = Column(Integer, nullable=False)
    product_quantity: int = Column(Integer)


@dataclass
class Category(db.Model):
    __allow_unmapped__ = True
    category_id: int = Column(Integer, primary_key=True, autoincrement=True)
    category_name: str = Column(String, nullable=False, unique=True)
    products: list[Product] = relationship("Product", backref="company")


@dataclass
class Cart(db.Model):
    user_id: str = Column(String, ForeignKey("users.user_id"), nullable=False)
    product_id: int = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    cart_id: int = Column(Integer, primary_key=True, autoincrement=True)
    quantity: int = Column(Integer, nullable=False)


@dataclass
class Users(db.Model):
    __allow_unmapped__ = True
    user_id: str = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    items: list[Cart] = relationship("Cart", backref="username")


@dataclass
class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id: int = db.Column(db.Integer(), primary_key=True)
    user_id: int = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id: int = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


@dataclass
class Role(db.Model, RoleMixin):
    id: int = db.Column(db.Integer(), primary_key=True)
    name: str = db.Column(db.String(80), unique=True)
    description: str = db.Column(db.String(255))


@dataclass
class User(db.Model, UserMixin):
    __allow_unmapped__ = True
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(255), unique=True, index=True)
    password: str = db.Column(db.String(255))
    active: bool = db.Column(db.Boolean())
    fs_uniquifier: str = db.Column(db.String(255), unique=True, nullable=False)
    roles: list[Role] = db.relationship('Role', secondary='roles_users',
                                        backref=db.backref('users', lazy='dynamic'))
