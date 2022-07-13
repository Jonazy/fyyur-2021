#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func, inspect
from datetime import date


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db) 

from models import *
from utils import data_to_list
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


# Home page return data
@app.route('/')
def index():
  recent_artists = Artist.query.order_by(Artist.id.desc()).all()
  recent_venues = Venue.query.order_by(Venue.id.desc()).all()
  return render_template('pages/home.html', recent_artists = recent_artists, recent_venues = recent_venues)


# Fetch all venues
@app.route('/venues')
def venues():
  venues_data = (db.session.query(Venue.city, Venue.state).group_by(Venue.city,Venue.state))
  data=data_to_list(venues_data)

  for area in data:
    area['venues'] = [data_to_list(ven) for ven in Venue.query.filter_by(city = area['city']).all()]
    for ven in area['venues']:
      ven['num_shows'] = db.session.query(func.count(Show.c.Venue_id)).filter(Show.c.Venue_id == ven['id']).filter(Show.c.start_time > datetime.now()).all()[0][0]
 
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '') 

  venue_count = db.session.query(db.func.count(Venue.id)).filter(Venue.name.contains(search_term)).all()
  search_result = Venue.query.filter(Venue.name.contains(search_term)).all()

  response = {
    "count": venue_count,
    "data": search_result
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

# Fetch venues by id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)

  data.past_shows = (db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"), Artist.image_link.label("artist_image_link"), Show)
    .filter(Show.venue == venue_id)
    .filter(Show.artist == Artist.id)
    .filter(Show.date <= datetime.now())
    .all())
  
  data.upcoming_shows = (db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"), Artist.image_link.label("artist_image_link"), Show)
    .filter(Show.venue == venue_id)
    .filter(Show.artist == Artist.id)
    .filter(Show.date > datetime.now())
    .all())

  data.past_shows_count = (db.session.query(db.func.count(Show.venue)).filter(Show.venue == venue_id)
    .filter(Show.date < datetime.now()).all())[0][0]

  data.upcoming_shows_count = (db.session.query(
    db.func.count(Show.venue))
    .filter(Show.venue == venue_id)
    .filter(Show.date > datetime.now())
    .all())[0][0]
  return render_template('pages/show_venue.html', venue=data)


# Render venues form
@app.route('/venues/create', methods=['GET'])
def create_venue():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


# Create Venue form
@app.route('/venues/create', methods=['POST'])
def create_venue():
  form = VenueForm(request.form)
  if form.validate():
    try:
      venue = Venue(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        address = request.form['address'],
        phone = request.form['phone'],
        genres = request.form.getlist('genres'),
        facebook_link = request.form['facebook_link'],
        website_link = request.form['website_link'],
        seeking_talent = request.form.getlist('seeking_talent'),
        seeking_description = request.form['seeking_description']
        )
      db.session.add(venue)
      db.session.commit()
      
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except: 

      flash('An error occurred. while adding ' + request.form['name'] + '. Try again!')  
    finally:

      db.session.close()
  return render_template('pages/home.html')

# Delete venue by id
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete(venue_id):

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    flash('Unable to delete venue, Try again!')  

  finally:
    db.session.close()
    flash('Venue successfully deleted')  
  return render_template('pages/home.html')


# Fetch all artist
@app.route('/artists')
def artists():
  artists = Artist.query.all() 
  data = artists
  return render_template('pages/artists.html', artists=data)

# Fetch artist by search word
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  artist_count = db.session.query(db.func.count(Artist.id)).filter(Artist.name.contains(search_term)).all()
  
  artist_result = Artist.query.filter(Artist.name.contains(search_term)).all()
  
  response={
    "count": artist_count[0][0],
    "data": artist_result
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)


# Fetch artist by artist_id
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  artist.past_shows = (db.session.query(Venue.id.label("venue_id"), Venue.name.label("venue_name"), Venue.image_link.label("venue_image_link"), Show)
    .filter(Show.artist == artist_id)
    .filter(Show.venue == Venue.id)
    .filter(Show.date <= datetime.now())
    .all())
  
  artist.upcoming_shows = (db.session.query(Venue.id.label("venue_id"), Venue.name.label("venue_name"), Venue.image_link.label("venue_image_link"), Show)
    .filter(Show.artist == artist_id)
    .filter(Show.venue == Venue.id)
    .filter(Show.date > datetime.now())
    .all())

  artist.past_shows_count = (db.session.query(db.func.count(Show.c.Artist_id))
    .filter(Show.artist == artist_id)
    .filter(Show.date < datetime.now())
    .all())[0][0]
  
  artist.upcoming_shows_count = (db.session.query(db.func.count(Show.c.Artist_id))
    .filter(Show.artist == artist_id)
    .filter(Show.date > datetime.now())
    .all())[0][0]
  return render_template('pages/show_artist.html', artist=artist)


# Update artist form rendering
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_talent.data = artist.seeking_talent
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)


# Update artist form
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Venue.query.get(artist_id)
  artist.name = request.form['name'],
  artist.city = request.form['city'],
  artist.state = request.form['state'],
  artist.phone = request.form['phone'],
  artist.genres = request.form['genres'],
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link'],
  artist.seeking_talent = request.form['seeking_talent'],
  artist.seeking_description = request.form['seeking_description']

  db.session.add(artist)
  db.session.commit()
  db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


# Update venue form rendering
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)


# Update venue submission
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.get(venue_id)
  venue.name = request.form['name'],
  venue.city = request.form['city'],
  venue.state = request.form['state'],
  venue.address = request.form['address'],
  venue.phone = request.form['phone'],
  venue.genres = request.form.getlist('genres'),
  venue.facebook_link = request.form['facebook_link']
  venue.website_link = request.form['website_link'],
  venue.seeking_talent = request.form['seeking_talent'],
  venue.seeking_description = request.form['seeking_description']

  db.session.add(venue)
  db.session.commit()
  db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))


# Create artist form
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# Create artist form submission
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form) 
  if form.validate():
    try:
      artist = Artist(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        facebook_link = request.form['facebook_link'],
        genres = request.form.getlist('genres'),
        website_link = request.form['website_link'],
        seeking_talent = request.form['seeking_talent'],
        seeking_description = request.form['seeking_description']
        )

      db.session.add(artist)
      db.session.commit()

      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except: 
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. while adding ' + request.form['name'] + '. Try again!')  
    finally:
      # close session
      db.session.close()
      flash('Artist ' + request.form['name'] + ' was successfully listed!') 
  else:
      flash('An error occurred. while adding ' + request.form['name'] + '. Try again!')  
  return render_template('pages/home.html')


# Fetch all shows
@app.route('/shows')
def shows():

  shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.venue == Venue.id)
    .filter(Show.artist == Artist.id)
    .all())
  return render_template('pages/shows.html', shows=shows)


# Create a show render form
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


# Create a show submission form
@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  if form.validate():
    try:
      show = Show.insert().values(
        venue = request.form['venue_id'],
        artist = request.form['artist_id'],
        date = request.form['start_time']
      )

      db.session.execute(show) 
      db.session.commit()

      flash('Show was successfully listed!')
    except : 
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred while adding show, Try again!.')
    finally:
      # close session
      db.session.close()
  else:
    flash('An error occurred while adding show, Try again!.')
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
