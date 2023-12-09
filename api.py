import sqlalchemy
from flask_security import roles_accepted, auth_required
from caching import cache
from model import *
from flask_restful import Resource
from flask import jsonify, request


class Categories(Resource):
    @auth_required("token")
    @cache.cached(timeout=10)
    def get(self, cate_id=None):
        if cate_id is not None:
            items = Category.query.filter_by(category_id=cate_id).first()
            print(items)
            return jsonify(items)
        else:
            items = db.session.query(Category).filter(~Category.changes.any(CategoryChange.add)).all()
            return jsonify(items)

    @auth_required("token")
    @roles_accepted("manager")
    def post(self):
        category = request.json['name']
        try:
            obj = Category(category_name=category)
            db.session.add(obj)
            db.session.commit()
            obj1 = CategoryChange(category_id=obj.category_id, category_name=category, add=True)
            db.session.add(obj1)
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)

    @auth_required("token")
    @roles_accepted("manager")
    def delete(self, cate_id):
        try:
            obj = Category.query.filter_by(category_id=cate_id).first()
            obj1 = CategoryChange.query.filter_by(category_id=cate_id).first()
            if obj:
                if not obj1:
                    obj2 = CategoryChange(category_id=cate_id, category_name=obj.category_name, delete=True)
                    db.session.add(obj2)
                    db.session.commit()
                    return jsonify({"status": "success"})
                else:
                    obj1.delete = True
                    db.session.add(obj1)
                    db.session.commit()
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})

    @auth_required("token")
    @roles_accepted("manager")
    def patch(self, cate_id):
        new_cat = request.args.get("new_cat")
        try:
            obj = CategoryChange.query.filter_by(category_id=cate_id).first()
            if not obj:
                cat = CategoryChange(category_id=cate_id, category_name=new_cat)
                db.session.add(cat)
                db.session.commit()
                return jsonify({"status": "success"})
            else:
                obj.category_name = new_cat
                db.session.add(obj)
                db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})


class Cart_items(Resource):
    @auth_required("token")
    @roles_accepted("customer")
    def get(self, username):
        if username:
            cart_items = User.query.filter_by(email=username).first().items
            return jsonify(cart_items)
        return jsonify({"status": "failure"})

    @auth_required("token")
    @roles_accepted("customer")
    def post(self, username):
        prod_id = request.json["prod_id"]
        quantity = int(request.json["quantity"])
        try:
            obj = Cart(email=username, product_id=int(prod_id), quantity=quantity)
            db.session.add(obj)
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})

    @auth_required("token")
    @roles_accepted("customer")
    def delete(self, username):
        prod_id = request.args.get("prod_id")
        try:
            Cart.query.filter_by(product_id=prod_id, email=username).delete()
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})

    @auth_required("token")
    @roles_accepted("customer")
    def patch(self, username):
        try:
            cart = Cart.query.filter_by(email=username).all()
            for i in cart:
                prod = Product.query.filter_by(product_id=i.product_id).first()
                prod.product_quantity -= i.quantity
                db.session.add(prod)
                db.session.commit()
                order = Order(email=username, product_name=prod.product_name, quantity=i.quantity, product_price=prod.product_price)
                db.session.add(order)
                db.session.delete(i)
                db.session.commit()
            return jsonify({"status": "failure"})
        except Exception as e:
            print(e)
            return jsonify({"status": "success"})


class Products(Resource):
    @auth_required("token")
    def get(self):
        items = db.session.query(Product).filter(~Product.changes.any(ProductChange.add)).all()
        return jsonify(items)

    @auth_required("token")
    @roles_accepted("manager")
    def post(self, cate_id):
        try:
            if not cate_id:
                return jsonify({"status": "failed"})
            data = request.json
            obj = Product(category_id=cate_id, product_name=data['name'], product_unit=data['unit'],
                          product_price=int(data['price']),
                          product_quantity=int(data['quantity']))
            db.session.add(obj)
            db.session.commit()
            obj1 = ProductChange(product_id=obj.product_id, product_name=data['name'], product_unit=data['unit'],
                                 product_price=int(data['price']), add=True,
                                 product_quantity=int(data['quantity']))
            db.session.add(obj1)
            db.session.commit()
            return jsonify({"status": "success"})
        except sqlalchemy.exc.IntegrityError:
            return jsonify({"error": "Product already exists !"})

    @auth_required("token")
    @roles_accepted("manager")
    def delete(self):
        try:
            product = request.args.get("product_id")
            obj = Product.query.filter_by(product_id=product).first()
            obj1 = ProductChange.query.filter_by(product_id=product).first()
            if not obj1:
                obj2 = ProductChange(product_id=int(product), product_name=obj.product_name, delete=True,
                                     product_unit=obj.product_unit, product_quantity=obj.product_quantity,
                                     product_price=obj.product_price)
                db.session.add(obj2)
                db.session.commit()
                return jsonify({"status": "success"})
            else:
                obj1.delete = True
                db.session.add(obj1)
                db.session.commit()
                return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})

    @auth_required("token")
    @roles_accepted("manager")
    def put(self):
        prod_id = request.args.get("product_id")
        new_unit = request.json["unit"]
        new_price = request.json["price"]
        new_quantity = request.json["quantity"]
        try:
            obj = Product.query.filter_by(product_id=prod_id).first()
            obj1 = ProductChange.query.filter_by(product_id=prod_id).first()
            if not obj1:
                obj2 = ProductChange(product_id=int(prod_id), product_name=obj.product_name,
                                     product_unit=new_unit, product_quantity=new_quantity,
                                     product_price=new_price)
                db.session.add(obj2)
                db.session.commit()
                return jsonify({"status": "success"})
            else:
                obj1.product_unit = new_unit
                obj1.product_quantity = new_quantity
                obj1.product_price = new_price
                db.session.add(obj1)
                db.session.commit()
                return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})
