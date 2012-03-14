#!/usr/bin/python

"""
A program for managing challenges, attempt and solutions.

"""

from google.appengine.dist import use_library
use_library('django', '1.3')

import logging
import os
import StringIO
import sys
import traceback

import wsgiref.handlers

from models import *

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from google.appengine.api import users
from google.appengine.ext.webapp import template


from google.appengine.ext import webapp

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

def add_common_vars(vars):
    vars['local'] = os.environ['APPLICATION_ID'].startswith('dev~')
    return vars


def authenticate(required=True):
    """ Authenticates the user and sets self.jeeqser to be the user object.
        The handler object (self) is different for each request. so jeeqser should not leak between requests.
        Will return with error if user is not authenticated
    """
    def real_decorator(func):
        def wrapper(self):
            user = users.get_current_user()
            if not user and required:
                self.error(403)
                self.out.response.write('User is not authenticated!')
                return
            elif user:
                self.jeeqser = get_jeeqser()
            else:
                self.jeeqser = None
            func(self)

        return wrapper
    return real_decorator



# Adds icons and background to feedback objects
def prettify_injeeqs(injeeqs):
    for jeeq in injeeqs:
        if jeeq.vote == 'correct':
            jeeq.icon = 'ui-icon-check'
            jeeq.background = '#EBFFEB'
        elif jeeq.vote == 'incorrect':
            jeeq.icon = 'ui-icon-closethick'
            jeeq.background = '#FFE3E3'
        elif jeeq.vote == 'genius':
            jeeq.icon = 'ui-icon-lightbulb'
            jeeq.background = '#FFFFE6'
        elif jeeq.vote == 'flag':
            jeeq.icon = 'ui-icon-flag'
            jeeq.background = 'lightgrey'

class FrontPageHandler(webapp.RequestHandler):
    """renders the home.html template
    """

    @authenticate(False)
    def get(self):
        # get available challenges

        all_challenges = Challenge.all().fetch(100)

        injeeqs = None

        for ch in all_challenges:
            submitted = False
            score = 0

            if self.jeeqser:
                #TODO: inefficient
                submissions = Attempt\
                                    .all()\
                                    .filter("author = ", self.jeeqser)\
                                    .filter("challenge = ", ch)\
                                    .filter('active = ', True)\
                                    .fetch(1)
                if len(submissions) > 0:
                    submission = submissions[0]
                    ch.submitted = True
                    ch.score = round(submission.vote_average, 2)
                    ch.solved = True if (submission.correct_count + submission.genius_count > submission.incorrect_count) else False
                    ch.active_submission = submission

                else:
                    ch.submitted = False
                    ch.score = 0

                injeeqs = Feedback\
                                .all()\
                                .filter('attempt_author = ', self.jeeqser)\
                                .order('flag_count')\
                                .order('-date')\
                                .fetch(10)
                prettify_injeeqs(injeeqs)

        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'home.html')

        vars = add_common_vars({
                'challenges': all_challenges,
                'injeeqs': injeeqs,
                'jeeqser': self.jeeqser,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url)
        })

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class UserHandler(webapp.RequestHandler):
    """Renders User's profile page"""

    @authenticate(False)
    def get(self):
        if not self.jeeqser:
            self.redirect("/")
            return

        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'Jeeqser.html')
        vars = add_common_vars({
            'jeeqser' : self.jeeqser,
                'gravatar_url' : self.jeeqser.gravatar_url,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url)
        })

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class AboutHandler(webapp.RequestHandler):
    """Renders the About page """

    @authenticate(required=False)
    def get(self):
        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'about.html')
        vars = add_common_vars({
                'jeeqser' : self.jeeqser,
                'gravatar_url' : self.jeeqser.gravatar_url if self.jeeqser else None,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url)
        })

        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class ChallengeHandler(webapp.RequestHandler):
    """renders the solve_a_challenge.html template
    """

    @authenticate(False)
    def get(self):
        # show this user's previous attempts
        attempts = None
        feedbacks = None
        submission = None


        # get the challenge
        ch_key = self.request.get('ch')
        if not ch_key:
            self.error(403)
        challenge = Challenge.get(ch_key)
        if not challenge:
            self.error(403)

        if not challenge.content and challenge.markdown:
            challenge.content = markdown.markdown(challenge.markdown, ['codehilite', 'mathjax'])
            challenge.put()

        attempt_key = self.request.get('att')
        if attempt_key:
            submission = Attempt.get(attempt_key)

        template_file = os.path.join(os.path.dirname(__file__), 'templates',
            'solve_a_challenge.html')

        if (self.jeeqser):
            attempts_query = db.GqlQuery(" SELECT * "
                                   " FROM Attempt "
                                   " WHERE author = :1 "
                                   " AND challenge = :2 "
                                   " ORDER BY date DESC",
                                   self.jeeqser.key(),
                                   challenge)
            attempts = attempts_query.fetch(20)

            if not submission:
                # fetch user's active submission
                submission_query = db.GqlQuery(" SELECT * "
                                               " FROM Attempt  "
                                               " WHERE author = :1 "
                                               " AND challenge = :2 "
                                               " AND active = True "
                                               " ORDER BY date DESC ",
                                                self.jeeqser.key(),
                                                challenge)
                submissions = submission_query.fetch(1)

                if (submissions):
                    submission = submissions[0]

                else:
                    submission = None

            if submission:
                feedbacks = Feedback.all()\
                                    .filter('attempt = ', submission)\
                                    .order('flag_count')\
                                    .order('-date')\
                                    .fetch(20)

            if feedbacks:
                prettify_injeeqs(feedbacks)

        vars = add_common_vars({
                'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'jeeqser': self.jeeqser,
                'isadmin' : users.is_current_user_admin(),
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'attempts': attempts,
                'challenge' : challenge,
                'challenge_key' : challenge.key(),
                'template_code': challenge.template_code,
                'submission' : submission,
                'feedbacks' : feedbacks
        })
        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

