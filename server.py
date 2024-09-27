from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from BPR.BPR import recommend_restaurants
from secret.config import *


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy()
db.init_app(app)


class User(db.Model):
    __table_name__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_code = db.Column(db.String(22), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, user_id, name, user_code) :
        self.user_id = user_id
        self.name = name
        self.user_code = user_code


class Business(db.Model):
    __table_name__ = "business"
    business_id = db.Column(db.Integer, primary_key=True, nullable=False)
    business_code = db.Column(db.String(22), unique=True, nullable=False)
    longitude = db.Column(db.Double)
    latitude = db.Column(db.Double)

    def __init__(self, business_id, business_code, longitude, latitude) :
        self.business_id = business_id
        self.business_code = business_code
        self.longitude = longitude
        self.latitude = latitude


@app.get('/recommend/<int:id>')
def recommend(id):
    restaurants = recommend_restaurants(id)
    result = { }
    result['user'] = {
            'id': id,
            'name': db.session.query(User.name).filter(User.user_id == id).scalar()
        }

    result['restaurants'] = {
        'count': len(restaurants.tolist()),
        'list': []
    }
    for restaurant_id in restaurants.tolist():
        result['restaurants']['list'].append({
            'id': restaurant_id,
            'longitude': db.session.query(Business.longitude).filter(Business.business_id == restaurant_id).scalar(),
            'latitude': db.session.query(Business.latitude).filter(Business.business_id == restaurant_id).scalar()
        })

    return result


app.run(debug=True)
