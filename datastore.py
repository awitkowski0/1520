from google.cloud import datastore

import objects
import logging


# Your data storage code goes here.
# Look at: https://console.cloud.google.com/datastore to see your live
# entities.


_USER_ENTITY = 'User'
_POST_ENTITY = 'Post'
_COMMENT_ENTITY = 'Comment'


def _get_client():
    """Build a datastore client."""

    return datastore.Client()


def _load_key(client, entity_type, entity_id=None, parent_key=None):
    """Load a datastore key using a particular client, and if known, the ID.
    Note that the ID should be an int - we're allowing datastore to generate
    them in this example."""

    key = None
    if entity_id:
        key = client.key(entity_type, entity_id, parent=parent_key)
    else:
        # this will generate an ID
        key = client.key(entity_type)
    return key


def _load_entity(client, entity_type, entity_id, parent_key=None):
    """Load a datstore entity using a particular client, and the ID."""

    key = _load_key(client, entity_type, entity_id, parent_key)
    entity = client.get(key)
    logging.info('retrieved entity for %s' % (entity_id))
    return entity


def _post_from_entity(post_entity):
    """Translate the post entity to a regular old Python object."""

    post_id = post_entity['post_id']
    username = post_entity['username']
    profile_pic = post_entity['profile_pic']
    title = post_entity['title']
    description = post_entity['description']
    price = post_entity['price']
    condition = post_entity['condition']
    image = post_entity['image']
    date = post_entity['date']
    created = post_entity['created']

    post = objects.Post(post_id, username, profile_pic, title, description,
                        price, condition, image, [], date, created)

    # post_entity['comments'] should be an array of IDs
    comments = post_entity['comments']
    for comment_id in comments:
        post.add_comment(load_comment(post_id, comment_id))

    logging.info('built object from post entity: %s' % (post_id))
    return post


def _comment_from_entity(comment_entity):
    """Translate the comment entity to a regular old Python object."""

    comment_id = comment_entity['comment_id']
    post_id = comment_entity['post_id']
    username = comment_entity['username']
    description = comment_entity['description']
    date = comment_entity['date']

    comment = objects.Comment(comment_id, post_id, username, description, date)
    logging.info('built object from comment entity: %s' % (comment_id))
    return comment


def load_post(post_id):
    """Load a post from the datastore, based on the post id."""

    logging.info('loading post: %s' % (post_id))
    client = _get_client()
    post_entity = _load_entity(client, _POST_ENTITY, post_id)
    logging.info('loaded post: %s' % (post_id))
    post = _post_from_entity(post_entity)
    query = client.query(kind=_COMMENT_ENTITY)
    # query.add_filter('post_id', '=', post_id)
    #query.order = ['date']

    for comment in query.fetch():
        post.add_comment(_comment_from_entity(comment))
    logging.info('loaded posts: %s' % (len(post.comments)))
    return post


def load_posts():
    """Load all of the posts."""

    client = _get_client()
    q = client.query(kind=_POST_ENTITY)
    q.order = ["-created"]

    result = []
    for post in q.fetch():
        result.append(post)
    return result


def load_comment(post_id, comment_id):
    """Load a comment under the given post id."""

    logging.info('loading comment detail: %s / %s ' % (post_id, comment_id))
    client = _get_client()
    parent_key = _load_key(client, _POST_ENTITY, post_id)
    comment_entity = _load_entity(
        client, _COMMENT_ENTITY, comment_id)
    return _comment_from_entity(comment_entity)


def load_user(email, passwordhash):
    """Load a user based on the passwordhash; if the passwordhash doesn't match
    the username, then this should return None."""

    client = _get_client()
    q = client.query(kind=_USER_ENTITY)
    q.add_filter('email', '=', email)
    q.add_filter('passwordhash', '=', passwordhash)
    for user in q.fetch():
        return objects.User(
            user['username'],
            user['email'],
            user['first_name'],
            user['last_name'],
            user['grad_year'],
            user['school'],
            user['photo_url'],
            user['bio'])
    return None


def load_user_from_username(email):
    """Load a user based on the passwordhash; if the passwordhash doesn't match
    the username, then this should return None."""

    client = _get_client()
    q = client.query(kind=_USER_ENTITY)
    q.add_filter('email', '=', email)
    for user in q.fetch():
        return objects.User(
            user['username'],
            user['email'],
            user['first_name'],
            user['last_name'],
            user['grad_year'],
            user['school'],
            user['photo_url'],
            user['bio'])
    return None

# GET BACK TO HERE ON SUNDAY!!


def load_about_user(username):
    """Return a string that represents the "About Me" information a user has
    stored."""

    user = _load_entity(_get_client(), _USER_ENTITY, username)
    if user:
        return user['bio']
    else:
        return ''


