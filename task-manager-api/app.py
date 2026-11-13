from flask import Flask
from flask_cors import CORS
from database import db
from config import CORS_ORIGINS, DATABASE_URI, DEBUG, SECRET_KEY
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
import os, sys, json, datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if SECRET_KEY:
    app.config['SECRET_KEY'] = SECRET_KEY

if CORS_ORIGINS:
    CORS(app, origins=CORS_ORIGINS)
db.init_app(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)

@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(datetime.datetime.now())}

@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
