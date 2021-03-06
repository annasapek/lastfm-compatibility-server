from flask import Flask, request, jsonify
import calculate

app = Flask(__name__)

# serve front end 
@app.route('/')
def index():
    return app.send_static_file('app.html')

# api request
@app.route('/api/compute', methods=['POST'])
def api_request():
    print request.form
    return jsonify(calculate.get_score(request.form['me'], request.form['friend']))
        
if __name__ == '__main__':
   app.run(debug=True)