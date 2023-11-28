from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class CategoryChange(db.Model):
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    category_id: int = Column(Integer, ForeignKey("category.category_id"))
    category_name: str = Column(String, nullable=False, unique=True)
    add: bool = Column(Boolean, default=False)
    delete: bool = Column(Boolean, default=False)


@dataclass
class ProductChange(db.Model):
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    product_id: int = Column(Integer, ForeignKey("product.product_id"))
    product_name: str = Column(String, nullable=False, unique=True)
    product_unit: str = Column(String, nullable=False)
    product_price: int = Column(Integer, nullable=False)
    product_quantity: int = Column(Integer)
    add: bool = Column(Boolean, default=False)
    delete: bool = Column(Boolean, default=False)


@dataclass
class Product(db.Model):
    __allow_unmapped__ = True
    category_id: int = Column(Integer, ForeignKey("category.category_id"), nullable=False)
    product_id: int = Column(Integer, primary_key=True, autoincrement=True)
    product_name: str = Column(String, nullable=False, unique=True)
    product_unit: str = Column(String, nullable=False)
    product_price: int = Column(Integer, nullable=False)
    product_quantity: int = Column(Integer)
    changes: list[ProductChange] = relationship("ProductChange")


@dataclass
class Category(db.Model):
    __allow_unmapped__ = True
    category_id: int = Column(Integer, primary_key=True, autoincrement=True)
    category_name: str = Column(String, nullable=False, unique=True)
    products: list[Product] = relationship("Product", backref="company")
    changes: list[CategoryChange] = relationship("CategoryChange")



@dataclass
class Cart(db.Model):
    __allow_unmapped__ = True
    email: str = Column(String, ForeignKey("user.email"), nullable=False)
    product_id: int = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    cart_id: int = Column(Integer, primary_key=True, autoincrement=True)
    quantity: int = Column(Integer, nullable=False)
    product: list[Product] = relationship('Product', backref='carts')


@dataclass
class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id: int = db.Column(db.Integer(), primary_key=True)
    user_email: int = db.Column('user_email', db.Integer(), db.ForeignKey('user.email'))
    role_id: int = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


@dataclass
class Role(db.Model, RoleMixin):
    id: int = db.Column(db.Integer(), primary_key=True)
    name: str = db.Column(db.String(80), unique=True)
    description: str = db.Column(db.String(255))


@dataclass
class ManagerApproval(db.Model):
    __allow_unmapped__ = True
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String, ForeignKey("user.email"), nullable=False)
    status: bool = Column(Boolean, default=False)


@dataclass
class User(db.Model, UserMixin):
    __allow_unmapped__ = True
    username: str = db.Column(db.String(255), nullable=False)
    email: str = db.Column(db.String(255), primary_key=True, index=True)
    password: str = db.Column(db.String(255))
    active: bool = db.Column(db.Boolean())
    fs_uniquifier: str = db.Column(db.String(255), unique=True, nullable=False)
    roles: list[Role] = db.relationship('Role', secondary='roles_users',
                                        backref=db.backref('users', lazy='dynamic'))
    items: list[Cart] = relationship("Cart")
    approved: list[ManagerApproval] = relationship("ManagerApproval")
