from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Business(SQLAlchemy().Model):
    __table_name__ = "business"
    business_id = db.Column(db.Integer, primary_key=True, nullable=False)
    business_code = db.Column(db.String(22), unique=True, nullable=False)
    name = db.Column(db.String(80))
    longitude = db.Column(db.Double)
    latitude = db.Column(db.Double)

    def __init__(self, business_id, business_code, name, longitude, latitude):
        self.business_id = business_id
        self.business_code = business_code
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
