from flask import Blueprint

devices = Blueprint("zigbees", __name__, url_prefix='/zigbees')

from .view import *