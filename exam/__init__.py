from flask import Blueprint

exam = Blueprint('exam', __name__)

from . import session
from . import exam_info