class ReviewHandler(webapp.RequestHandler):
    """renders the review template
    """

    @authenticate(False)
    def get(self):

        if not self.jeeqser:
            self.redirect('/')
            return

        # get the challenge
        ch_key = self.request.get('ch')
        if not ch_key:
            self.error(403)

        challenge = Challenge.get(ch_key)
        if not challenge:
            self.error(403)

        # Retrieve other users' submissions
        submissions_query = db.GqlQuery(" SELECT * "
                                        " FROM Attempt "
                                        " WHERE challenge = :1 "
                                        " AND active = True "
                                        " AND flagged = False "
                                        " ORDER BY vote_count ASC ",
                                        challenge)
        submissions = submissions_query.fetch(20)

        # TODO: replace this iteration with a data oriented approach
        submissions[:] = [submission for submission in submissions if not (submission.author.key() == self.jeeqser.key() or self.jeeqser.key() in submission.users_voted)]

        template_file = os.path.join(os.path.dirname(__file__), 'templates',
            'review_a_challenge.html')

        vars = add_common_vars({
                'server_software': os.environ['SERVER_SOFTWARE'],
                'python_version': sys.version,
                'jeeqser': self.jeeqser,
                'login_url': users.create_login_url(self.request.url),
                'logout_url': users.create_logout_url(self.request.url),
                'challenge' : challenge,
                'challenge_key' : challenge.key(),
                'submissions' : submissions,
        })

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
            if not str(result) == test.expected:
                self.response.out.write("FAILED ON TEST CASE " + test.statement + '\n')
        if test_num == 0:
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

        # run!
        try:
            stdout_buffer = StringIO.StringIO()
            stderr_buffer = StringIO.StringIO()
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            try:
                sys.stdout = stdout_buffer
                sys.stderr = stderr_buffer
                # This does not allow anything to be done in the sandbox!
                exec compiled in {'__builtins__': {}}, {}

            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

                # Write the buffer to response
                self.response.out.write(stdout_buffer.getvalue())
                self.response.out.write(stderr_buffer.getvalue())

            # to be extended if there are test cases to be run.
            #self.run_testcases(challenge, program_module)

        except:
            self.response.out.write(traceback.format_exc())
            return