def save_user(user, passwordhash):
    """Save the user details to the datastore."""

    client = _get_client()
    entity = datastore.Entity(_load_key(client, _USER_ENTITY, user.username))
    entity['username'] = user.username
    entity['email'] = user.email
    entity['passwordhash'] = passwordhash
    entity['first_name'] = user.first_name
    entity['last_name'] = user.last_name
    entity['grad_year'] = user.grad_year
    entity['school'] = user.school
    entity['photo_url'] = user.photo_url
    entity['bio'] = ''
    client.put(entity)


def save_about_user(user, first_name, last_name, grad_year, school, photo_url, bio):
    """Save the user's bio info to the datastore."""

    client = _get_client()
    user = _load_entity(client, _USER_ENTITY, user)
    user['first_name'] = first_name
    user['last_name'] = last_name
    user['grad_year'] = grad_year
    user['school'] = school
    user['photo_url'] = photo_url
    user['bio'] = bio
    client.put(user)


def create_comment(comment: objects.Comment):
    """Save comment to datastore"""
    client = _get_client()

    entity = datastore.Entity(
        _load_key(client, _COMMENT_ENTITY, comment.comment_id))

    entity['comment_id'] = comment.comment_id
    entity['post_id'] = comment.post_id
    entity['username'] = comment.username
    entity['description'] = comment.description
    entity['date'] = comment.date

    client.put(entity)


def save_post(post):
    """Save post info to the datastore"""

    client = _get_client()
    entity = datastore.Entity(_load_key(client, _POST_ENTITY, post.post_id))
    entity['post_id'] = post.post_id
    entity['username'] = post.username
    entity['profile_pic'] = post.profile_pic
    entity['title'] = post.title
    entity['description'] = post.description
    entity['price'] = post.price
    entity['condition'] = post.condition
    entity['image'] = post.image
    entity['comments'] = post.comments
    entity['date'] = post.date
    entity['created'] = post.created

    client.put(entity)


def update_post(post: objects.Post):
    client = _get_client()
    entity = _load_entity(client, _POST_ENTITY, post.post_id)

    entity['profile_pic'] = post.profile_pic
    entity['title'] = post.title
    entity['description'] = post.description
    entity['price'] = post.price
    entity['condition'] = post.condition
    entity['image'] = post.image
    for comment in post.comments:
        entity['comments'].append(comment.comment_id)
    entity['date'] = post.date

    client.put(entity)


def delete_post(id):
    client = _get_client()
    key = client.key(_POST_ENTITY, id)
    client.delete(key)


# def create_data():
#     """You can use this function to populate the datastore with some basic
#     data."""

#     client = _get_client()
#     entity = datastore.Entity(client.key(_USER_ENTITY, 'testuser'),
#                               exclude_from_indexes=[])
#     entity.update({
#         'username': 'testuser',
#         'passwordhash': '',
#         'email': '',
#         'bio': ''
#     })
#     client.put(entity)

#     entity = datastore.Entity(client.key(_COURSE_ENTITY, 'Course01'),
#                               exclude_from_indexes=['description', 'code'])
#     entity.update({
#         'code': 'Course01',
#         'name': 'First Course',
#         'description': 'This is a description for a test course.  In the \
# future, real courses will have lots of other stuff here to see that will tell \
# you more about their content.',
#     })
#     client.put(entity)
#     entity = datastore.Entity(client.key(_COURSE_ENTITY, 'Course02'),
#                               exclude_from_indexes=['description', 'code'])
#     entity.update({
#         'code': 'Course02',
#         'name': 'Second Course',
#         'description': 'This is also a course description, but maybe less \
# wordy than the previous one.'
#     })
#     client.put(entity)
#     entity = datastore.Entity(client.key(_COURSE_ENTITY,
#                                          'Course01',
#                                          _LESSON_ENTITY),
#                               exclude_from_indexes=['content', 'title'])
#     entity.update({
#         'title': 'Lesson 1: The First One',
#         'content': 'Imagine there were lots of video content and cool things.',
#     })
#     client.put(entity)
#     entity = datastore.Entity(client.key(_COURSE_ENTITY,
#                                          'Course01',
#                                          _LESSON_ENTITY),
#                               exclude_from_indexes=['content', 'title'])
#     entity.update({
#         'title': 'Lesson 2: Another One',
#         'content': '1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11',
#     })
#     client.put(entity)
#     entity = datastore.Entity(client.key(_COURSE_ENTITY,
#                                          'Course02',
#                                          _LESSON_ENTITY),
#                               exclude_from_indexes=['content', 'title'])
#     entity.update({
#         'title': 'Lesson 1: The First One, a Second Time',
#         'content': '<p>Things</p><p>Other Things</p><p>Still More Things</p>',
#     })

#     client.put(entity)
#     entity = datastore.Entity(client.key(_COURSE_ENTITY,
#                                          'Course02',
#                                          _LESSON_ENTITY),
#                               exclude_from_indexes=['content', 'title'])
#     entity.update({
#         'title': 'Lesson 2: Yes, Another One',
#         'content': '<ul><li>a</li><li>b</li><li>c</li><li>d</li><li></ul>',
#     })
#     client.put(entity)
