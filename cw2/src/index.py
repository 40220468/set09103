import ConfigParser
import bcrypt
import logging
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash, g
from functools import wraps
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'OB\x96\x86\xcc\x1f\xfar\x04BTK%\xa8\xf6P\n\xcb\xcb\xf3!\xd4\xd9\xc2'
db_location = 'var/sqlite3.db'

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
	app.config['log_file'] = config.get("logging", "name")
	app.config['log_location'] = config.get("logging", "location")
	app.config['log_level'] = config.get("logging", "level")
  except:
    print "Could not read configs from: ", config_location

def logs(app) :
	log_pathname = app.config['log_location'] + app.config['log_file']
	file_handler = RotatingFileHandler(log_pathname, maxBytes =1024*1024 * 10 , backupCount =1024)
	file_handler.setLevel(app.config['log_level'])
	formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s")
	file_handler.setFormatter(formatter)
	app.logger.setLevel(app.config['log_level'])
	app.logger.addHandler(file_handler)

def get_db() :
	db = getattr(g, 'db', None)
	if db is None :
		db = sqlite3.connect(db_location)
		g.db = db
	return db

@app.teardown_appcontext
def close_db_connection (exception):
	db = getattr(g, 'db', None)
	if db is not None :
		db.close()

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

valid_email = 'sergio894@hotmail.com'
valid_pwhash = bcrypt.hashpw('password', bcrypt.gensalt())

def check_auth(user, password):
	db = get_db()
	sql = "SELECT password FROM users WHERE user=?"
	row = db.cursor().execute(sql, [user]).fetchone()
	print row
	if(row is not None):
		dbPassword = row[0]
		if(dbPassword == bcrypt.hashpw(password.encode('utf-8'), dbPassword)):
			return True
	return False

def requires_login(f):
	@wraps(f)
	def decorated(*args , **kwargs):
		status = session.get('logged_in', False)
		if not status:
			return redirect(url_for('.root'))
		return f(*args , **kwargs)
	return decorated

@app.route('/logout/')
def logout():
	session ['logged_in'] = False
	return redirect(url_for('.root'))

@app.route("/secret/")
@requires_login
def secret():
	return "Secret Page"

@app.route("/", methods=['GET','POST'])
def root():
	this_route = url_for('.root')
	app.logger.info("Logging a test message from "+this_route)

	
	return render_template('index.html')

@app.route("/login/", methods=['GET','POST'])
def login():
	this_route = url_for('.login')
	app.logger.info("Logging a test message from "+this_route)
	
	if request.method =='POST':
		user = request.form['InputUsername']
		pw = request.form['InputPassword']
		if check_auth(user, pw):
				session['logged_in'] = True
				return redirect(url_for('.secret'))
		else:
				flash("Incorrect user or password")
	else:
		return render_template('login.html')
	
@app.route("/register/", methods=['GET','POST'])
def register():
	this_route = url_for('.register')
	app.logger.info("Logging a test message from "+this_route)
	
	if request.method =='POST':
		user = request.form['InputUsername']
		email = request.form['InputEmail']
		pw = request.form['InputPassword']
		db = get_db()
		db.cursor().execute('insert into users values ("{user}", "{email}", "{pw}")'.format(user=user, email=email, pw=bcrypt.hashpw(pw, bcrypt.gensalt())))
		#db.cursor().execute('insert into users values (?, ?, ?)', (user, email, bcrypt.hashpw(pw, bcrypt.gensalt())))
		db.commit()
		flash("Successful! Now you can login.")
		return redirect(url_for('root'))
	else:
		return render_template('register.html')
		
@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html')
  
@app.route("/force404/")
def force404():
  abort(404)

if __name__ == '__main__':
  init(app)
  logs(app)
  app.run(
    host=app.config['ip_address'],
    port=int(app.config['port']))