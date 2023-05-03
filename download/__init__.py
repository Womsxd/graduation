import os
import messages
from flask_login import login_required
from flask import request, jsonify, Blueprint, send_file

XLS_TEMPLATES_DIR = 'static/download/xls_template'
XLS_TEMPLATES = [i for i in os.listdir(XLS_TEMPLATES_DIR) if os.path.isfile(os.path.join(XLS_TEMPLATES_DIR, i))]
download = Blueprint('download', __name__)


@download.route('/download/template/xls/download', methods=['GET'])
@login_required
def download_xls_template():
    file = request.values.get("file")
    if file is None:
        return jsonify(messages.DATA_NONE)
    if file not in XLS_TEMPLATES:
        return jsonify(messages.NOT_FOUND)
    return send_file(os.path.join(XLS_TEMPLATES_DIR, file), as_attachment=True)
