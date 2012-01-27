#!/usr/bin/python

"""
Model for challenges and solutions.

"""

from google.appengine.ext import db

__author__ = 'akhavan'

class Solution(db.Model):
    """Models a Solution"""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


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
    content = db.StringProperty(multiline=True)
    template_code = db.StringProperty(multiline=True)

class TestCase(db.Model):
    """ Models a test case"""
    challenge = db.ReferenceProperty(Challenge, collection_name='testcases')
    statement = db.StringProperty(multiline=True)
    expected = db.StringProperty(multiline=True)

    '''
    c = Challenge.get('agpkZXZ-amVlcXN5cg8LEglDaGFsbGVuZ2UYAQw')
    test = TestCase(challenge=c, statement='factorial(3)')
    '''


