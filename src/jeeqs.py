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
from models import *

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.dist import use_library

use_library('django', '1.2')

from google.appengine.ext.webapp import template

import lib.markdown as markdown


# Set to True if stack traces should be shown in the browser, etc.
_DEBUG = True


# Gets Jeeqser entity related to the given authenticated user
def get_jeeqser():
    user = users.get_current_user()
    if user is None:
        return None

    jeeqsers = Jeeqser.all().filter('user = ', user).fetch(1)

    if (len(jeeqsers) == 0):
        jeeqser = Jeeqser(user=user, displayname=user.nickname())
        jeeqser.put()
        return jeeqser
    return jeeqsers[0]


class FrontPageHandler(webapp.RequestHandler):
    """renders the home.html template
    """

    def get(self):
        # get available challenges

        all_challenges = Challenge.all().fetch(100)
        challenges = {}

        jeeqser = get_jeeqser()

        for ch in all_challenges:
            submitted = False
            score = 0

            if jeeqser:
                #TODO: inefficient
                submissions = Attempt\
                                    .all()\
                                    .filter("author = ", jeeqser.key())\
                                    .filter("challenge = ", ch)\
                                    .filter('active = ', True)\
                                    .fetch(1)
                if (len(submissions) > 0):
                    submitted = True
                    score = submissions[0].vote_average

            challenges[ch.name] = [str(ch.key()), submitted, round(score, 2)]


        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'home.html')

        vars = {'challenges': challenges,
                'jeeqser': get_jeeqser(),
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url)
        }

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class UserHandler(webapp.RequestHandler):
    """Renders User's profile page"""

    def get(self):
        jeeqser = get_jeeqser()
        if not jeeqser:
            self.redirect("/")

        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'Jeeqser.html')
        vars = {'jeeqser' : jeeqser,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url)
        }

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
        feedbacks = None

        jeeqser = get_jeeqser()

        if (jeeqser):
            attempts_query = db.GqlQuery(" SELECT * "
                                   " FROM Attempt "
                                   " WHERE author = :1 "
                                   " AND challenge = :2 "
                                   " ORDER BY date DESC",
                                   jeeqser.key(),
                                   challenge)
            attempts = attempts_query.fetch(20)

            # fetch user's submission
            submission_query = db.GqlQuery(" SELECT * "
                                           " FROM Attempt  "
                                           " WHERE author = :1 "
                                           " AND challenge = :2 "
                                           " AND active = True "
                                           " ORDER BY date DESC ",
                                            jeeqser.key(),
                                            challenge)
            submissions = submission_query.fetch(1)

            if (submissions):
                submission = submissions[0]

            else:
                submission = None

            if submission:
                feedbacks = Feedback.all()\
                                    .filter('attempt = ', submission)\
                                    .order('-date')\
                                    .fetch(10)

            if feedbacks:
                for feedback in feedbacks:
                    if feedback.vote == 'correct':
                        feedback.icon = 'ui-icon-check'
                        feedback.background = '#EBFFEB'
                    elif feedback.vote == 'incorrect':
                        feedback.icon = 'ui-icon-closethick'
                        feedback.background = '#FFE3E3'
                    else:
                        feedback.icon = 'ui-icon-lightbulb'
                        feedback.background = '#FFFFE6'

        vars = {'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'jeeqser': jeeqser,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'attempts': attempts,
                'challenge' : challenge,
                'challenge_key' : challenge.key(),
                'template_code': challenge.template_code,
                'submission' : submission,
                'feedbacks' : feedbacks
        }
        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class ReviewHandler(webapp.RequestHandler):
    """renders the review template
    """

    def get(self):

        # TODO: extract this out
        user = users.get_current_user()
        if (not user):
            self.redirect('/')
            return

        jeeqser = get_jeeqser()

        # get the challenge
        ch_key = self.request.get('ch')
        if (not ch_key):
            self.error(403)

        challenge = Challenge.get(ch_key)
        if (not challenge):
            self.error(403)

        # Retrieve other users' submissions
        submissions_query = db.GqlQuery(" SELECT * "
                                        " FROM Attempt "
                                        " WHERE challenge = :1 "
                                        " AND active = True "
                                        " ORDER BY vote_count ASC ",
                                        challenge)
        submissions = submissions_query.fetch(10)

        # TODO: replace this iteration with a data oriented approach
        # each .author is one query!! copy the username to the submission entity
        submissions[:] = [submission for submission in submissions if not (submission.author.key() == jeeqser.key() or jeeqser.key() in submission.users_voted)]

        template_file = os.path.join(os.path.dirname(__file__), 'templates',
            'review_a_challenge.html')

        vars = {'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'jeeqser': jeeqser,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'challenge' : challenge,
                'challenge_key' : challenge.key(),
                'submissions' : submissions,
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

        # log and compile the program up front
        try:
            logging.debug('Compiling and evaluating:\n%s' % program)
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
        if method == 'submit_vote':
            self.submit_vote()
        elif method == 'update_displayname':
            self.update_displayname()
        elif method== 'submit_solution':
            self.submit_solution()

    @staticmethod
    def get_vote_numeric_value(vote):
        if vote == 'correct':
            return 2
        elif vote == 'incorrect':
            return 0
        else:
            return 4 # genius

    def submit_solution(self):
        solution = self.request.get('solution')
        if not solution:
            return

        # retrieve the challenge
        challenge_key = self.request.get('challenge_key')
        if not challenge_key:
            self.error(403)
        challenge = Challenge.get(challenge_key);
        jeeqser = get_jeeqser()
        if not challenge or not jeeqser:
            self.error(403)

        attempt = Attempt(
                    author=jeeqser.key(),
                    challenge=challenge,
                    content=markdown.markdown(solution, ['codehilite']),
                    markdown=solution,
                    submitted=True,
                    active=True)

        previous_submissions = Attempt\
            .all()\
            .filter('author = ', get_jeeqser().key())\
            .filter('challenge = ', challenge)\
            .filter('active = ', True)\
            .filter('submitted = ', True)\
            .fetch(10)

        # there should be only one previous submission.
        for previous_submission in previous_submissions:
            previous_submission.active = False
            previous_submission.put()

        attempt.put()

        jeeqser.submissions_num += 1
        jeeqser.put()

    def update_displayname(self):
        displayname = self.request.get('display_name')
        jeeqser = Jeeqser.get(self.request.get('key'))

        if displayname == jeeqser.displayname_persisted:
            return;

        exists = len(Jeeqser.all().filter('displayname_persisted = ', displayname).fetch(1)) > 0
        if not exists:
            jeeqser.displayname = displayname
            jeeqser.put()
        else:
            self.error(403)

    def submit_vote(self):
        submission_key = self.request.get('submission_key')
        logging.debug('submission key is ' + submission_key)

        # TODO: extract this out
        user = users.get_current_user()
        if (not user):
            self.error(403)
            return

        #TODO: move this to an earlier stage - jeeqser should be available to everyone
        jeeqser = get_jeeqser()

        submission = Attempt.get(submission_key)
        if (not submission):
            self.error(403)
            return

        if (not jeeqser.key() in submission.users_voted):
            submission.users_voted.append(jeeqser.key())
            submission.vote_count += 1
            submission.vote_sum += float(RPCHandler.get_vote_numeric_value(self.request.get('vote')))
            submission.vote_average = float(submission.vote_sum / submission.vote_count)
            submission.put()

            feedback = Feedback(
                attempt=submission,
                author=jeeqser,
                attempt_author=submission.author,
                content=self.request.get('response'),
                vote=self.request.get('vote'))
            feedback.put()

            # update stats
            jeeqser.reviews_out_num += 1
            jeeqser.put()

            submission.author.reviews_in_num +=1
            submission.author.put()

def main():
    application = webapp.WSGIApplication(
        [('/', FrontPageHandler),
            ('/challenge/', ChallengeHandler),
            ('/challenge/shell.runProgram', ProgramHandler),
            ('/review/', ReviewHandler),
            ('/rpc', RPCHandler),
            ('/user/', UserHandler)], debug=_DEBUG)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
