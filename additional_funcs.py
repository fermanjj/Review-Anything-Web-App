import json
import os
import bcrypt
import sqlite3
from flask import flash, session, request
import base64

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_ARGS = json.loads(open(os.path.join(APP_ROOT, 'config.json')).read())


def cursor_results(cursor):
    """Runs fetchall once on the attached cursor.
    Gets the column names. Iterates the fetched
    results and attaches a dictionary of the
    column name and value of the column for each
    row.

    :param cursor:
    :return:
    """
    r = cursor.fetchall()
    c = cursor.description
    output = []
    for row in r:
        output_d = {}
        for col, col_name in zip(row, c):
            output_d[col_name[0]] = col
        output.append(output_d)
    return output


def verify_csrf():
    """
    Gets the csrf token from the form
    and from the session cookie. Validates
    that they match and returns True.
    Otherwise if there's any missing data or
    they don't match, flashes the appropriate
    message and returns False.

    :return: True if valid csrf token else False
    """
    csrf_token = request.form.get('csrf-token', '')
    cookie_token = session.get('csrf-token', False)
    if cookie_token is False:
        flash_message('Your session has expired.', 'danger')
        return False
    if csrf_token != cookie_token:
        flash_message('Invalid CSRF token.', 'danger')
        return False
    return True


def make_csrf():
    session['csrf-token'] = base64.b64encode(
        os.urandom(16)).decode()


def flash_message(msg, alert):
    """Flash a message on the next loaded page.

    alert options:
        primary
        secondary
        success
        danger
        warning
        info
        light
        dark

    :param msg: The message str
    :param alert: Must be a valid alert str
    """
    flash({'alert': alert, 'message': msg})


def create_db_conn():
    """Returns a tuple of the
    sqlite connection and cursor,
    in that order.

    :return:
    """
    conn = sqlite3.connect(os.path.join(
        APP_ROOT, CONFIG_ARGS['DB_NAME']
    ))
    cursor = conn.cursor()
    return conn, cursor


def create_hash_pw(pw, salt=None):
    """
    Hashes a given password and returns both the hashed
    pw and the salt that was used.

    :param pw: A password you'd like to create a hash for.
    :param salt: Default is None, however this func is
        used in checking the pw and that's the only
        time this should be provided.
    :returns: hashed pw, salt
    """
    if salt is None:
        salt = bcrypt.gensalt().decode()
    combo = pw + salt + CONFIG_ARGS['MASTER_SECRET_KEY']
    return bcrypt.hashpw(combo.encode(), salt.encode()), salt


def check_pw(pw, hashed_pw, salt):
    """
    Checks a provided password against a hashed pw,
    requires the same salt that the hashed pw was
    made with.

    :param str pw: The typed password
    :param str hashed_pw:
    :param str salt:
    :return: True if passwords match else False
    """
    if hashed_pw != create_hash_pw(pw, salt)[0]:
        return False
    return True
