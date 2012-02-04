#!/usr/bin/python

"""
Model for challenges and solutions.

In order to backup the local data store, first create DataStore stats using the local Admin console and then
run the following command:

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
    num_correct = db.IntegerProperty(default=0)
    num_incorrect = db.IntegerProperty(default=0)
    # List of users who voted correct for this submission
    voted_correct = db.ListProperty(db.Key)
    # List of users who voted incorrect for this submission
    voted_incorrect = db.ListProperty(db.Key)

class TestCase(db.Model):
    """ Models a test case"""
    challenge = db.ReferenceProperty(Challenge, collection_name='testcases')
    statement = db.StringProperty(multiline=True)
    expected = db.StringProperty(multiline=True)

    '''
    c = Challenge.get('agpkZXZ-amVlcXN5cg8LEglDaGFsbGVuZ2UYAQw')
    test = TestCase(challenge=c, statement='factorial(3)')
    '''


