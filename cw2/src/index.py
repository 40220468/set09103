import ConfigParser
import bcrypt
import logging
import sqlite3
import datetime
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

def check_auth(user, password):
	db = get_db()
	sql = "SELECT password FROM users WHERE user=?"
	row = db.cursor().execute(sql, [user]).fetchone()
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

@app.route("/", methods=['GET','POST'])
@app.route("/<int:pageNumber>/", methods=['GET','POST'])
def root(pageNumber=1):
	this_route = url_for('.root')
	app.logger.info("Logging a test message from "+this_route)
	
	db = get_db()
	sql = "SELECT * FROM blogables"
	rows = db.cursor().execute(sql).fetchall()
		
	return render_template('index.html', blogables=rows, pageNum=pageNumber, session=session)

@app.route("/login/", methods=['GET','POST'])
def login():
	this_route = url_for('.login')
	app.logger.info("Logging a test message from "+this_route)
	
	if request.method =='POST':
		user = request.form['InputUsername']
		pw = request.form['InputPassword']
		if check_auth(user, pw):
				session['logged_in'] = True
				session['name'] = user
				return redirect(url_for('loadUserBlog', wantedUser=user))
		else:
				flash("Incorrect user or password")
				return render_template('login.html', session=session)
	else:
		return render_template('login.html', session=session)
	
@app.route("/register/", methods=['GET','POST'])
def register():
	this_route = url_for('.register')
	app.logger.info("Logging a test message from "+this_route)
	
	if request.method =='POST':
		user = request.form['InputUsername']
		email = request.form['InputEmail']
		pw = request.form['InputPassword']
		db = get_db()
		#db.cursor().execute('insert into users values ("{user}", "{email}", "{pw}")'.format(user=user, email=email, pw=bcrypt.hashpw(pw, bcrypt.gensalt())))
		db.cursor().execute('insert into users values (?, ?, ?)', (user, email, bcrypt.hashpw(pw, bcrypt.gensalt())))
		db.commit()
		session['logged_in'] = True
		session['name'] = user
		return redirect(url_for('loadUserBlog', wantedUser=user))
	else:
		return render_template('register.html', session=session)
		
@app.route("/<wantedUser>/")
@app.route("/<wantedUser>/<int:pageNumber>/")
def loadUserBlog(wantedUser, pageNumber=1):
	db = get_db()
	sql = "SELECT * FROM users WHERE user=?"
	row = db.cursor().execute(sql, [wantedUser]).fetchone()
	if(row is not None):
		sql = "SELECT * FROM blogables WHERE user=?"
		rows = db.cursor().execute(sql, [wantedUser]).fetchall()
		
		return render_template('userBlog.html', user=wantedUser, blogables=rows, pageNum=pageNumber, session=session)
	else:
		abort(404)
		
@app.route("/post/", methods=['GET','POST'])
@requires_login
def post():
	this_route = url_for('.post')
	app.logger.info("Logging a test message from "+this_route)
	
	if request.method =='POST':
		user = session['name']
		title = request.form['InputTitle']
		post = request.form['InputPost']
		date = datetime.datetime.now().date()
		db = get_db()
		db.cursor().execute('insert into blogables values (?, ?, ?, ?)', (user, title, post, date))
		db.commit()
		flash("Successful! blogABLE completed!")
		return redirect(url_for('loadUserBlog', wantedUser=user))
	else:
		return render_template('post.html', session=session)

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
