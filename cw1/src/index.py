import ConfigParser

from flask import Flask, render_template, request, redirect, url_for
from tmdb3 import set_key, searchMovie, Movie

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

@app.route('/', methods=['POST','GET'])
def index():
  if request.method == 'POST':
    name = request.form['name']
    return redirect(url_for('search', searched=name))
  else:
    mostPopFilms = Movie.mostpopular()
    return render_template('index.html', films = mostPopFilms[0:20])

@app.route('/movies/')
def moviesPage():
  return render_template('movies.html')

@app.route('/search/', methods=['POST','GET'])
@app.route('/search/<searched>', methods=['POST','GET'])
def search(searched):
  if request.method == 'POST':
    name = request.form['name']
    return redirect(url_for('search', searched=name))
  films = searchMovie(searched)
  return render_template('search.html', films=films)

if __name__ == '__main__':
  init(app)
  app.run(
    host=app.config['ip_address'],
    port=int(app.config['port']))
