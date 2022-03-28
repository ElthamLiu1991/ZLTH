from flask import Blueprint

firmwares = Blueprint("firmwares", __name__, url_prefix='/firmwares')

from .view import *