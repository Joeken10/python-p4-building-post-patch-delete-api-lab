#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries', methods=['GET'])
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

@app.route('/bakeries/<int:id>', methods=['GET'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        abort(404, description="Bakery not found")
    return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods/by_price', methods=['GET'])
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(baked_goods_by_price_serialized, 200)

@app.route('/baked_goods/most_expensive', methods=['GET'])
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if not most_expensive:
        abort(404, description="No baked goods found")
    return make_response(most_expensive.to_dict(), 200)

# POST endpoint to create a new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form
    new_baked_good = BakedGood(
        name=data['name'],
        price=data['price'],
        bakery_id=data['bakery_id']
    )
    db.session.add(new_baked_good)
    db.session.commit()

    return make_response(jsonify(new_baked_good.to_dict()), 201)
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = db.session.get(Bakery, id)  # Use session.get for more clarity
    if not bakery:
        abort(404, description="Bakery not found")

    data = request.get_json()  # Get the JSON data from the request
    name = data.get('name') if data else None  # Check if data exists

    if name:
        bakery.name = name
        db.session.commit()
        return jsonify(bakery.to_dict()), 200

    return jsonify({"error": "No valid fields to update"}), 400


@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = db.session.get(BakedGood, id)  # Use Session.get() to fetch the baked good
    if not baked_good:
        abort(404, description="Baked good not found")

    db.session.delete(baked_good)
    db.session.commit()
    return jsonify({"message": "Baked good deleted successfully"}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
