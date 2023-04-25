from flask import Blueprint

school = Blueprint('school', __name__)

from . import college
from . import sclass
