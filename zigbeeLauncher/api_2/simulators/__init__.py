from flask import Blueprint

simulators = Blueprint("simulators", __name__, url_prefix='/simulators')

from .view import *