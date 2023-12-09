from flask import jsonify, request
from flask_restful import Resource
from flask_security import roles_accepted, auth_required
from model import *
from task import manager_account_status


class AdminAction(Resource):
    @auth_required("token")
    @roles_accepted("admin")
    def get(self):
        try:
            data = User.query.filter_by(active=False).with_entities(User.username, User.email).all()
            result = [{'username': row.username, 'email': row.email} for row in data]
            return jsonify(result)
        except Exception as e:
            print(e)

    @auth_required("token")
    @roles_accepted("admin")
    def patch(self):
        try:
            action = request.args.get("action")
            email = request.json["email"]
            if int(action) == 1:
                obj = User.query.filter_by(email=email).first()
                obj.active = True
                db.session.add(obj)
                db.session.commit()
                manager_account_status(email, "Regarding your request for manager!", "Dear" + obj.username + ", Your request for manager login has been approved. You can proceed to log in!").delay()
                return jsonify({"status": "success"})
            elif int(action) == 0:
                obj = User.query.filter_by(email=email).first()
                obj1 = RolesUsers.query.filter_by(user_email=email).first()
                db.session.delete(obj1)
                db.session.commit()
                db.session.delete(obj)
                db.session.commit()
                manager_account_status(email, "Regarding your request for manager!",
                                       "Dear" + obj.username + ", I am sorry to inform you that your request for manager login has been disapproved!").delay()
                return jsonify({"status": "success"})
        except Exception as e:
            print(e)


class Changes(Resource):
    @auth_required("token")
    @roles_accepted("admin")
    def get(self):
        try:
            name = request.args.get("for")
            if name == "cat":
                cats = Category.query.all()
                return jsonify(cats)
            elif name == "prod":
                prods = Product.query.all()
                return jsonify(prods)
        except Exception as e:
            print(e)

    @auth_required("token")
    @roles_accepted("admin")
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
                        if obj3:
                            db.session.delete(obj3)
                        db.session.delete(i)
                    db.session.commit()
                    db.session.delete(obj1)
                    db.session.commit()
                if obj.add is False and obj.delete is False:
                    obj1.category_name = obj.category_name
                    db.session.add(obj1)
                    db.session.commit()
                db.session.delete(obj)
                db.session.commit()
            elif name == "prod":
                obj = ProductChange.query.filter_by(id=cat_id).first()
                if obj.add is False and obj.delete is False:
                    obj2 = Product.query.filter_by(product_id=obj.product_id).first()
                    obj2.product_name = obj.product_name
                    obj2.product_price = obj.product_price
                    obj2.product_unit = obj.product_unit
                    obj2.product_quantity = obj.product_quantity
                    db.session.add(obj2)
                    db.session.commit()
                if obj.delete:
                    obj1 = Product.query.filter_by(product_id=obj.product_id).first()
                    db.session.delete(obj1)
                    db.session.commit()
                db.session.delete(obj)
                db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failure"})

    @auth_required("token")
    @roles_accepted("admin")
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
            elif name == "prod":
                obj = ProductChange.query.filter_by(id=cat_id).first()
                if obj.add:
                    obj1 = Product.query.filter_by(product_id=obj.product_id).first()
                    db.session.delete(obj1)
                db.session.delete(obj)
                db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failure"})