class RPCHandler(webapp.RequestHandler):
    """Handles RPC calls
    """

    @authenticate(True)
    def post(self):
        method = self.request.get('method')
        if (not method):
            self.error(403)

        if method == 'submit_vote':
            self.submit_vote()
        elif method == 'update_displayname':
            self.update_displayname()
        elif method == 'submit_solution':
            self.submit_solution()
        elif method == 'flag_feedback':
            self.flag_feedback()
        elif method == 'submit_challenge_source':
            self.submit_challenge_source()
        else:
            self.error(403)

    @staticmethod
    def get_vote_numeric_value(vote):
        if vote == 'correct':
            return 2
        elif vote == 'incorrect':
            return 0
        elif vote == 'genius':
            return 4
        else:
            return 0 # flag

    @staticmethod
    def updateSubmission(submission, vote, voter):
        if vote == 'correct':
            submission.correct_count += 1
        elif vote == 'incorrect':
            submission.incorrect_count += 1
        elif vote == 'genius':
            submission.genius_count += 1
        elif vote == 'flag':
            submission.flag_count += 1
            if submission.flag_count > 2:
                submission.flagged = True
            submission.flagged_by.append(voter.key())

    def submit_challenge_source(self):
        """updates a challenge's source """
        if not users.is_current_user_admin():
            self.error(403)
            return

        new_source = self.request.get('source')
        if not new_source:
            self.error(403)
            return

        # retrieve the challenge
        challenge_key = self.request.get('challenge_key')
        if not challenge_key:
            self.error(403)
            return
        challenge = Challenge.get(challenge_key);

        if not challenge:
            self.error(403)
            return

        challenge.markdown = new_source
        challenge.content = markdown.markdown(challenge.markdown, ['codehilite', 'mathjax'])
        challenge.put()

    def submit_solution(self):
        """
        Submits a solution
        """
        solution = self.request.get('solution')
        if not solution:
            return

        # retrieve the challenge
        challenge_key = self.request.get('challenge_key')
        if not challenge_key:
            self.error(403)
            return
        challenge = Challenge.get(challenge_key);

        if not challenge:
            self.error(403)
            return

        attempt = Attempt(
                    author=self.jeeqser.key(),
                    challenge=challenge,
                    content=markdown.markdown(solution, ['codehilite', 'mathjax']),
                    markdown=solution,
                    submitted=True,
                    active=True)

        previous_submissions = Attempt\
            .all()\
            .filter('author = ', self.jeeqser.key())\
            .filter('challenge = ', challenge)\
            .filter('active = ', True)\
            .filter('submitted = ', True)\
            .fetch(10)

        max_old_index = 0
        # there should be only one previous submission.
        for previous_submission in previous_submissions:
            previous_submission.active = False
            max_old_index = max(max_old_index, previous_submission.index)
            previous_submission.put()

        attempt.index = max_old_index + 1
        attempt.put()

        self.jeeqser.submissions_num += 1
        self.jeeqser.put()

    def update_displayname(self):
        displayname = self.request.get('display_name')

        if displayname == self.jeeqser.displayname_persisted:
            return;

        exists = len(Jeeqser.all().filter('displayname_persisted = ', displayname).fetch(1)) > 0
        if not exists:
            self.jeeqser.displayname = displayname
            self.jeeqser.put()
        else:
            self.error(403)

    def submit_vote(self):
        submission_key = self.request.get('submission_key')

        submission = Attempt.get(submission_key)
        if (not submission):
            self.error(403)
            return

        if (not self.jeeqser.key() in submission.users_voted):
            submission.users_voted.append(self.jeeqser.key())
            submission.vote_count += 1
            vote = self.request.get('vote')

            submission.vote_sum += float(RPCHandler.get_vote_numeric_value(vote))
            submission.vote_average = float(submission.vote_sum / submission.vote_count)
            RPCHandler.updateSubmission(submission, vote, self.jeeqser)
            submission.put()

            feedback = Feedback(
                attempt=submission,
                author=self.jeeqser,
                attempt_author=submission.author,
                content=self.request.get('response'),
                vote=vote)
            feedback.put()

            # update stats
            self.jeeqser.reviews_out_num += 1
            self.jeeqser.put()

            submission.author.reviews_in_num +=1
            submission.author.put()

    def flag_feedback(self):
        feedback_key = self.request.get('feedback_key')

        feedback = Feedback.get(feedback_key)

        if (self.jeeqser.key() not in feedback.flagged_by):
            feedback.flagged_by.append(self.jeeqser.key())
            feedback.flag_count += 1
            feedback.put()


def main():
    application = webapp.WSGIApplication(
        [('/', FrontPageHandler),
            ('/challenge/', ChallengeHandler),
            ('/challenge/shell.runProgram', ProgramHandler),
            ('/review/', ReviewHandler),
            ('/rpc', RPCHandler),
            ('/user/', UserHandler),
            ('/about/', AboutHandler)], debug=_DEBUG)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
