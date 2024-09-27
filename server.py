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

    ### User ###
    result['user'] = {
        'id': id,
        'name': db.session.query(User.name).filter(User.user_id == id).scalar()
    }

    ### Resturant ###
    result['restaurants'] = {
        'count': restaurants.size,
        'list': []
    }
    for restaurant_id in restaurants.tolist():
        row = db.session.query(Business) \
               .filter(Business.business_id == restaurant_id) \
               .with_entities(Business.longitude, Business.latitude) \
               .first()
        result['restaurants']['list'].append({
            'id': restaurant_id,
            'longitude': row.longitude,
            'latitude': row.latitude
        })

    return result


app.run(debug=True)
