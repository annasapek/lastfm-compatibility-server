from flask import Flask, request, jsonify
app = Flask(__name__)
import calculate

# server info 
@app.route('/')
def index():
    return app.send_static_file('app.html')

# api request
@app.route('/api/compute', methods=['POST'])
def api_request():
	if request.method == 'POST':
		return jsonify({'result': calculate.get_score(request.form['me'], request.form['friend'])})

		
if __name__ == '__main__':
   app.run(debug=True)