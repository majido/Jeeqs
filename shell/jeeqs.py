#!/usr/bin/python

"""
A program for managing challenges, attempt and solutions.

"""

import logging
import new
import os
import StringIO
import sys
import traceback
import wsgiref.handlers
from google.appengine.ext.db import Key
from model import *

from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext.webapp import template


# Set to True if stack traces should be shown in the browser, etc.
_DEBUG = True

__author__ = 'akhavan'


class FrontPageHandler(webapp.RequestHandler):
    """renders the home.html template
    """

    def get(self):
        # get available challenges

        query = Challenge.all()
        results = query.fetch(20)

        challenges = {}

        for ch in results:
            challenges[ch.name] = str(ch.key())

        logging.info(challenges)

        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'home.html')

        vars = {'challenges': challenges,
                'user': users.get_current_user(),
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url)}

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)


class ChallengeHandler(webapp.RequestHandler):
    """renders the solve_a_challenge.html template
    """

    def get(self):
        # get the challenge
        ch_key = self.request.get('ch')
        if (not ch_key):
            self.error(403)

        challenge = Challenge.get(ch_key)
        if (not challenge):
            self.error(403)

        logging.info("template code is : " + challenge.template_code)

        template_file = os.path.join(os.path.dirname(__file__), 'templates',
            'solve_a_challenge.html')

        # show this user's previous attempts
        attempts = None
        submission = None

        if (users.get_current_user()):
            attempts_query = db.GqlQuery(" SELECT * "
                                   " FROM Attempt "
                                   " WHERE author = :1 "
                                   " AND challenge = :2 "
                                   " ORDER BY date DESC",
                                   users.get_current_user(),
                                   challenge)
            attempts = attempts_query.fetch(20)

            # fetch user's submission
            submission_query = db.GqlQuery(" SELECT * "
                                           " FROM Submission "
                                           " WHERE author = :1 "
                                           " AND challenge = :2 "
                                           " ORDER BY date DESC ",
                                            users.get_current_user(),
                                            challenge)
            submissions = submission_query.fetch(1)

            if (submissions):
                submission = submissions[0]
            else:
                submission = None

        vars = {'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'user': users.get_current_user(),
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'attempts': attempts,
                'challenge_text': challenge.content,
                'challenge_name' : challenge.name,
                'challenge_key' : challenge.key(),
                'template_code': challenge.template_code,
                'submission' : submission
        }
        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class ReviewHandler(webapp.RequestHandler):
    """renders the solve_a_challenge.html template
    """

    def get(self):
        # get the challenge
        ch_key = self.request.get('ch')
        if (not ch_key):
            self.error(403)

        challenge = Challenge.get(ch_key)
        if (not challenge):
            self.error(403)

        # Retrieve other users' submissions
        submissions_query = db.GqlQuery(" SELECT * "
                                        " FROM Submission "
                                        " WHERE challenge = :1 "
                                        " ORDER BY date DESC ",
                                        challenge)
        submissions = submissions_query.fetch(20)

        # TODO: replace this iteration with a data oriented approach
        submissions[:] = [submission for submission in submissions if not submission.author == users.get_current_user()]

        template_file = os.path.join(os.path.dirname(__file__), 'templates',
            'review_a_challenge.html')

        vars = {'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'user': users.get_current_user(),
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'challenge_text': challenge.content,
                'challenge_name' : challenge.name,
                'challenge_key' : challenge.key(),
                'submissions' : submissions
        }

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)


class ProgramHandler(webapp.RequestHandler):
    """Evaluates a python program and returns the result.
    """

    def run_testcases(self, challenge, program_module):
        # Run test cases
        test_num = 0
        for test in challenge.testcases:
            test_num = test_num + 1
            result = eval(test.statement, program_module.__dict__)
            if (not str(result) == test.expected):
                self.response.out.write("FAILED ON TEST CASE " + test.statement + '\n')
        if (test_num == 0):
            self.response.out.write("No test cases to run!")
        else:
            self.response.out.write("SUCCESS")

    def get(self):
        program = self.request.get('program')
        logging.debug('program is ' + program)
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
            attempt = Attempt(author=users.get_current_user(), challenge=challenge, content=program)
            if (self.request.get('is_submission')):
                submission = Submission(author=users.get_current_user(), challenge=challenge, content=program)


        # log and compile the program up front
        try:
            logging.info('Compiling and evaluating:\n%s' % program)
            compiled = compile(program, '<string>', 'exec')
        except:
            self.response.out.write('Compile error:' + traceback.format_exc())
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
                stdout_buffer = StringIO.StringIO()
                stderr_buffer = StringIO.StringIO()
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                try:
                    sys.stdout = stdout_buffer
                    sys.stderr = stderr_buffer
                    exec compiled in program_module.__dict__

                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                    # Write the buffer to response
                    self.response.out.write(stdout_buffer.getvalue())
                    self.response.out.write(stderr_buffer.getvalue())

                    attempt.stdout = stdout_buffer.getvalue()
                    attempt.stderr = stderr_buffer.getvalue()
                    attempt.put()

                    if (self.request.get('is_submission')):
                        submission.stdout = stdout_buffer.getvalue()
                        submission.stderr = stderr_buffer.getvalue()
                        submission.put()

                self.run_testcases(challenge, program_module)


            except:
                self.response.out.write(traceback.format_exc())
                return

        finally:
            sys.modules['__main__'] = old_main

class RPCHandler(webapp.RequestHandler):
    """Handles RPC calls
    """

    def post(self):
        method = self.request.get('method')
        if (not method):
            self.error(403)
        if (method == 'submit_correct'):
            RPCHandler.submit_correct(self)
#        elif (method == 'submit_incorrect'):
#            RPCHandler.submit_incorrect(self)

    def get_jeeqser(self, user):
        jeeqsers = Jeeqser.all().filter('user = ', user).fetch(1)
        if (len(jeeqsers) == 0):
            jeeqser = Jeeqser(user=user, username=user.nickname())
            jeeqser.put()
            return jeeqser
        return jeeqsers[0]


    def submit_correct(self):
        submission_key = self.request.get('submission_key')
        logging.debug('submission key is ' + submission_key)

        # TODO: extract this out
        user = users.get_current_user()
        if (not user):
            self.error(403)
            return

        #TODO: move this to an earlier stage - jeeqser should be available to everyone
        jeeqser = self.get_jeeqser(user)

        submission = Submission.get(submission_key)
        if (not submission):
            self.error(403)
            return

        if (not jeeqser.key() in submission.voted_correct):
            submission.voted_correct.append(jeeqser.key())
            submission.num_correct += 1
            submission.put()

def main():
    application = webapp.WSGIApplication(
        [('/', FrontPageHandler),
            ('/challenge/', ChallengeHandler),
            ('/challenge/shell.runProgram', ProgramHandler),
            ('/review/', ReviewHandler),
            ('/rpc', RPCHandler)], debug=_DEBUG)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
