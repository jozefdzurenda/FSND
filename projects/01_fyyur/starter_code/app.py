#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from os import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from wtforms.fields import choices
from forms import *

from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    # Home page
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # List venues, group by state, city
    data = []
    venues = Venue.query.all()
    places = Venue.query.distinct(Venue.city, Venue.state).all()

    for place in places:
        data.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Venue search
    search_term = request.form.get('search_term')
    matches = Venue.query.filter(Venue.name.ilike(
        "%{}%".format(search_term))).order_by(Venue.name).all()
    response = {
        "count": len(matches),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
        } for venue in matches]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Venue details
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        artist = Artist.query.get(show.artist_id)
        show_info = {
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_url,
            "start_time": show.start_time
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Creates a venue bases on input form

    form = VenueForm(request.form, meta={"csrf": False})

    if form.validate():

        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            genres=form.genres.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )

        try:
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully listed!')
        except:
            db.session.rollback()
            flash('Error! Venue ' + venue.name +
                  ' was NOT listed - database failure.', 'error')
        finally:
            db.session.close()
    else:
        flash('Error! Venue ' + form['name'].data +
              ' was NOT listed - invalid form submit.', 'error')
        # print(form.errors.items())

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Deletes a venue - returns None (triggered by a Delete button/JS)
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # List artists
    artists = Artist.query.order_by(Artist.name).all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Artist search
    search_term = request.form.get('search_term')
    matches = Artist.query.filter(Artist.name.ilike(
        "%{}%".format(search_term))).order_by(Artist.name).all()
    response = {
        "count": len(matches),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()])
        } for artist in matches]
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Artist details
    artist = Artist.query.filter(Artist.id == artist_id).first_or_404()
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        venue = Venue.query.get(show.venue_id)
        show_info = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_url,
            "start_time": show.start_time
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(show_info)
        else:
            past_shows.append(show_info)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Updates artist based on input form
    try:
        artist = Artist.query.get(artist_id)
        form = ArtistForm(request.form, meta={"csrf": False})
        if form.validate():
            artist.name = form.name.data,
            artist.city = form.city.data,
            artist.state = form.state.data,
            artist.phone = form.phone.data,
            artist.image_link = form.image_link.data,
            artist.facebook_link = form.facebook_link.data,
            artist.website_link = form.website_link.data,
            artist.genres = form.genres.data,
            artist.seeking_venue = form.seeking_venue.data,
            artist.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Artist ' + artist.name + ' edit successful!')
        else:
            flash('Artist ' + artist.name +
                  ' edit failed - invalid form submit', 'error')
    except:
        db.session.rollback()
        flash('Artist ' + artist.name + ' edit failed - db error', 'error')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Edits venue based on input form
    try:
        venue = Venue.query.get(venue_id)
        form = VenueForm(request.form, meta={"csrf": False})
        if form.validate():
            venue.name = form.name.data,
            venue.city = form.city.data,
            venue.state = form.state.data,
            venue.address = form.address.data,
            venue.phone = form.phone.data,
            venue.image_link = form.image_link.data,
            venue.facebook_link = form.facebook_link.data,
            venue.website_link = form.website_link.data,
            venue.genres = form.genres.data,
            venue.seeking_talent = form.seeking_talent.data,
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + venue.name + ' edit successful!')
        else:
            flash('Venue ' + venue.name +
                  ' edit failed - invalid form submit', 'error')
    except:
        db.session.rollback()
        flash('Venue ' + venue.name + ' edit failed - db error', 'error')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Creates artist based on input form
    form = ArtistForm(request.form, meta={"csrf": False})
    if form.validate():

        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            genres=form.genres.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )

        try:
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + artist.name + ' was successfully listed!')
        except:
            db.session.rollback()
            flash('Error! Artist ' + artist.name +
                  ' was NOT listed - database failure.', 'error')
        finally:
            db.session.close()
    else:
        flash('Error! Artist ' + form['name'].data +
              ' was NOT listed - invalid form submit.', 'error')
        # print(form.errors.items())

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # Lists shows ordered by start time
    shows = Show.query.order_by(Show.start_time).all()
    data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venues.name,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time.strftime("%d/%m/%Y, %H:%M")
        } for show in shows]

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # creates a show based on input form
    form = ShowForm(request.form, meta={"csrf": False})
    if form.validate():
        try:
            artist = Artist.query.get(form.artist_id.data)
            venue = Venue.query.get(form.venue_id.data)
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=form.start_time.object_data
            )
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            flash('Show was NOT listed - db failure', 'error')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash('Show was NOT listed - invalid form submited', 'error')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
