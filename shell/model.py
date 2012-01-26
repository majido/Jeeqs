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
    name = db.StringProperty()
    content = db.StringProperty(multiline=True)
    template_code = db.StringProperty(multiline=True)

    '''
    # initialization code
from model import *

c = Challenge()
c.name = 'Factorial'
c.content = 'Write a function that calculates the factorial of n'
c.template_code = 'def factorial(n): \n'
c.put()
    '''
