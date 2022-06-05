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
from datetime import date


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db) #using flask-migrate to sync models with db

from models import *

# TODO: connect to a local postgresql database

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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # venues = db.session.query(Venue, Show)
  # areas = Venue.query.all()
  # num_upcoming_shows = Show.query.filter_by(date>date.now()).counts()


  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
   
  #  Get search value
  search_term=request.form.get('search_term', '') 

  # Get search count
  venue_count = db.session.query(db.func.count(Venue.id)).filter(Venue.name.contains(search_term)).all()

  # fetch all record that match search
  search_result = Venue.query.filter(Venue.name.contains(search_term)).all()

  response={
    "count": venue_count,
    "data": search_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # Get a venue by id
  data = Venue.query.get(venue_id)

  # Get past shows
  data.past_shows = (db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"), Artist.image_link.label("artist_image_link"), Show)
    .filter(Show.venue == venue_id)
    .filter(Show.artist == Artist.id)
    .filter(Show.date <= datetime.now())
    .all())
  
  # Step 3: Get Upcomming Shows
  data.upcoming_shows = (db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"), Artist.image_link.label("artist_image_link"), Show)
    .filter(Show.venue == venue_id)
    .filter(Show.artist == Artist.id)
    .filter(Show.date > datetime.now())
    .all())

  # Step 4: Get Number of past Shows
  data.past_shows_count = (db.session.query(db.func.count(Show.venue)).filter(Show.venue == venue_id)
    .filter(Show.date < datetime.now()).all())[0][0]

  # Get number of of Upcoming Shows
  data.upcoming_shows_count = (db.session.query(
    db.func.count(Show.venue))
    .filter(Show.venue == venue_id)
    .filter(Show.date > datetime.now())
    .all())[0][0]
    
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
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
      
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except: 
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. while adding ' + request.form['name'] + '. Try again!')  
    finally:
      # close session
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    flash('Unable to delete venue, Try again!')  

  finally:
    # close database session.
    db.session.close()
    flash('Venue successfully deleted')  
  return render_template('pages/home.html')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all() 
  data = artists
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # Get search value
  search_term=request.form.get('search_term', '')

  # Get search count
  artist_count = db.session.query(db.func.count(Artist.id)).filter(Artist.name.contains(search_term)).all()
  
  # Get search result
  artist_result = Artist.query.filter(Artist.name.contains(search_term)).all()
  
  response={
    "count": artist_count[0][0],
    "data": artist_result
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  # Get artist
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

#  Update
#  ----------------------------------------------------------------
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

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

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

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)

  # Pre Fill form with data
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

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

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

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

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

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

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

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

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


  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
