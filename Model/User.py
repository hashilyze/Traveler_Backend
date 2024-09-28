from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
class User(db.Model):
    __table_name__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_code = db.Column(db.String(22), unique=True, nullable=False)
    name = db.Column(db.String(80))

    def __init__(self, user_id, user_code, name):
        self.user_id = user_id
        self.user_code = user_code
        self.name = name
