from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))

    created_time = db.Column(db.DateTime)

    shows = db.relationship('Show', backref=db.backref('venues'), cascade='all, delete', lazy=True)



class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))

    created_time = db.Column(db.DateTime)

    shows = db.relationship('Show', backref=db.backref('artists'), cascade='all, delete', lazy=True)

class Show(db.Model):
    __tablename__= 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    start_time = db.Column(db.DateTime, nullable = False)
