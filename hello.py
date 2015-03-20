
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello World!'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
   return render_template('hello.html', name=name)

@app.route('/user/<username>')
def test_user(username):
	return 'User %s' % username

@app.route('/backslash/')
def test_backslash():
	return 'trailing backslash test!'
   
if __name__ == '__main__':
   app.run(debug=True)
