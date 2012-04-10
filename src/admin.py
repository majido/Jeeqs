import os
import string

from google.appengine.dist import use_library
use_library('django', '1.3')

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext.db import djangoforms
from django import forms

from models import *
from jeeqs import authenticate, _DEBUG, add_common_vars

class ChallengeForm(djangoforms.ModelForm):
    class Meta:
        model = Challenge

class ChallengeDjangoFormPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write(unicode('<html><body>'
                                '<form method="POST" '
                                'action="/admin/challenges/new">'
                                '<table>'))
        self.response.out.write(unicode(ChallengeForm()))
        self.response.out.write(unicode('</table>'
                                '<input type="submit">'
                                '</form></body></html>'))

    def post(self):
        data = ChallengeForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=True)
            entity.added_by = users.get_current_user()
            entity.put()
            self.redirect('/admin/challenges')
        else:
            self.response.out.write('<html><body>'
                                    '<form method="POST" '
                                    'action="/">'
                                    '<table>')
            self.response.out.write(data)
            self.response.out.write('</table>'
                                    '<input type="submit">'
                                    '</form></body></html>')

class ChallengePage(webapp.RequestHandler):
    """
    Create a new challenge
    """
    @authenticate(required=True)
    def get(self):
        all_courses = Course.all().fetch(1000)

        vars = add_common_vars({
            'courses': all_courses,
            'jeeqser': self.jeeqser,
            'login_url': users.create_login_url(self.request.url),
            'logout_url': users.create_logout_url(self.request.url)
        })
        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'new_challenge.html')
        rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
        self.response.out.write(rendered)

    @authenticate(required=True)
    def post(self):
        course = Course.get(self.request.get('course'))
        self.response.out.write(course.name)
        number = self.request.get('number')
        name = string.capwords(self.request.get('name'))
        markdown = self.request.get('markdown')
        template_code = self.request.get('template_code')
        source = self.request.get('source')

        exercise = Exercise(number=number, name=name, course=course)
        exercise.put()

        challenge = Challenge(name_persistent=name, markdown=markdown, template_code=template_code, exercise=exercise)
        if source and source != '':
            challenge.source = source

        challenge.put()

        self.redirect('/admin/challenges')


class ChallengeListPage(webapp.RequestHandler):
    def get(self):
        query = Challenge.all().fetch(1000)
        for item in query:
            self.response.out.write('<a href="/admin/challenges/edit?key=%s">Edit</a> ' % item.key())
            number = item.exercise.number if item.exercise else '--'
            self.response.out.write("%s %s <br>" % (number, item.name))

        self.response.out.write('<br/><a href="/admin/challenges/new">New Challenge</a>')

class ChallengeEditPage(webapp.RequestHandler):
    def get(self):
        key = self.request.get('key')
        challenge = Challenge.get(key)
        self.response.out.write(unicode('<html><body>'
                                '<form method="POST" '
                                'action="/admin/challenges/edit">'
                                '<table>'))
        self.response.out.write(unicode(ChallengeForm(instance=challenge)))
        self.response.out.write(unicode('</table>'
                                '<input type="hidden" name="key" value="%s">'
                                '<input type="submit">'
                                '</form></body></html>' % key))

    def post(self):
        key = self.request.get('key')
        challenge = Challenge.get(key)
        data = ChallengeForm(data=self.request.POST, instance=challenge)
        if data.is_valid():
            entity = data.save(commit=True)
            entity.put()
            self.redirect('/admin/challenges')
        else:
            self.response.out.write(unicode('<html><body>'
                                    '<form method="POST" '
                                    'action="/admin/challenges/edit">'
                                    '<table>'))
            self.response.out.write(unicode(data))
            self.response.out.write(unicode('</table>'
                                    '<input type="hidden" name="key" value="%s">'
                                    '<input type="submit">'
                                    '</form></body></html>' % key))
def main():
    application = webapp.WSGIApplication(
        [   ('/admin/challenges/new', ChallengePage),
            ('/admin/challenges/new_django', ChallengeDjangoFormPage),
            ('/admin/challenges', ChallengeListPage),
            ('/admin/challenges/', ChallengeListPage),
            ('/admin/challenges/edit', ChallengeEditPage)
        ],
        debug=True)
    run_wsgi_app(application)

if __name__=="__main__":
    main()