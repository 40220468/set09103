from flask import Flask, redirect, url_for, abort
app = Flask(__name__)

@app.route("/")
def root():
  return "The default, 'root' route"

@app.route("/hello/")
def hello():
  return "Hello World!"

@app.route("/static-example/img/")
def static_example_img():
  start = '<img src="'
  url = url_for('static', filename='vmask.jpg')
  end = '">'
  return start+url+end, 200

@app.route("/private/")
def private():
  return redirect(url_for('login'))

@app.route("/login/")
def login():
  return "Now we would get username & password"

@app.route("/force404/")
def force404():
  abort(404)

@app.errorhandler(404)
def page_not_found(error):
  return "Couldn't find the page you requested.", 404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
