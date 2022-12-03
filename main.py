from email.utils import parseaddr

import flask
import hashlib
import objects
import datastore
import logging

app = flask.Flask(__name__)
app.secret_key = b'oaijrwoizsdfmnvoiajw34foinmzsdv98j234'


@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def root():
    post_list = datastore.load_courses()
    return show_page('index.html', 'Home Page', posts=post_list)


@app.route('/signup')
def signup():
    return show_page('signup.html', 'Sign Up')


@app.route('/signin')
def signin():
    return show_page('signin.html', 'Sign In')


@app.route('/dosignin', methods=['POST'])
def dosignin():
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')
    passwordhash = get_password_hash(password)
    user = datastore.load_user(email, passwordhash)
    if user:
        flask.session['user'] = user.username
        return flask.redirect('/')
    else:
        return show_login_page()


@app.route('/signout')
def signout():
    flask.session['user'] = None
    return flask.redirect('/')


@app.route('/register', methods=['POST'])
def register_user():
    email = flask.request.form.get('email')
    password1 = flask.request.form.get('password1')
    password2 = flask.request.form.get('password2')
    first_name = flask.request.form.get('first_name')
    last_name = flask.request.form.get('last_name')
    grad_year = flask.request.form.get('grad_year')
    school = flask.request.form.get('school')
    photo_url = flask.request.form.get('photo_url')
    bio = flask.request.form.get('bio')

    errors = []
    if password1 != password2:
        errors.append('Passwords do not match.')
    email_parts = parseaddr(email)
    if len(email_parts) != 2 or not email_parts[1]:
        errors.append('Invalid email address: ' + str(email))
    emails = email.split('@')

    if emails[1] != 'pitt.edu'.lower():
        errors.append('Please use a pitt.edu email address: ' + str(email))
    username = emails[0]

    user = objects.User(
        username,
        email,
        first_name, 
        last_name, 
        grad_year, 
        school, 
        photo_url, 
        bio
    )
    if errors:
        return show_page('/signup.html', 'Sign Up', errors=errors)
    else:
        passwordhash = get_password_hash(password1)
        datastore.save_user(user, passwordhash)
        flask.session['user'] = user.username
        return flask.redirect('/courses')


@app.route('/editprofile')
def editprofile():
    user = get_user()
    if user:
        about = datastore.load_about_user(user)
        return show_page('edit_profile.html', 'Edit Info for ' + user, text=about)
    return show_login_page()


@app.route('/saveprofile', methods=['POST'])
def saveprofile():
    user = get_user()
    if user:
        first_name = flask.request.form.get('first_name')
        last_name = flask.request.form.get('last_name')
        grad_year = flask.request.form.get('grad_year')
        school = flask.request.form.get('school')
        photo_url = flask.request.form.get('photo_url')
        bio = flask.request.form.get('bio')
        datastore.save_about_user(
            user,
            first_name, 
            last_name, 
            grad_year, 
            school, 
            photo_url, 
            bio
        )
        return flask.redirect('/user/' + user)
    return show_login_page()


@app.route('/user/<username>')
def user_page(username):
    about = datastore.load_about_user(username)
    about_lines = about.splitlines()
    completions = datastore.load_completions(username)

    # We use the following loop to sort the lessons in lexical order.
    for course in completions:
        lesson_list = []
        for lesson_id in completions[course]:
            lesson_list.append(completions[course][lesson_id])
        lesson_list.sort()
        completions[course] = lesson_list

    return show_page('user.html', username, lines=about_lines,
                     completions=completions)


# We should only use this to populate our data for the first time.
@app.route('/createdata')
def createdata():
    datastore.create_data()
    return 'OK'


def get_password_hash(pw):
    """This will give us a hashed password that will be extremlely difficult to
    reverse.  Creating this as a separate function allows us to perform this
    operation consistently every time we use it."""

    encoded = pw.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def get_user():
    """If our session has an identified user (i.e., a user is signed in), then
    return that username."""

    return flask.session.get('user', None)


def show_login_page():
    errors = ['You are not signed in.']
    return show_page('/signin.html', 'Sign In', errors)


def show_page(page, title, posts=None, post=None, comment=None,
              completions=None, show=True, text=None, lines=None, errors=None):
    return flask.render_template(page,
                                 page_title=title,
                                 user=get_user(),
                                 posts=posts,
                                 post=post,
                                 comment=comment,
                                 show=show,
                                 completions=completions,
                                 text=text,
                                 lines=lines,
                                 errors=errors)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
