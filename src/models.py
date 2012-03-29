#!/usr/bin/python

"""
Model for challenges and solutions.

In order to backup the local data store, first create DataStore stats using the local Admin console and then
run the following command:

These commands are working on Python 2.5.4 as of now. There are known issues with default installations of
python on MacOS and serialization of floats.

Download from local datastore into a file
appcfg.py download_data --url=http://localhost:8080/remote_api --filename=localdb

Upload from a file into production:
appcfg.py upload_data --url=http://jeeqsy.appspot.com/remote_api --filename=localdb

In order to use the remote api use the following statement:
python /Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/remote_api_shell.py -s localhost:8080

"""

from google.appengine.ext import db
from gravatar import get_profile_url

class Jeeqser(db.Model):
    """ A Jeeqs User """
    user = db.UserProperty()
    displayname_persisted = db.StringProperty()
    reviews_out_num = db.IntegerProperty(default=0)
    reviews_in_num = db.IntegerProperty(default=0)
    submissions_num = db.IntegerProperty(default=0)
    gravatar_url_persisted = db.LinkProperty()
    is_moderator = db.BooleanProperty()
    suspended_until = db.DateTimeProperty()
    unaccounted_flag_count = db.IntegerProperty(default=0)
    total_flag_count = db.IntegerProperty(default=0)

    def get_displayname(self):
        if self.displayname_persisted is None:
            self.displayname_persisted = self.user.nickname().split('@')[0]
            self.put()
        return self.displayname_persisted

    def set_displayname(self, value):
        self.displayname_persisted = value

    # Proxy for persisted displayname # TODO: upgrade to property decorator in python 2.7
    displayname = property(get_displayname, set_displayname, "Display name")

    def get_gravatar_url(self):
        if self.gravatar_url_persisted is None:
            self.gravatar_url_persisted = get_profile_url(self.user.email())
            self.put()
        return self.gravatar_url_persisted

    def set_gravatar_url(self, value):
        self.gravatar_url_persisted = value

    gravatar_url = property(get_gravatar_url, set_gravatar_url, "Gravatar URL")

class University(db.Model):
    name = db.StringProperty()
    fullname = db.StringProperty()

class Program(db.Model):
    name = db.StringProperty()
    fullname = db.StringProperty()
    university = db.ReferenceProperty(University, collection_name='programs')

class Course(db.Model):
    name = db.StringProperty()
    code = db.StringProperty()
    description = db.TextProperty()
    level = db.StringProperty(choices=['undergraduate', 'graduate'])
    program = db.ReferenceProperty(Program, collection_name='courses')
    yearOffered = db.IntegerProperty()
    monthOffered = db.StringProperty(choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'Auguest', 'September', 'October', 'November', 'December'])
    # Attribution for this course
    attribution = db.TextProperty()

class Exercise(db.Model):
    # Exercise number like
    name = db.StringProperty()
    number = db.StringProperty()
    course = db.ReferenceProperty(Course, collection_name='exercises')

class Challenge(db.Model):
    """Models a challenge"""
    EMPTY_MARKDOWN = 'Complete me!'

    name_persistent = db.StringProperty()

    def get_name(self):
        if self.name_persistent:
            return self.name_persistent
        elif self.exercise and self.exercise.name:
            self.name_persistent = self.exercise.name
            self.put()
            return self.name_persistent

    def set_name(self, value):
        self.name_persistent = value

    name = property(get_name, set_name, "Name")

    #compiled markdown
    content = db.TextProperty()
    #non-compiled markdown
    markdown = db.TextProperty(default=EMPTY_MARKDOWN)

    template_code = db.StringProperty(multiline=True)
    attribution_persistent = db.TextProperty()
    source = db.LinkProperty()

    # one to one relationship
    exercise = db.ReferenceProperty(Exercise, collection_name='challenge')

    def get_attribution(self):
        if self.attribution_persistent:
            return self.attribution_persistent
        elif self.exercise and self.exercise.course.attribution:
            self.attribution_persistent = self.exercise.course.attribution
            self.put()
            return self.attribution_persistent

    def set_attribution(self, value):
        self.attribution_persistent = value

    attribution = property(get_attribution, set_attribution, "Attribution")

class Attempt(db.Model):
    """Models a Submission for a Challenge """
    challenge = db.ReferenceProperty(Challenge)
    author = db.ReferenceProperty(Jeeqser)
    #compiled markdown
    content = db.TextProperty()
    #non-compiled markdown
    markdown = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    stdout = db.StringProperty(multiline=True)
    stderr = db.StringProperty(multiline=True)
    # List of users who voted for this submission
    users_voted = db.ListProperty(db.Key)
    vote_count = db.IntegerProperty(default=0)

    correct_count = db.IntegerProperty(default=0)
    incorrect_count = db.IntegerProperty(default=0)
    genius_count = db.IntegerProperty(default=0)

    #vote quantization TODO: might be removed !?
    vote_sum = db.FloatProperty(default=float(0))
    vote_average = db.FloatProperty(default=float(0))

    # is this the active submission for review ?
    active = db.BooleanProperty(default=False)
    submitted = db.BooleanProperty(default=False)

    # the index of this attempt among all attempts for a challenge.
    index = db.IntegerProperty(default=0)

    # Spam ?
    flagged_by = db.ListProperty(db.Key)
    flag_count = db.IntegerProperty(default=0)
    # if True, this attempt is blocked. Become true, once flag_count goes above a threshold
    flagged = db.BooleanProperty(default=False)

class Feedback(db.Model):
    """Models feedback for submission """
    attempt = db.ReferenceProperty(Attempt, collection_name='feedbacks')
    author = db.ReferenceProperty(Jeeqser, collection_name='feedback_out')
    # Denormalizing the attempt author
    attempt_author = db.ReferenceProperty(Jeeqser, collection_name='feedback_in')
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    vote = db.StringProperty(choices=['correct', 'incorrect', 'genius', 'flag'])

    # Spam ?
    flagged_by = db.ListProperty(db.Key)
    flag_count = db.IntegerProperty(default=0)
    # if True, this feedback is blocked. Becomes true, once flag_count goes above a threshold
    flagged = db.BooleanProperty(default=False)

class TestCase(db.Model):
    """ Models a test case"""
    challenge = db.ReferenceProperty(Challenge, collection_name='testcases')
    statement = db.StringProperty(multiline=True)
    expected = db.StringProperty(multiline=True)


