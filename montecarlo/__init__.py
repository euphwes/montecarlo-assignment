import logging

from os import environ
from os.path import abspath, dirname, join
from sys import stdout

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

log_format = '%(levelname)s %(asctime)s [%(filename)s %(funcName)s] - %(message)s'
logging.basicConfig(stream=stdout, format=log_format)

app = Flask(__name__)

# Lean sqlite database setup
basedir = abspath(dirname(__file__))

if environ.get('MONTECARLO_TEST_ENV') == 'true':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(basedir, 'metrics_db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(app)

@app.route('/')
def placeholder():
    return 'Hello, Monte Carlo folks!'

