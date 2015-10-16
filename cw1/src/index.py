from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
  if request.method == 'POST':
    return redirect(url_for('search'))
  else:
    return render_template('index.html')

@app.route('/movies/')
def moviesPage():
  return render_template('movies.html')

@app.route('/search/')
def search():
  return render_template('search.html')

if __name__ == ("__main__"):
  app.run(host='0.0.0.0', debug=True)
