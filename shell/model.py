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

"""

from google.appengine.ext import db

__author__ = 'akhavan'

class Jeeqser(db.Model):
    """ Holds information for a Jeeqs User """

    username = db.StringProperty()
    user = db.UserProperty()

class Challenge(db.Model):
    """Models a challenge"""
    '''
    # initialization code
    from model import *

    c = Challenge()
    c.name = 'Factorial'
    c.content = 'Write a function that calculates the factorial of n'
    c.template_code = 'def factorial(n): \n'
    c.put()
    '''

    name = db.StringProperty()
    content = db.TextProperty()
    template_code = db.StringProperty(multiline=True)

class Attempt(db.Model):
    """Models a Solution"""
    challenge = db.ReferenceProperty(Challenge)
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    stdout = db.StringProperty(multiline=True)
    stderr = db.StringProperty(multiline=True)

class Submission(db.Model):
    """Models a Submission for a Challenge """
    challenge = db.ReferenceProperty(Challenge)
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    stdout = db.StringProperty(multiline=True)
    stderr = db.StringProperty(multiline=True)
    # List of users who voted for this submission
    users_voted = db.ListProperty(db.Key)
    vote_count = db.IntegerProperty(default=0)
    vote_sum = db.FloatProperty(default=float(0))
    vote_average = db.FloatProperty(default=float(0))
    # is this the latest submission on the challenge ?
    latest = db.BooleanProperty(default=True)

class TestCase(db.Model):
    """ Models a test case"""
    challenge = db.ReferenceProperty(Challenge, collection_name='testcases')
    statement = db.StringProperty(multiline=True)
    expected = db.StringProperty(multiline=True)

    '''
    c = Challenge.get('agpkZXZ-amVlcXN5cg8LEglDaGFsbGVuZ2UYAQw')
    test = TestCase(challenge=c, statement='factorial(3)')
    '''


