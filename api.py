import sqlalchemy
from flask_security import roles_accepted, auth_required

from model import *
from flask_restful import Resource
from flask import jsonify, request


class Categories(Resource):
    def get(self, cate_id=None):
        if cate_id is not None:
            items = Category.query.filter_by(category_id=cate_id).first()
            return jsonify(items)
        else:
            items = db.session.query(Category).all()
            return jsonify(items)

    def post(self):
        category = request.json['name']
        print(category)
        try:
            obj = Category(category_name=category)
            db.session.add(obj)
            db.session.commit()
            return jsonify({"status": "success"})
        # except sqlalchemy.exc.IntegrityError:
        #     return jsonify({"error": "Category already exists !"})
        except Exception as e:
            print(e)

    def delete(self, cate_id):
        try:
            obj = Product.query.filter_by(category_id=cate_id).first()
            if obj:
                db.session.delete(obj)
                db.session.commit()
            db.session.delete(Category.query.filter_by(category_id=cate_id).first())
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})

    def patch(self, cate_id):
        new_cat = request.args.get("new_cat")
        print(cate_id, new_cat)
        try:
            cat = db.session.query(Category).filter_by(category_id=cate_id).first()
            cat.category_name = new_cat
            db.session.add(cat)
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})


class Cart_items(Resource):
    def get(self, username):
        if username:
            cart_items = Users.query.filter_by(user_id=username).first().items
            return jsonify(cart_items)
        return jsonify({"status": "failure"})

    def post(self, username):
        prod_id = request.json["prod_id"]
        quantity = int(request.json["quantity"])
        try:
            obj = Cart(user_id=username, product_id=int(prod_id), quantity=quantity)
            db.session.add(obj)
            db.session.commit()
            return jsonify({"status": "success"})
        except:
            return jsonify({"status": "failed"})

    def delete(self, username):
        prod_id = request.args.get("prod_id")
        try:
            Cart.query.filter_by(product_id=prod_id, user_id=username).delete()
            db.session.commit()
            return jsonify({"status": "success"})
        except:
            return jsonify({"status": "failed"})

    def patch(self, username):
        try:
            cart = Cart.query.filter_by(user_id=username).all()
            for i in cart:
                prod = Product.query.filter_by(product_id=i.product_id).first()
                prod.product_quantity -= i.quantity
                db.session.add(prod)
                db.session.commit()
                db.session.delete(i)
                db.session.commit()
            return jsonify({"status": "failure"})
        except Exception as e:
            print(e)
            return jsonify({"status": "success"})


class Products(Resource):
    def post(self, cate_id):
        try:
            data = request.json
            obj = Product(category_id=cate_id, product_name=data['name'], product_unit=data['unit'],
                          product_price=int(data['price']),
                          product_quantity=int(data['quantity']))
            db.session.add(obj)
            db.session.commit()
            return jsonify({"status": "success"})
        except sqlalchemy.exc.IntegrityError:
            return jsonify({"error": "Category already exists !"})

    def delete(self):
        try:
            product = request.args.get("product_id")
            obj = Product.query.filter_by(product_id=product).first()
            db.session.delete(obj)
            db.session.commit()
        except:
            return jsonify({"status": "failed"})
        return jsonify({"status": "success"})

    def put(self):
        prod_id = request.args.get("product_id")
        new_unit = request.json["unit"]
        new_price = request.json["price"]
        new_quantity = request.json["quantity"]
        try:
            prod = db.session.query(Product).filter_by(product_id=prod_id).first()
            prod.product_price = new_price
            prod.product_quantity = new_quantity
            prod.product_unit = new_unit
            db.session.add(prod)
            db.session.commit()
            return jsonify({"status": "success"})
        except:
            return jsonify({"status": "failed"})
