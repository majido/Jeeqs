import cgi

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext.db import djangoforms

from models import *

class ChallengeForm(djangoforms.ModelForm):
    class Meta:
        model = Challenge
        exclude = []

class ChallengePage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>'
                                '<form method="POST" '
                                'action="/admin/challenges/new">'
                                '<table>')
        self.response.out.write(ChallengeForm())
        self.response.out.write('</table>'
                                '<input type="submit">'
                                '</form></body></html>')

    def post(self):
        data = ChallengeForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
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

class ChallengeListPage(webapp.RequestHandler):
    def get(self):
        query = db.GqlQuery("SELECT * FROM Challenge ORDER BY name")
        for item in query:
            self.response.out.write('<a href="/admin/challenges/edit?key=%s">Edit</a> ' % item.key())
            self.response.out.write("%s<br>" % (item.name))

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
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/admin/challenges')
        else:
            self.response.out.write('<html><body>'
                                    '<form method="POST" '
                                    'action="/admin/challenges/edit">'
                                    '<table>')
            self.response.out.write(data)
            self.response.out.write('</table>'
                                    '<input type="hidden" name="key" value="%s">'
                                    '<input type="submit">'
                                    '</form></body></html>' % key)
def main():
    application = webapp.WSGIApplication(
        [   ('/admin/challenges/new', ChallengePage),
            ('/admin/challenges', ChallengeListPage),
            ('/admin/challenges/edit', ChallengeEditPage)
        ],
        debug=True)
    run_wsgi_app(application)

if __name__=="__main__":
    main()