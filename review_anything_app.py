from flask import (
    Flask, render_template, request, url_for, redirect)
from flask_login import (
    UserMixin, LoginManager, login_required,
    login_user, logout_user)
import os
import json
from additional_funcs import (
    create_db_conn, flash_message, cursor_results,
    check_pw, create_hash_pw)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_ARGS = json.loads(open(os.path.join(APP_ROOT, 'config.json')).read())

# make sure to set debug to false for production
DEBUG = CONFIG_ARGS['DEBUG']
HOST = CONFIG_ARGS['HOST']
PORT = CONFIG_ARGS['PORT']

app = Flask(__name__)
app.secret_key = os.urandom(16)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass


# noinspection SqlDialectInspection
@login_manager.user_loader
def user_loader(user_id):
    conn, cursor = create_db_conn()
    cursor.execute('select * from users where id = ?', (user_id,))
    results = cursor_results(cursor)
    if len(results) == 0:
        return
    return User()


# noinspection SqlDialectInspection
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    form_email = request.form['email']
    form_password = request.form['password']

    conn, cursor = create_db_conn()
    cursor.execute('select * from users where email = ?', (form_email,))
    results = cursor_results(cursor)
    conn.close()
    if len(results) == 0:
        flash_message('Incorrect email or password.', 'danger')
        return render_template('login.html')

    if check_pw(form_password, results[0]['hash'], results[0]['salt']):
        user = User()
        user.id = results[0]['id']
        login_user(user)
        flash_message('You are now logged in.', 'success')
        return render_template('home.html')

    flash_message('Incorrect email or password.', 'danger')
    return render_template('login.html')


# noinspection SqlDialectInspection
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    form_email = request.form['email']
    form_name = request.form['name']
    form_password = request.form['password']

    if not form_email or not form_name or not form_password:
        flash_message('All fields need to be provided.', 'danger')
        return render_template('add_user.html')

    # check that the email doesn't already exist
    conn, cursor = create_db_conn()
    cursor.execute('select * from users where email = ?', (form_email,))
    results = cursor_results(cursor)
    if len(results) != 0:
        conn.close()
        flash_message('Account with that email already exists.', 'danger')
        return render_template('add_user.html')

    # hash the pw
    hashed_pw, salt = create_hash_pw(form_password)

    # add new user to db
    cursor.execute(
        'insert into users VALUES (?,?,?,?,?)',
        (None, form_name, form_email, hashed_pw, salt)
    )
    conn.commit()
    conn.close()

    flash_message('New account created under {}'.format(form_email), 'success')
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
