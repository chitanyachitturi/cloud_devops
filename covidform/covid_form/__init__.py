from flask import Flask
from flask_pymongo import PyMongo


mongo = PyMongo()


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.debug = True
    app.secret_key = 'CovidFormApp'
    app.config['MONGO_URI'] = "mongodb://localhost:27017/covid"
    mongo.init_app(app)
    from .forms import covidForm
    app.register_blueprint(covidForm)
    return app



