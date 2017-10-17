from flask import Flask
import os

#initialize app
app = Flask(__name__, instance_relative_config=True)
# app.secret_key = 'soSecure'
app.secret_key = os.urandom(32)

#load views
from app import views

#load config file
app.config.from_object('config')