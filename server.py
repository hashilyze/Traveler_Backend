from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from BPR.BPR import recommend_restaurants
from Model.User import *
from Model.Business import *
from secret.config import *

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy()
db.init_app(app)


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
