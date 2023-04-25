import time
import pyotp
import utils
import messages
from . import userf
from database import models, db
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from flask import request, jsonify, session


@userf.route('/user/otp/enable', methods=['POST'])
@login_required
def otp_enable():
    user = models.User.query.filter_by(id=session["_uid"]).first()
    if user.otp_status == 1:
        return jsonify(messages.OTP_OPEN)
    while True:
        otp_secret = pyotp.random_base32()
        if models.User.query.filter_by(otp_secret=otp_secret).first() is None:
            break  # 一般来说是不会重复的，不过为了以防万一，还是写个判断吧
    user.otp_secret = otp_secret
    otp_fast_url = pyotp.totp.TOTP(user.otp_secret). \
        provisioning_uri(name=user.account, issuer_name='Graduation of Womsxd')
    user.otp_act_exp_time = int(time.time()) + 300
    try:
        db.session.commit()
        returns = {"data": {"otp": {"secret": user.otp_secret, "qrcode": utils.get_b64_qrcode(otp_fast_url),
                                    "expiration": user.otp_act_exp_time}}}
        returns.update(messages.OK)
        return jsonify(returns)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/otp/verify', methods=['POST'])
@login_required
def otp_verify():
    otp_code = request.form.get("otp_code")
    if not otp_code:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(id=session["_uid"]).first()
    if user.otp_status == 1:
        return jsonify(messages.OTP_OPEN)
    if user.otp_secret is None or user.otp_act_exp_time is None:
        return jsonify(messages.OTP_NEED_OPEN)
    if int(time.time()) > user.otp_act_exp_time:
        return jsonify(messages.OTP_TIME_OUT)
    if not pyotp.TOTP(user.otp_secret).verify(otp_code):
        return jsonify(messages.OTP_VERIFY_ERROR)
    user.otp_status = 1
    user.otp_act_exp_time = None
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/otp/disable', methods=['POST'])
@login_required
def otp_disable():
    otp_code = request.form.get("otp_code")
    if not otp_code:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(id=session["_uid"]).first()
    if user.otp_status == 0 or user.otp_secret is None:
        return jsonify(messages.OTP_NEED_OPEN)
    if not pyotp.TOTP(user.otp_secret).verify(otp_code):
        return jsonify(messages.OTP_VERIFY_ERROR)
    user.otp_status = 0
    user.otp_secret = None
    user.otp_act_exp_time = None
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
