# Review Anything

An example of a web app in Flask where you can review anything.

## Getting Started

This app was built using Python 3.6 so I would suggest that as the version.

* Make sure you have the right version of Python installed on your machine.
* Fork & Clone this repo.
* Create a virtualenv and activate it.
* Change directory `cd /path/to/repo`
* Install required libraries `pip install -r requirements.txt`
* Create the database `python create_db.py`
* Run `python review_anything_app.py`

## Features

* Creating Users
* Login/Logout
* Write Reviews
* Up/Down vote reviews
* Comment on reviews _(coming soon)_

## Tech Implementations

* Persistent data to a database
* Sessions
* CSRF Tokens
* SQL Injection prevention
* Password hashing
* Design templates

## Setup on pythonanywhere.com

* Create an account on [pythonanywhere.com](https://www.pythonanywhere.com) *(a free account will work)*

* Open a new bash console

* Clone this repo `git clone https://github.com/fermanjj/Review-Anything-Web-App.git`

* Change directories to the new repo `cd review-anything-web-app/`

* Create a virtual environment `virtualenv -p /usr/local/bin/python3.6 ~/py36`

* Active the newly created virtualenv `source ~/py36/bin/activate`

* Install the required libraries `pip install -r requirements.txt`

* Create the database `python create_db.py`

* Return to the dashboard *(you can close the bash console)*

* Add a new web app under the web tab

* Select manual configuration as the web framework and python 3.6 as the python version

##### NOTE:

*For the next few steps, make sure to change `user` to your correct user directory.*

* Change the working directory to the location of the repo `/home/user/review-anything-web-app`

* Change the source code to the path to the `/home/user/review-anything-web-app/review_anything_app.py` file

* Change the virtualenv to the newly created virtual environment `/home/user/py36`

* Open the WSGI file and uncomment appropriate code under the flask section, changing the names like so

```python
import sys
path = '/home/user/review-anything-web-app'
if path not in sys.path:
    sys.path.append(path)
from review_anything_app import app as application
```

* Reload the app and you're done!
