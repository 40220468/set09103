import ConfigParser

from flask import Flask, render_template, request, redirect, url_for, abort
from tmdb3 import set_key, searchMovie, Movie, searchPerson
from random import randint

set_key('80c7be1cb23c1e1ce5e409bb977ed400')

app = Flask(__name__)

@app.route('/config/')
def config():
  str = []
  str.append('Debug:'+app.config['DEBUG'])
  str.append('port:'+app.config['port'])
  str.append('url:'+app.config['url'])
  str.append('ip_address:'+app.config['ip_address'])
  return '\t'.join(str)

def init(app):
  config = ConfigParser.ConfigParser()
  try:
    config_location = "etc/config.cfg"
    config.read(config_location)

    app.config['DEBUG'] = config.get("config", "debug")
    app.config['ip_address'] = config.get("config", "ip_address")
    app.config['port'] = config.get("config", "port")
    app.config['url'] = config.get("config", "url")
  except:
    print "Could not read configs from: ", config_location

@app.route('/')
def index():
	mostPopFilms = Movie.mostpopular()
	upcomingFilms = Movie.upcoming()
	topRatFilms = Movie.toprated()
	return render_template('index.html', filmsPop = mostPopFilms[0:6],
	filmsUpc = upcomingFilms[0:6], filmsTop = topRatFilms[0:6])

@app.route('/search/', methods=['GET'])
@app.route('/search/<searched>', methods=['GET'])
def completeSearchFilm(searched):
  searchedMovies = searchMovie(searched)
  return render_template('search.html', films=searchedMovies)

@app.route('/', methods=['POST'])
@app.route('/search/', methods=['POST'])
@app.route('/search/<searched>', methods=['POST'])
def searchFilm(searched=None, film=None):
  name = request.form['searchedName']
  return redirect(url_for('completeSearchFilm', searched=name))
  
@app.route('/search/actor/', methods=['GET'])
@app.route('/search/actor/<searched>', methods=['GET'])
def completeSearchActor(searched):
  searchedActors = searchPerson(searched)
  return render_template('searchActor.html', actors=searchedActors)

@app.route('/<film>/cast', methods=['POST'])
@app.route('/people/', methods=['POST'])
def searchActor(film=None):
  name = request.form['searchedActor']
  return redirect(url_for('completeSearchActor', searched=name))
  
@app.route('/<film>/cast')
def filmCast(film):
	film = searchMovie(film)[0]
	castFilm = film.cast
	return render_template('filmCast.html', film=film, people=castFilm)
 
@app.route('/about/')
def about():
	return render_template('about.html')
	
@app.route('/people/', methods=['GET'])
def people():
	mostPopFilm = Movie.mostpopular()[0:6]
	randNumber = randint(0,5)
	castFilm = mostPopFilm[randNumber].cast
	return render_template('people.html', film=mostPopFilm[randNumber], people=castFilm)
  
@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html')
  
@app.route("/force404/")
def force404():
  abort(404)

if __name__ == '__main__':
  init(app)
  app.run(
    host=app.config['ip_address'],
    port=int(app.config['port']))
