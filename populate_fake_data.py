"""Make sure your web app is running before doing this."""
import requests
import random
import csv
import re
# noinspection PyProtectedMember
from bs4 import _s


HOST = 'http://0.0.0.0:5000'  # change this
fake_data_file = 'fake_data.csv'


def create_email(name):
    name_clean = re.sub('[^a-zA-Z0-9- ]', '', name).strip()
    name_proper = re.sub(' +', '_', name_clean)

    return name_proper + str(random.randint(1, 1000)) + '@fake.com'


def populate():
    with open(fake_data_file) as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            movie = row['movie']
            celeb = row['celeb']
            review = row['review']

            email = create_email(celeb)
            print([
                movie, celeb, review[:20],
                email
            ])
            run_app_populate(movie, celeb, review, email)


def run_app_populate(movie, name, review, email):
    session = requests.Session()

    # create account
    print('creating account for: {}'.format(email))
    r = session.get(HOST + '/add_user')
    csrf_token = _s(r.text, 'html.parser').find('input', {'name': 'csrf-token'})['value']
    session.post(HOST + '/add_user', data={
        'email': email, 'name': name,
        'password': 'test', 'csrf-token': csrf_token
    })
    print('account created')

    # log in
    print('logging in')
    r = session.get(HOST + '/login')
    csrf_token = _s(r.text, 'html.parser').find('input', {'name': 'csrf-token'})['value']
    session.post(HOST + '/login', data={
        'email': email, 'password': 'test',
        'csrf-token': csrf_token
    })
    print('logged in')

    # create review
    print('creating review')
    r = session.get(HOST + '/create_review')
    csrf_token = _s(r.text, 'html.parser').find('input', {'name': 'csrf-token'})['value']
    session.post(HOST + '/create_review', data={
        'title': movie, 'rating': random.randint(1, 10),
        'review': review, 'csrf-token': csrf_token
    })
    print('review created')

    # search for a key word and up or down vote
    keyword = random.choice(review.split())
    print('searching keyword: {}'.format(keyword))
    r = session.get(HOST + '/search?keyword={}'.format(keyword))
    a_tags = _s(r.text, 'html.parser').find_all('a', {'href': re.compile('/review/.*')})
    if len(a_tags):
        a = random.choice(a_tags)['href']
        print('voting on review: {}'.format(a))
        session.get(HOST + '/vote?id={}&ud={}'.format(
            re.search('[0-9]+', a).group(), random.randint(0, 1)
        ))
    else:
        print('nothing found')


if __name__ == '__main__':
    populate()
