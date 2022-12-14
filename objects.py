import datetime

# Your application objects go here.


class Course(object):
    """Represents a course."""

    def __init__(self, code, name, description, lessons):
        self.code = code
        self.name = name
        self.description = description
        self.lessons = lessons

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def to_dict(self):
        """ If we were using AJAX, we'd probably use this method for JSON."""
        d = {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'lessons': [],
        }
        for lesson in self.lessons:
            d['lessons'].append(lesson.to_dict())
        return d


class Lesson(object):
    """Represents one lesson in a course."""

    def __init__(self, lesson_id, title, content=''):
        self.id = lesson_id
        self.title = title
        self.content = content

    def to_dict(self):
        return {
            'id': self.lesson_id,
            'title': self.title,
            'content': self.content,
        }

# User obj


class User(object):
    """A user for the application."""

    def __init__(self, username, email, first_name, last_name, grad_year, school, photo_url, bio):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.grad_year = grad_year
        self.school = school
        self.photo_url = photo_url
        self.bio = bio

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grad_year': self.grad_year,
            'school': self.school,
            'photo_url': self.photo_url,
            'bio': self.bio
        }

# Comment obj


class Comment(object):
    def __init__(self, comment_id, post_id, username, description, date=None):
        self.comment_id = comment_id
        self.post_id = post_id
        self.username = username
        self.description = description

        if date:
            self.date = date
        else:
            self.date = datetime.datetime.now().strftime('%a, %B %d, %Y at %H:%M:%S')

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'post_id': self.post_id,
            'username': self.user.username,
            'description': self.description,
            'date': self.date
        }

# Post obj


class Post(object):
    def __init__(self, post_id, username, profile_pic, title, description, price, condition, image, comments: list, date=None, created=None):
        self.post_id = post_id
        self.username = username
        self.profile_pic = profile_pic
        self.title = title
        self.description = description
        self.price = price
        self.condition = condition
        self.image = image
        self.comments = comments

        if date:
            self.date = date
        else:
            self.date = datetime.datetime.now().strftime('%a, %B %d, %Y at %H:%M:%S')

        self.created = str(datetime.datetime.now())

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def to_dict(self):
        d = {
            'post_id': self.post_id,
            'username': self.username,
            'profile_pic': self.profile_pic,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'condition': self.condition,
            'image': self.image,
            'comments': [],
            'date': self.date,
            'created': self.created
        }
        for comment in self.comments:
            d['comments'].append(comment.comment_id)
        return d
