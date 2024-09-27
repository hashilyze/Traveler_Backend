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


@app.get('/recommend/<int:id>')
def recommend(id):
    restaurants = recommend_restaurants(id)
    result = {
        'user': {
            'id': id,
            'name': db.session.query(User.name).filter(User.user_id == id).scalar()
        },
        'restaurants': restaurants.tolist()
    }

    return result


app.run(debug=True)
