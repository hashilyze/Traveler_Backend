from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from BPR.BPR import recommend_restaurants
from secret.config import *


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy()
db.init_app(app)


@app.get('/recommend/<int:id>')
def recommend(id):
    restaurants = recommend_restaurants(id)
    result = {
        'id': id,
        'restaurants': restaurants.tolist()
    }

    return result


app.run(debug=True)
