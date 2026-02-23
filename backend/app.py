from flask import Flask
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from routes.auth_routes import auth_bp
from routes.investor_routes import investor_bp
from routes.startup_routes import startup_bp
from auth import init_data_files

app = Flask(__name__)
CORS(app)

init_data_files()

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(investor_bp, url_prefix='/api/investor')
app.register_blueprint(startup_bp, url_prefix='/api/startup')

@app.route('/')
def index():
    return {'message': 'StartupMatch API', 'status': 'running'}

@app.route('/api/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
