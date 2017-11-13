from flask import (
    Flask, render_template, request, url_for, redirect)
from flask_login import (
    UserMixin, LoginManager, login_required,
    login_user, logout_user, current_user)
import os
import json
from additional_funcs import (
    create_db_conn, flash_message, cursor_results,
    check_pw, create_hash_pw, make_csrf, verify_csrf
)
from datetime import datetime

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
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email


# noinspection SqlDialectInspection
@login_manager.user_loader
def user_loader(user_id):
    conn, cursor = create_db_conn()
    cursor.execute('select * from users where id = ?', (user_id,))
    results = cursor_results(cursor)
    conn.close()
    if len(results) == 0:
        return
    user = User(results[0]['id'], results[0]['name'], results[0]['email'])
    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauthorized.html')


# noinspection SqlDialectInspection
@app.route('/create_review', methods=['GET', 'POST'])
@login_required
def create_review():
    if request.method == 'GET':
        make_csrf()
        return render_template('create_review.html')

    form_title = request.form['title']
    form_rating = request.form['rating']
    form_review = request.form['review']

    if not form_title or not form_rating or not form_review:
        flash_message('Not all information provided.', 'danger')
        return render_template('create_review.html')

    if not verify_csrf():
        return render_template('create_review.html')

    # TODO: add captcha verification

    conn, cursor = create_db_conn()
    cursor.execute(
        'insert into reviews VALUES (?,?,?,?,?,?,?,?)',
        (None, form_title, form_rating, form_review,
         current_user.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
         0, 0)
    )
    conn.commit()
    cursor.execute('select * from reviews ORDER BY id desc limit 1')
    results = cursor_results(cursor)
    conn.close()

    url = url_for("view_review", id=results[0]['id'], title=results[0]['title'])

    view_text = 'View it <a href="{}">here</a>.'.format(url)

    flash_message('Your review has been created!' + view_text, 'success')
    return render_template('create_review.html')


# noinspection SqlDialectInspection
@app.route('/review/<id_>/<title>')
def view_review(id_, title):
    conn, cursor = create_db_conn()
    cursor.execute(
        'select * from reviews where id = ?',
        (id_,)
    )
    results = cursor_results(cursor)
    if len(results) == 0:
        flash_message('No review found.', 'danger')
        return render_template('view_review.html')

    return render_template('view_review.html', title=title)


# noinspection SqlDialectInspection
@app.route('/login', methods=['GET', 'POST'])
def login():
    """A route for a user to login."""
    if request.method == 'GET':
        make_csrf()
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

    if not verify_csrf():
        return render_template('login.html')

    # TODO: add captcha verification

    if check_pw(form_password, results[0]['hash'], results[0]['salt']):
        user = User(results[0]['id'], results[0]['name'], results[0]['email'])
        login_user(user)
        flash_message('You are now logged in.', 'success')
        return render_template('home.html')

    flash_message('Incorrect email or password.', 'danger')
    return render_template('login.html')


# noinspection SqlDialectInspection
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """A route for creating new users."""
    if request.method == 'GET':
        make_csrf()
        return render_template('add_user.html')
    form_email = request.form['email']
    form_name = request.form['name']
    form_password = request.form['password']

    if not form_email or not form_name or not form_password:
        flash_message('All fields need to be provided.', 'danger')
        return render_template('add_user.html')

    if not verify_csrf():
        return render_template('login.html')

    # TODO: add captcha verification

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
    """The route to log out a user."""
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
