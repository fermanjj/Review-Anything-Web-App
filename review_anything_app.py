from flask import Flask, render_template, request
import flask_login
import os

DEBUG = True  # turn this off in production
HOST = '0.0.0.0'
PORT = 5000

app = Flask(__name__)
app.secret_key = os.urandom(16)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# mock user database
users = {}


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    if request.form['password'] == users.get(email, {'password': ''})['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('home.html')

    return render_template('login.html')


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
