from flask import Blueprint

devices = Blueprint("devices", __name__, url_prefix='/devices')

from .view import *