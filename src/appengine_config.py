from google.appengine.dist import use_library
use_library('django', '1.3')

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app