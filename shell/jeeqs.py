#!/usr/bin/python

"""
A program for managing challenges and solutions.

"""

import logging
import new
import os
import sys
import traceback
import wsgiref.handlers
from google.appengine.ext.db import Key
from model import *

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


# Set to True if stack traces should be shown in the browser, etc.
_DEBUG = True

__author__ = 'akhavan'


class FrontPageHandler(webapp.RequestHandler):
    """renders the challenges.html template
    """

    def get(self):
        # get available challenges

        query = Challenge.all()
        results = query.fetch(20)

        challenges = {}

        for ch in results:
            challenges[ch.name] = str(ch.key())

        logging.info(challenges)

        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'challenges.html')

        vars = {'challenges': challenges}

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)


class ChallengeHandler(webapp.RequestHandler):
    """renders the challenge.html template
    """

    def get(self):
        # get the challenge
        ch_key = self.request.get('ch')
        if (not ch_key):
            self.error(403)

        challenge = Challenge.get(ch_key)
        if (not challenge):
            self.error(403)

        challenge_text = challenge.content
        template_code = '"' + challenge.template_code + '"'

        logging.info("template code is : " + template_code)

        template_file = os.path.join(os.path.dirname(__file__), 'templates',
            'challenge.html')

        # show this user's previous submitted solutions
        attempts_text = ''
        if (users.get_current_user()):
            attempts = db.GqlQuery(" SELECT * "
                                   " FROM Solution "
                                   " WHERE author = :1 ",
                users.get_current_user())

            for attempt in attempts:
                attempts_text = attempts_text + attempt.content + '====================== \n'

        vars = {'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'user': users.get_current_user(),
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'attempts_text': attempts_text,
                'challenge_text': challenge_text,
                'challenge_key' : challenge.key(),
                'template_code': template_code
        }
        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)


class ProgramHandler(webapp.RequestHandler):
    """Evaluates a python program and returns the result.
    """

    def get(self):
        program = self.request.get('program')
        logging.info('program is ' + program)
        if not program:
            return

        # retrieve the challenge
        challenge_key = self.request.get('challenge_key')
        if not challenge_key:
            self.error(403)
        challenge = Challenge.get(challenge_key);
        if not challenge:
            self.error(403)

        self.response.headers['Content-Type'] = 'text/plain'

        # the python compiler doesn't like network line endings
        program = program.replace('\r\n', '\n')

        # add a couple newlines at the end of the program. this makes
        # single-line expressions such as 'class Foo: pass' evaluate happily.
        program += '\n\n'

        #persist the program
        if (users.get_current_user()):
            solution = Solution(author=users.get_current_user())
            solution.content = program
            solution.put()

        # log and compile the program up front
        try:
            logging.info('Compiling and evaluating:\n%s' % program)
            compiled = compile(program, '<string>', 'exec')
        except:
            self.response.out.write(traceback.format_exc())
            return

        # create a dedicated module to be used as this program's __main__
        program_module = new.module('__main__')

        # use this request's __builtin__, since it changes on each request.
        # this is needed for import statements, among other things.
        import __builtin__

        program_module.__builtins__ = __builtin__

        # swap in our custom module for __main__. run the program, swap the custom module out.
        old_main = sys.modules.get('__main__')
        try:
            sys.modules['__main__'] = program_module
            program_module.__name__ = '__main__'

            # run!
            try:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                try:
                    sys.stdout = self.response.out
                    sys.stderr = self.response.out
                    exec compiled in program_module.__dict__

                    for test in challenge.testcases:
                        result = eval(test.statement, program_module.__dict__)
                        if (not str(result) == test.expected):
                            self.response.out.write("FAILED ON TEST CASE " + test.statement + '\n')

                    self.response.out.write("SUCCESS")

                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            except:
                self.response.out.write(traceback.format_exc())
                return

        finally:
            sys.modules['__main__'] = old_main


def main():
    application = webapp.WSGIApplication(
        [('/', FrontPageHandler),
            ('/challenge/', ChallengeHandler),
            ('/challenge/shell.runProgram', ProgramHandler)], debug=_DEBUG)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
